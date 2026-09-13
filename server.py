import asyncio
import websockets

HTTP_PORT = 5000   # For tunnel-app.rajababu.duckdns.org
WS_PORT = 9000     # For tunnel-agent.rajababu.duckdns.org

agent_ws = None
active_conns = {}
next_conn_id = 1

async def ws_handler(websocket, *args):
    global agent_ws
    print("[+] Local PC connected via WebSocket tunnel!")
    agent_ws = websocket
    try:
        async for msg in websocket:
            if not isinstance(msg, bytes) or len(msg) < 5:
                continue
            cmd = msg[0]
            conn_id = int.from_bytes(msg[1:5], 'big')
            payload = msg[5:]

            writer = active_conns.get(conn_id)
            if not writer:
                continue

            if cmd == 1:  # DATA
                writer.write(payload)
                await writer.drain()
            elif cmd == 2:  # CLOSE
                writer.close()
                active_conns.pop(conn_id, None)
    except Exception as e:
        print(f"[-] Local PC disconnected: {e}")
    finally:
        agent_ws = None

async def handle_visitor(reader, writer):
    global next_conn_id
    if not agent_ws:
        writer.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 25\r\n\r\nTunnel agent not online.")
        await writer.drain()
        writer.close()
        return

    conn_id = next_conn_id
    next_conn_id = (next_conn_id + 1) % 0xFFFFFFFF
    active_conns[conn_id] = writer
    conn_bytes = conn_id.to_bytes(4, 'big')

    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            await agent_ws.send(b'\x01' + conn_bytes + data)
    except Exception:
        pass
    finally:
        if agent_ws:
            try:
                await agent_ws.send(b'\x02' + conn_bytes)
            except Exception:
                pass
        active_conns.pop(conn_id, None)
        writer.close()

async def main():
    tcp_server = await asyncio.start_server(handle_visitor, '127.0.0.1', HTTP_PORT)
    ws_server = await websockets.serve(ws_handler, '127.0.0.1', WS_PORT, ping_interval=20)
    print(f"[*] (NEW) App listening on 127.0.0.1:{HTTP_PORT}")
    print(f"[*] (NEW) WebSocket Agent listening on 127.0.0.1:{WS_PORT}")
    async with tcp_server, ws_server:
        await asyncio.gather(tcp_server.serve_forever(), ws_server.wait_closed())

if __name__ == '__main__':
    asyncio.run(main())