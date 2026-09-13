from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool
from agents.model_settings import ModelSettings
from pydantic import BaseModel,Field
from dotenv import load_dotenv
import asyncio
import os
from typing import Dict
from IPython.display import display,Markdown
#from messenger import send_email,push

load_dotenv(override=True)
open_api_key=os.getenv("OPENAI_API_KEY")
MODEL_NAME="gpt-5.4-mini"
USE_EMAIL=True
HOW_MANY_SEARCHES=5
#includes 4 agents here
#the search agent/the planner agent/the writer agent/ the emailer agent
#the search agent
INSTRUCTIONS="""
You are a research assistant. Given a search term, you search the web for that term and produce a concise summary of the results. The summary must 2-3 praragraphs and less than 300 words.
Capture the main points and be succinct.Reply only with the summary.
"""
task="Most popular AI Agent frameworks in 2026"

settings=ModelSettings(tool_choice="required")

async def search():    
    tools = [WebSearchTool()]
    search_agent=Agent(name="Search Agent",instructions=INSTRUCTIONS,tools=tools,model=MODEL_NAME,model_settings=settings)
    result = await Runner.run(search_agent,task)
    #display(Markdown(result.final_output))
    print(result.final_output)
#the planner agent
class WebSearchItem(BaseModel):
    reason:str=Field(description="Yor reasoning for why this search is important to the query.")
    query:str=Field(description="The search term to use for the web search.")

class WebSearchPlan(BaseModel):
    searches:list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")

WebSearchPlan.model_json_schema()
INSTRUCTIONS=f"""
You are a research planner assistant. Given a user query, come up with a set of web searches
to perform to best answer the query. Output{HOW_MANY_SEARCHES} terms to query for.
"""
async def plan():   
    planner_agent=Agent(name="Planner Agent",instructions=INSTRUCTIONS,model=MODEL_NAME,output_type=WebSearchPlan)
    result=await Runner.run(planner_agent,task)
    #display(Markdown(result.final_output))
    print(result.final_output)
async def main():

    await plan()

    await search()


if __name__ == "__main__":
    asyncio.run(main())