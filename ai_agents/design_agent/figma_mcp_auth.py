import asyncio
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from mcp.client.auth import OAuthClientProvider
from mcp.shared.auth import (
    AuthorizationCodeResult,
    OAuthClientInformationFull,
    OAuthClientMetadata,
    OAuthToken,
)

from config.settings import settings

# Loopback redirect used for the one-time interactive OAuth login
# (see scripts/figma_mcp_login.py). Must match what's registered with Figma's
# MCP server via Dynamic Client Registration -- keeping it fixed avoids
# re-registering a new client on every login.
REDIRECT_HOST = "127.0.0.1"
REDIRECT_PORT = 8945
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"


class FileTokenStorage:
    """Persists OAuth tokens + registered client info to a local JSON file.

    Implements mcp.client.auth.TokenStorage (get/set tokens + client_info).
    """

    def __init__(self, path: str):
        self._path = Path(path)

    def _read(self) -> dict:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text())

    def _write(self, data: dict) -> None:
        self._path.write_text(json.dumps(data, indent=2))

    async def get_tokens(self) -> OAuthToken | None:
        data = self._read()
        if "tokens" not in data:
            return None
        return OAuthToken.model_validate(data["tokens"])

    async def set_tokens(self, tokens: OAuthToken) -> None:
        data = self._read()
        data["tokens"] = tokens.model_dump(mode="json")
        self._write(data)

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        data = self._read()
        if "client_info" not in data:
            return None
        return OAuthClientInformationFull.model_validate(data["client_info"])

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        data = self._read()
        data["client_info"] = client_info.model_dump(mode="json")
        self._write(data)


class _CallbackServer:
    """One-shot local HTTP server that captures the OAuth redirect's code/state."""

    def __init__(self):
        self.result: AuthorizationCodeResult | None = None
        self.error: str | None = None

    def handle_once(self) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                params = parse_qs(urlparse(self.path).query)

                if "error" in params:
                    outer.error = params["error"][0]
                    body = f"Authorization failed: {outer.error}. You can close this window."
                else:
                    code = params.get("code", [None])[0]
                    state = params.get("state", [None])[0]
                    outer.result = AuthorizationCodeResult(code=code, state=state)
                    body = "Figma authorization complete. You can close this window."

                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(body.encode())

            def log_message(self, format, *args):
                return  # silence default request logging

        server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), Handler)
        server.handle_request()
        server.server_close()


async def _redirect_handler(authorization_url: str) -> None:
    print("\nOpen this URL in your browser to authorize the agent with Figma:\n")
    print(authorization_url)
    print()
    webbrowser.open(authorization_url)


async def _callback_handler() -> AuthorizationCodeResult:
    callback_server = _CallbackServer()
    await asyncio.to_thread(callback_server.handle_once)

    if callback_server.error:
        raise RuntimeError(f"Figma authorization failed: {callback_server.error}")

    if callback_server.result is None:
        raise RuntimeError("Figma authorization callback did not return a code.")

    return callback_server.result


def build_oauth_provider() -> OAuthClientProvider:
    """Build the OAuth handler used to authenticate with Figma's remote MCP server.

    Reuses stored tokens/refreshes them automatically. Only triggers the
    interactive browser flow (redirect_handler/callback_handler) if no valid
    token is on hand -- callers running inside a Slack-triggered request
    should NOT hit that path; run scripts/figma_mcp_login.py once beforehand.
    """
    storage = FileTokenStorage(settings.figma_token_storage_path)

    client_metadata = OAuthClientMetadata(
        client_name="Agentic SDLC",
        redirect_uris=[REDIRECT_URI],
        application_type="native",
    )

    return OAuthClientProvider(
        server_url=settings.figma_mcp_url,
        client_metadata=client_metadata,
        storage=storage,
        redirect_handler=_redirect_handler,
        callback_handler=_callback_handler,
    )
