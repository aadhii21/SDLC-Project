import secrets

from fastapi import Header, HTTPException, status

from config.settings import settings


async def verify_plugin_token(x_plugin_token: str = Header(default="")) -> None:
    """Shared-secret check between the Figma plugin and this service. Fails
    closed: an unconfigured FIGMA_PLUGIN_API_TOKEN rejects every request
    rather than falling back to "no auth required"."""
    expected = settings.figma_plugin_api_token
    if not expected or not secrets.compare_digest(x_plugin_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-Plugin-Token")
