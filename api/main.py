"""Figma job service -- the only HTTP surface in this project. Slack itself
runs over Socket Mode (see slack/run.py) and never touches this process;
this app exists purely so the Figma plugin (running inside the Figma
desktop app, which can't import Python) has an HTTP endpoint to poll for
work and report results back to.

Run with:
    uvicorn api.main:app --port 8787 --reload
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config.logging  # noqa: F401 -- side effect: configures root logger format/level for this process
from config.settings import settings
from integrations.figma.service.routes import router as figma_jobs_router

logger = logging.getLogger(__name__)

if not settings.figma_plugin_api_token:
    # Fail at startup, not on the plugin's first request -- an empty token
    # would otherwise mean every request gets an identical 401 with no clue
    # why, and auth.py's fail-closed check makes that failure silent-looking
    # (no distinct "misconfigured" vs "wrong token" response).
    raise RuntimeError(
        "FIGMA_PLUGIN_API_TOKEN is not configured -- set it in .env before starting this service "
        "(see .env.example)."
    )

app = FastAPI(title="Figma Job Service")

# The Figma plugin's fetch() runs in Figma's plugin sandbox, which enforces
# normal CORS rules against whatever this server responds with -- without
# this, the browser-side preflight (triggered by the custom X-Plugin-Token
# header) would fail before the actual request is ever sent. Wide open here
# because this service only ever runs on localhost in dev; tighten
# allow_origins if this is ever deployed anywhere reachable off-machine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(figma_jobs_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=settings.figma_job_service_port)
