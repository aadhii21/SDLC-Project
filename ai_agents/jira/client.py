import asyncio

import httpx

from config.settings import settings

REQUEST_TIMEOUT_SECONDS = 15.0
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1.5


async def _jira_request(method: str, path: str, payload: dict):

    url = f"{settings.jira_base_url}{path}"

    async with httpx.AsyncClient(
        auth=(settings.jira_email, settings.jira_api_token),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as client:

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = await client.request(method, url, json=payload)
                break
            except httpx.TransportError as error:
                if attempt == MAX_ATTEMPTS:
                    print("\n========== JIRA TRANSPORT ERROR ==========")
                    print("URL:", url)
                    print(f"Failed after {MAX_ATTEMPTS} attempts:", repr(error))
                    print("===========================================\n")
                    return {
                        "error": True,
                        "status": None,
                        "response": f"Transport error after {MAX_ATTEMPTS} attempts: {error}",
                    }
                await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)

        print("\n========== JIRA DEBUG ==========")
        print("METHOD:", method)
        print("URL:", url)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        print("PAYLOAD:", payload)
        print("================================\n")

        if response.status_code >= 400:
            return {
                "error": True,
                "status": response.status_code,
                "response": response.text,
            }

        if not response.text:
            # Jira's PUT endpoints commonly return 204 No Content on success.
            return {"error": False, "status": response.status_code}

        return response.json()


async def jira_post(path: str, payload: dict):
    return await _jira_request("POST", path, payload)


async def jira_put(path: str, payload: dict):
    return await _jira_request("PUT", path, payload)
