import httpx
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeMatch:
    filename: str
    file_path: str
    file_url: str
    content: str
    similarity: float


class CodeLibrarianClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def find_similar(self, query: str) -> list[CodeMatch]:
        response = httpx.post(f"{self.base_url}/test-embed-query", json={"query": query})
        response.raise_for_status()
        data = response.json()
        logger.info("find_similar response: %s", data)
        return [CodeMatch(**item) for item in data]
