import re
import json
import httpx
import logging
from typing import AsyncGenerator

from services.models import RepoQueryResult, RepoStatus, EmbedFileEvent, EmbedResult, RepoCodeSize

logger = logging.getLogger(__name__)


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
        response = await self._http.post("/repos/query", json={"query": query, "repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("query_repo response: %s", data)
        return [RepoQueryResult(**item) for item in data]

    async def check_repository_status(self, repo_url: str) -> RepoStatus:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.get("/repos/status", params={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("check_repository_status response: %s", data)
        return RepoStatus(**data)

    async def embed_repository(self, repo_url: str) -> AsyncGenerator[EmbedFileEvent | EmbedResult, None]:
        repo_url = self._normalize_github_url(repo_url)
        async with self._http.stream("POST", "/repos/embed", json={"repo_url": repo_url}, timeout=180.0) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                event = json.loads(line)
                if event["type"] == "file":
                    yield EmbedFileEvent(path=event["path"], index=event["index"], total=event["total"])
                elif event["type"] == "done":
                    logger.info("embed_repository done: %s", event)
                    yield EmbedResult(repo=event["repo"], status=event["status"], files=event["files"])

    async def get_file_tree(self, repo_url: str) -> dict:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.get("/repos/file-tree", params={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("get_file_tree response: %s", data)
        return data

    async def get_code_size(self, repo_url: str) -> RepoCodeSize:
        repo_url = self._normalize_github_url(repo_url)
        response = await self._http.get("/repos/code-size", params={"repo_url": repo_url})
        response.raise_for_status()
        data = response.json()
        logger.info("get_code_size response: %s", data)
        return RepoCodeSize(**data)

    def _normalize_github_url(self, url: str) -> str:
        match = re.search(r"github\.com/([^/]+/[^/]+)", url)
        if not match:
            raise ValueError(f"Invalid GitHub repo URL: {url!r}. Expected format: https://github.com/owner/repo")
        return f"https://github.com/{match.group(1)}"
