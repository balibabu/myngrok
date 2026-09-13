import os

from dotenv import load_dotenv

load_dotenv()

SERVER_WS_URL = os.getenv("SERVER_WS_URL", "wss://tunnel-agent.rajababu.duckdns.org:4343")
LOCAL_APP_HOST = os.getenv("LOCAL_APP_HOST", "127.0.0.1")
LOCAL_APP_PORT = int(os.getenv("LOCAL_APP_PORT", "8000"))
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "3"))
WS_PING_INTERVAL = int(os.getenv("WS_PING_INTERVAL", "20"))
READ_CHUNK_SIZE = int(os.getenv("READ_CHUNK_SIZE", "65536"))

HTTP_LISTEN_HOST = os.getenv("HTTP_LISTEN_HOST", "127.0.0.1")
HTTP_LISTEN_PORT = int(os.getenv("HTTP_LISTEN_PORT", "5000"))
WS_LISTEN_HOST = os.getenv("WS_LISTEN_HOST", "127.0.0.1")
WS_LISTEN_PORT = int(os.getenv("WS_LISTEN_PORT", "9000"))
