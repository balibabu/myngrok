import asyncio
import websockets

# URL of your agent subdomain through your open proxy port
SERVER_WS_URL = "wss://tunnel-agent.rajababu.duckdns.org:4343"
LOCAL_APP_PORT = 8000  # The port your local app runs on

local_conns = {}

async def pipe_local_to_ws(conn_id, reader, ws):
    conn_bytes = conn_id.to_bytes(4, 'big')
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            await ws.send(b'\x01' + conn_bytes + data)
    except Exception:
        pass
    finally:
        try:
            await ws.send(b'\x02' + conn_bytes)
        except Exception:
            pass
        local_conns.pop(conn_id, None)

async def main():
    while True:
        try:
            print(f"Connecting to {SERVER_WS_URL}...")
            async with websockets.connect(SERVER_WS_URL, ping_interval=20) as ws:
                print(f"[+] Tunnel open! Forwarding traffic to localhost:{LOCAL_APP_PORT}")
                async for msg in ws:
                    if not isinstance(msg, bytes) or len(msg) < 5:
                        continue
                    cmd = msg[0]
                    conn_id = int.from_bytes(msg[1:5], 'big')
                    payload = msg[5:]

                    if cmd == 1:  # DATA
                        if conn_id not in local_conns:
                            try:
                                r, w = await asyncio.open_connection('127.0.0.1', LOCAL_APP_PORT)
                                local_conns[conn_id] = (r, w)
                                asyncio.create_task(pipe_local_to_ws(conn_id, r, ws))
                            except Exception as e:
                                print(f"Could not connect to local app: {e}")
                                continue

                        _, writer = local_conns[conn_id]
                        writer.write(payload)
                        await writer.drain()

                    elif cmd == 2:  # CLOSE
                        pair = local_conns.pop(conn_id, None)
                        if pair:
                            pair[1].close()

        except Exception as e:
            print(f"Connection error: {e}. Retrying in 3 seconds...")
            await asyncio.sleep(3)

if __name__ == '__main__':
    asyncio.run(main())