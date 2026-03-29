import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from services.telemetry import setup_telemetry
setup_telemetry()

from server import mcp

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8001))
    mcp.run(transport="streamable-http", host=host, port=port)
