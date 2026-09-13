import asyncio
import websockets

from config import HTTP_LISTEN_HOST, HTTP_LISTEN_PORT, READ_CHUNK_SIZE, WS_LISTEN_HOST, WS_LISTEN_PORT, WS_PING_INTERVAL

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

            if cmd == 1:
                writer.write(payload)
                await writer.drain()
            elif cmd == 2:
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
            data = await reader.read(READ_CHUNK_SIZE)
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
    tcp_server = await asyncio.start_server(handle_visitor, HTTP_LISTEN_HOST, HTTP_LISTEN_PORT)
    ws_server = await websockets.serve(ws_handler, WS_LISTEN_HOST, WS_LISTEN_PORT, ping_interval=WS_PING_INTERVAL)
    print(f"[*] App listening on {HTTP_LISTEN_HOST}:{HTTP_LISTEN_PORT}")
    print(f"[*] WebSocket Agent listening on {WS_LISTEN_HOST}:{WS_LISTEN_PORT}")
    async with tcp_server, ws_server:
        await asyncio.gather(tcp_server.serve_forever(), ws_server.wait_closed())


if __name__ == '__main__':
    asyncio.run(main())
