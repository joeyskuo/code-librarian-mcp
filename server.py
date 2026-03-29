from fastmcp import FastMCP
from fastmcp.server.auth.auth import AccessToken, TokenVerifier

from config import settings
from tools.code_librarian import register_tools


class StaticTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if token == settings.mcp_secret_token:
            return AccessToken(token=token, client_id="client", scopes=[])
        return None


mcp = FastMCP("code-librarian-mcp", auth=StaticTokenVerifier())
register_tools(mcp)
