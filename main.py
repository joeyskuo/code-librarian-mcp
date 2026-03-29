import logging
logging.basicConfig(level=logging.INFO)

from config import settings
from services.telemetry import setup_telemetry
setup_telemetry()

from server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=settings.host, port=settings.port)
