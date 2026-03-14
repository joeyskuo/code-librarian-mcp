import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
