import pytest
from services.code_librarian_service import CodeLibrarianClient


def make_client():
    return CodeLibrarianClient.__new__(CodeLibrarianClient)


@pytest.mark.parametrize("url,expected", [
    ("https://github.com/owner/repo", "https://github.com/owner/repo"),
    ("https://github.com/owner/repo/", "https://github.com/owner/repo"),
    ("https://github.com/owner/repo/tree/main/src", "https://github.com/owner/repo"),
    ("http://github.com/owner/repo", "https://github.com/owner/repo"),
    ("github.com/owner/repo", "https://github.com/owner/repo"),
])
def test_normalize_valid_urls(url, expected):
    client = make_client()
    assert client._normalize_github_url(url) == expected


@pytest.mark.parametrize("url", [
    "https://gitlab.com/owner/repo",
    "not-a-url",
    "https://example.com",
    "",
])
def test_normalize_invalid_urls_raise(url):
    client = make_client()
    with pytest.raises(ValueError, match="Invalid GitHub repo URL"):
        client._normalize_github_url(url)
