from dataclasses import dataclass


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
class EmbedFileEvent:
    path: str
    index: int
    total: int


@dataclass
class EmbedResult:
    repo: str
    status: str
    files: int


@dataclass
class RepoCodeSize:
    repo: str
    file_count: int
    total_bytes: int
