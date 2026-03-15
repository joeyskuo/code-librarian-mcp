import os
from fastmcp import FastMCP
from services.code_librarian_service import CodeLibrarianClient


def register_tools(mcp: FastMCP):
    client = CodeLibrarianClient(base_url=os.environ["RAG_BASE_URL"])

    @mcp.tool()
    def find_relevant_code(query: str) -> list[dict]:
        """Search the codebase to find code relevant to answering a question about a repository.

        Use this to retrieve context from the codebase when answering questions about how
        something works, where logic lives, what a piece of code does, or what technologies
        and frameworks are used. Query with natural language describing what you're trying
        to understand.

        Returns a list of matches, each with: filename, file_path, file_url, content, similarity (0-1).
        """
        results = client.find_similar(query)
        return [vars(r) for r in results]
