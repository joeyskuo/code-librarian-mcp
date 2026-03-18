import os
from fastmcp import FastMCP
from services.code_librarian_service import CodeLibrarianClient


def register_tools(mcp: FastMCP):
    client = CodeLibrarianClient(base_url=os.environ["CL_API_URL"], api_key=os.environ["CL_API_KEY"])

    @mcp.tool()
    async def query_repository_code(query: str, repo_url: str) -> list[dict]:
        """Search the codebase to find code relevant to answering a question about a repository.

        Use this to retrieve context from the codebase when answering questions about how
        something works, where logic lives, what a piece of code does, or what technologies
        and frameworks are used. Query with natural language describing what you're trying
        to understand.

        repo_url must be a GitHub repository URL (e.g. https://github.com/owner/repo).

        Returns a list of matches, each with: filename, file_path, file_url, content, similarity (0-1).
        """
        results = await client.query_repo(query, repo_url)
        return [vars(r) for r in results]

    @mcp.tool()
    async def check_repository_status(repo_url: str) -> dict:
        """Check if a repository has embeddings, so that it is able to be queried.

        Use this before querying a repository to confirm it has been embedded.
        If embeddings is 0, the repository must be embedded first using embed_repository.

        repo_url must be a GitHub repository URL (e.g. https://github.com/owner/repo).

        Returns: repo (str), embeddings (int).
        """
        return vars(await client.check_repository_status(repo_url))

    @mcp.tool()
    async def embed_repository(repo_url: str) -> dict:
        """Embed a GitHub repository so it can be queried.

        Initiates the embedding process for all code files in the repository.
        Run this if check_repository_status shows 0 embeddings.

        repo_url must be a GitHub repository URL (e.g. https://github.com/owner/repo).

        Returns: repo (str), files_found (int), stored (int), skipped (int).
        """
        return vars(await client.embed_repository(repo_url))

    @mcp.tool()
    async def get_repository_file_tree(repo_url: str) -> dict:
        """Get a flattened list of code-related files in a repository.

        Use this to quickly understand the structure of a repository without
        fetching file contents. Lighter than a full embed or query.

        repo_url must be a GitHub repository URL (e.g. https://github.com/owner/repo).

        Returns: repo (str), truncated (bool), files (list of file paths).
        """
        return await client.get_file_tree(repo_url)

    @mcp.tool()
    async def get_repository_code_size(repo_url: str) -> dict:
        """Get the code size of a repository: file count and total bytes.

        Use this only if check_repository_status shows 0 embeddings and you need
        to decide whether to proceed with embedding — e.g. if the repo has too
        many files or exceeds an allowed file size total.

        repo_url must be a GitHub repository URL (e.g. https://github.com/owner/repo).

        Returns: repo (str), file_count (int), total_bytes (int).
        """
        return vars(await client.get_code_size(repo_url))
