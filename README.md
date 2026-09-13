# myngrok

A minimal ngrok-style TCP tunnel over WebSockets. A server running on a public machine accepts visitor connections and forwards them through a WebSocket tunnel to a client running next to your local app.

## Architecture

- **server.py** — runs on the public server. Listens for visitors (TCP) and for the tunnel client (WebSocket), and pipes bytes between them.
- **client.py** — runs on your local machine. Connects to the server's WebSocket endpoint and forwards tunnel traffic to your local app.

## Prerequisites

- [Python](https://www.python.org/) 3.9+
- [uv](https://docs.astral.sh/uv/) package manager

## Setup

1. Clone the repo and enter the directory:

   ```bash
   git clone <your-repo-url>
   cd myngrok
   ```

2. Install dependencies and create the virtual environment:

   ```bash
   uv sync
   ```

3. Create your env file from the example:

   ```bash
   cp .env.example .env
   ```

4. Edit `.env` to match your setup. Set a strong `AUTH_TOKEN` (generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"`) and use the same value in the `.env` on both the server and client machines.

## Configuration

All settings live in `.env` (loaded via `config.py`):

| Variable | Used by | Default | Description |
|---|---|---|---|
| `AUTH_TOKEN` | both | — | Shared secret the client sends to authenticate with the server (required; both sides must match) |
| `SERVER_WS_URL` | client | `wss://tunnel-agent.rajababu.duckdns.org:4343` | WebSocket URL of the server's agent endpoint |
| `LOCAL_APP_HOST` | client | `127.0.0.1` | Host of the local app to forward traffic to |
| `LOCAL_APP_PORT` | client | `8000` | Port of the local app |
| `RECONNECT_DELAY` | client | `3` | Seconds to wait before retrying a dropped tunnel |
| `WS_PING_INTERVAL` | both | `20` | WebSocket ping interval in seconds |
| `READ_CHUNK_SIZE` | both | `65536` | TCP read chunk size in bytes |
| `HTTP_LISTEN_HOST` | server | `127.0.0.1` | Host the visitor-facing TCP server binds to |
| `HTTP_LISTEN_PORT` | server | `5000` | Port for visitor traffic (e.g. behind an Nginx/caddy proxy for your domain) |
| `WS_LISTEN_HOST` | server | `127.0.0.1` | Host the WebSocket agent server binds to |
| `WS_LISTEN_PORT` | server | `9000` | Port the tunnel client connects to (e.g. proxied to `wss://tunnel-agent...`) |

## Running

### Start the server (public machine)

```bash
uv run server.py
```

### Start the client (local machine, next to your app)

```bash
uv run client.py
```

Make sure your local app is running on `LOCAL_APP_HOST:LOCAL_APP_PORT` first. Visitors hitting the server's public endpoint will now reach your local app.

### Without uv

```bash
python -m venv .venv
source .venv/bin/activate
pip install websockets python-dotenv
python server.py
python client.py
```
