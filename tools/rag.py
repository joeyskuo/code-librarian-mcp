import os
from fastmcp import FastMCP
from services.rag_client import RagClient


def register_tools(mcp: FastMCP):
    client = RagClient(base_url=os.environ["RAG_BASE_URL"])

    @mcp.tool()
    def find_similar(query: str) -> list[dict]:
        """Find semantically similar code snippets from the library"""
        results = client.find_similar(query)
        return [vars(r) for r in results]
