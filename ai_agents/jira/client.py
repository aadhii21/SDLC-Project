import httpx

from config.settings import settings


async def jira_post(path: str, payload: dict):

    url = f"{settings.jira_base_url}{path}"

    async with httpx.AsyncClient(
        auth=(settings.jira_email, settings.jira_api_token),
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