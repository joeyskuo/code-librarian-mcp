import re
import httpx
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RepoQueryResult:
    filename: str
    file_path: str
    file_url: str
    content: str
    similarity: float
    start_line: int
    end_line: int


@dataclass
class RepoStatus:
    repo: str
    embeddings: int


@dataclass
class EmbedResult:
    repo: str
    files_found: int
    stored: int
    skipped: int


@dataclass
class RepoCodeSize:
    repo: str
    file_count: int
    total_bytes: int


class CodeLibrarianClient:
    def __init__(self, base_url: str, api_key: str):
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"X-API-KEY": api_key},
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            timeout=60.0,
        )

    async def query_repo(self, query: str, repo_url: str) -> list[RepoQueryResult]:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.post("/query-repo", json={"query": query, "repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("query_repo response: %s", data)
        return [RepoQueryResult(**item) for item in data]

    async def check_repository_status(self, repo_url: str) -> RepoStatus:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.get("/repo-status", params={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("check_repository_status response: %s", data)
        return RepoStatus(**data)

    async def embed_repository(self, repo_url: str) -> EmbedResult:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.post("/embed-repo", json={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("embed_repository response: %s", data)
        return EmbedResult(**data)

    async def get_file_tree(self, repo_url: str) -> dict:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.get("/repo-file-tree", params={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("get_file_tree response: %s", data)
        return data

    async def get_code_size(self, repo_url: str) -> RepoCodeSize:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.get("/repo-code-size", params={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("get_code_size response: %s", data)
        return RepoCodeSize(**data)

    def _normalize_github_url(self, url: str) -> str:
        match = re.search(r"github\.com/([^/]+/[^/]+)", url)
        if not match:
            raise ValueError(f"Invalid GitHub repo URL: {url!r}. Expected format: https://github.com/owner/repo")
        return f"https://github.com/{match.group(1)}"
