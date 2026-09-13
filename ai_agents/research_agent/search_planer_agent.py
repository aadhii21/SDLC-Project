import asyncio
import os

from agents import Agent, Runner, WebSearchTool
from agents.model_settings import ModelSettings
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "gpt-5.4-mini"
HOW_MANY_SEARCHES = 5

SEARCH_INSTRUCTIONS = """
You are a research assistant. Given a search term, you search the web for that term and produce a concise summary of the results. The summary must 2-3 praragraphs and less than 300 words.
Capture the main points and be succinct. Reply only with the summary.
"""

search_settings = ModelSettings(tool_choice="required")
search_agent = Agent(
    name="Search Agent",
    instructions=SEARCH_INSTRUCTIONS,
    tools=[WebSearchTool()],
    model=MODEL_NAME,
    model_settings=search_settings,
)


class WebSearchItem(BaseModel):
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


PLANNER_INSTRUCTIONS = f"""
You are a research planner assistant. Given a user query, come up with a set of web searches
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for.
"""

planner_agent = Agent(
    name="Planner Agent",
    instructions=PLANNER_INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=WebSearchPlan,
)


async def _run_single_search(item: WebSearchItem) -> str:
    result = await Runner.run(search_agent, f"Search term: {item.query}\nReason: {item.reason}")
    return result.final_output


async def run_research_agent(query: str) -> str:
    plan_result = await Runner.run(planner_agent, query)
    plan: WebSearchPlan = plan_result.final_output

    summaries = await asyncio.gather(
        *[_run_single_search(item) for item in plan.searches]
    )

    return "\n\n".join(summaries)


if __name__ == "__main__":
    async def main():
        result = await run_research_agent("Most popular AI Agent frameworks in 2026")
        print(result)

    asyncio.run(main())
