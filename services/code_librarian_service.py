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


class CodeLibrarianClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def query_repo(self, query: str, repo_url: str) -> list[RepoQueryResult]:
        repo_url = self._normalize_github_url(repo_url)
        response = httpx.post(f"{self.base_url}/query-repo", json={"query": query, "repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("query_repo response: %s", data)
        return [RepoQueryResult(**item) for item in data]

    def check_repository_status(self, repo_url: str) -> RepoStatus:
        repo_url = self._normalize_github_url(repo_url)
        response = httpx.post(f"{self.base_url}/repo-status", json={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("check_repository_status response: %s", data)
        return RepoStatus(**data)

    def embed_repository(self, repo_url: str) -> EmbedResult:
        repo_url = self._normalize_github_url(repo_url)
        response = httpx.post(f"{self.base_url}/embed-repo", json={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("embed_repository response: %s", data)
        return EmbedResult(**data)

    def _normalize_github_url(self, url: str) -> str:
        import re
        match = re.search(r"github\.com/([^/]+/[^/]+)", url)
        if not match:
            raise ValueError(f"Invalid GitHub repo URL: {url!r}. Expected format: https://github.com/owner/repo")
        return f"https://github.com/{match.group(1)}"
