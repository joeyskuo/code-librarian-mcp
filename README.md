# code-librarian-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes code embeddding and vector search operations as tools for AI assistants. Built with [FastMCP](https://github.com/jlowin/fastmcp), targets the Claude API via streamable-http transport.

## What it does

Connects an AI assistant (Claude) to a tool server so it can answer contextual questions about GitHub repositories. The assistant can embed the code files in a repo, perform a vector search with an embedded query, and generate a response using the top results of the semantic search.

## Tools exposed

| Tool | Description |
|---|---|
| `query_repository_code` | Semantic search over embedded code; returns matching snippets with file path, URL, similarity score, and line range |
| `check_repository_status` | Check whether a repo has been embedded and is queryable |
| `embed_repository` | Trigger embedding for a GitHub repo; streams file-by-file progress |
| `get_repository_file_tree` | List all code files in a repo without fetching content |
| `get_repository_code_size` | Get file count and total byte size; used to determine whether the repo is within embedding limits |

## Architecture

```
Claude API
    │  MCP
    ▼
code-librarian-mcp          ← this repo
    │  HTTP
    ▼
Tool server      ← embedding and repo-operations service
```

- `main.py`: entrypoint; loads env, configures OpenTelemetry (must run before FastMCP import), starts server
- `server.py`: FastMCP app instance with static token auth
- `tools/code_librarian.py`: MCP tool definitions; thin wrappers that delegate to the service client
- `services/code_librarian_service.py`: async HTTP client (`httpx`) wrapping the RAG API
- `services/models.py`: shared dataclasses (`RepoQueryResult`, `EmbedResult`, etc.)

## Tech stack

- **Python 3.11+**
- **FastMCP**: MCP server framework
- **httpx**: async HTTP client with connection pooling
- **OpenTelemetry**: distributed tracing, exported to Langfuse via OTLP

## Setup

```bash
pip install -e .
```

`.env` file required:

```
CL_API_URL=http://localhost:8000
CL_API_KEY=...
MCP_SECRET_TOKEN=your-mcp-token
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_BASE_URL=...
```

## Running

```bash
python main.py
```

Server starts on `0.0.0.0:8001` by default. Override with `HOST` and `PORT` env vars.
