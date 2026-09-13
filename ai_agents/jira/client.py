import os
import httpx

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


async def jira_post(path: str, payload: dict):

    url = f"{JIRA_BASE_URL}{path}"

    async with httpx.AsyncClient(
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
    ) as client:

        response = await client.post(url, json=payload)

        print("\n========== JIRA DEBUG ==========")
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

        return response.json()