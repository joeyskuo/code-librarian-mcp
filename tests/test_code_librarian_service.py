import json
import pytest
import httpx
import respx

from services.code_librarian_service import CodeLibrarianClient
from services.models import RepoQueryResult, RepoStatus, EmbedFileEvent, EmbedResult, RepoCodeSize

BASE_URL = "http://test-api"
API_KEY = "test-key"


@pytest.fixture
def client():
    return CodeLibrarianClient(base_url=BASE_URL, api_key=API_KEY)


@respx.mock
@pytest.mark.asyncio
async def test_query_repo_returns_results(client):
    payload = [
        {
            "filename": "main.py",
            "file_path": "src/main.py",
            "file_url": "https://github.com/owner/repo/blob/main/src/main.py",
            "content": "def hello(): pass",
            "similarity": 0.95,
            "start_line": 1,
            "end_line": 1,
        }
    ]
    respx.post(f"{BASE_URL}/repos/query").mock(return_value=httpx.Response(200, json=payload))

    results = await client.query_repo("hello function", "https://github.com/owner/repo")

    assert len(results) == 1
    assert isinstance(results[0], RepoQueryResult)
    assert results[0].filename == "main.py"
    assert results[0].similarity == 0.95


@respx.mock
@pytest.mark.asyncio
async def test_query_repo_raises_on_http_error(client):
    respx.post(f"{BASE_URL}/repos/query").mock(return_value=httpx.Response(500))

    with pytest.raises(httpx.HTTPStatusError):
        await client.query_repo("hello", "https://github.com/owner/repo")


@respx.mock
@pytest.mark.asyncio
async def test_check_repository_status(client):
    payload = {"repo": "https://github.com/owner/repo", "embeddings": 42}
    respx.get(f"{BASE_URL}/repos/status").mock(return_value=httpx.Response(200, json=payload))

    result = await client.check_repository_status("https://github.com/owner/repo")

    assert isinstance(result, RepoStatus)
    assert result.embeddings == 42


@respx.mock
@pytest.mark.asyncio
async def test_get_code_size(client):
    payload = {"repo": "https://github.com/owner/repo", "file_count": 10, "total_bytes": 50000}
    respx.get(f"{BASE_URL}/repos/code-size").mock(return_value=httpx.Response(200, json=payload))

    result = await client.get_code_size("https://github.com/owner/repo")

    assert isinstance(result, RepoCodeSize)
    assert result.file_count == 10
    assert result.total_bytes == 50000


@respx.mock
@pytest.mark.asyncio
async def test_get_file_tree(client):
    payload = {"repo": "https://github.com/owner/repo", "truncated": False, "files": ["src/main.py", "README.md"]}
    respx.get(f"{BASE_URL}/repos/file-tree").mock(return_value=httpx.Response(200, json=payload))

    result = await client.get_file_tree("https://github.com/owner/repo")

    assert result["truncated"] is False
    assert "src/main.py" in result["files"]


@respx.mock
@pytest.mark.asyncio
async def test_embed_repository_yields_events_and_result(client):
    lines = [
        json.dumps({"type": "file", "path": "src/main.py", "index": 1, "total": 2}),
        json.dumps({"type": "file", "path": "src/utils.py", "index": 2, "total": 2}),
        json.dumps({"type": "done", "repo": "https://github.com/owner/repo", "status": "ok", "files": 2}),
    ]
    body = "\n".join(lines) + "\n"
    respx.post(f"{BASE_URL}/repos/embed").mock(return_value=httpx.Response(200, text=body))

    events = []
    async for event in client.embed_repository("https://github.com/owner/repo"):
        events.append(event)

    assert len(events) == 3
    assert isinstance(events[0], EmbedFileEvent)
    assert events[0].path == "src/main.py"
    assert isinstance(events[2], EmbedResult)
    assert events[2].files == 2


@respx.mock
@pytest.mark.asyncio
async def test_query_repo_normalizes_url(client):
    payload = []
    route = respx.post(f"{BASE_URL}/repos/query").mock(return_value=httpx.Response(200, json=payload))

    await client.query_repo("test", "https://github.com/owner/repo/tree/main/src")

    request_body = json.loads(route.calls[0].request.content)
    assert request_body["repo_url"] == "https://github.com/owner/repo"
