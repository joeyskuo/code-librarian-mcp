from fastmcp import FastMCP
from tools.code_librarian import register_tools

mcp = FastMCP("code-librarian-mcp")
register_tools(mcp)
