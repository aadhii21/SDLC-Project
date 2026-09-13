"""
One-time interactive login for the Figma remote MCP server.

Run this manually (it opens a real browser window):

    ./.venv/bin/python scripts/figma_mcp_login.py

It performs the OAuth authorization-code + PKCE flow (with Dynamic Client
Registration) against settings.figma_mcp_url and persists the resulting
tokens to settings.figma_token_storage_path. Re-run it whenever that token
file is deleted or a refresh permanently fails.
"""

import asyncio

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from ai_agents.design_agent.figma_mcp_auth import build_oauth_provider
from config.settings import settings


async def main() -> None:
    oauth_provider = build_oauth_provider()

    async with httpx2.AsyncClient(auth=oauth_provider) as http_client:
        async with streamable_http_client(
            settings.figma_mcp_url,
            http_client=http_client,
        ) as (read_stream, write_stream):

            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                tools = await session.list_tools()
                tool_names = [tool.name for tool in tools.tools]

    print("\nFigma MCP login successful.")
    print(f"Tokens stored at: {settings.figma_token_storage_path}")
    print(f"Available tools ({len(tool_names)}): {', '.join(tool_names)}")


if __name__ == "__main__":
    asyncio.run(main())
