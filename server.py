from fastmcp import FastMCP
from tools.rag import register_tools

mcp = FastMCP("code-librarian-mcp")
register_tools(mcp)
