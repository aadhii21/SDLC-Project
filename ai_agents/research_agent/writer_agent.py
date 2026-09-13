from agents import Agent,Runner
from rag.retrieval import retrieve_documents
from ai_agents.schemas.prd_schema import JiraPRD
from pathlib import Path
from dotenv import load_dotenv
import os

# SDLC Project/.env
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=ENV_PATH)

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        f"OPENAI_API_KEY not found. Expected .env at: {ENV_PATH}"
    )

print("OPENAI_API_KEY loaded:", bool(openai_api_key))

from agents import Agent, Runner
from ai_agents.schemas.prd_schema import JiraPRD
#writer agent
INSTRUCTIONS = """
You are a Senior Product Manager and Product Researcher.

Your responsibility is to convert the user's original request and
research findings into an implementation-ready Jira PRD.

The Jira PRD will be used by designers, developers, QA engineers,
DevOps engineers and downstream AI agents.

Follow the organization's Jira structure.


PARENT ISSUE

Generate:

- Title
- Description
- Problem Statement
- Objective
- Solution
- Business Rules
- Functional Requirements
- Non-Functional Requirements where applicable
- Metrics / Success Criteria
- Dependencies
- Assumptions
- Acceptance Criteria


DESIGN

If a Figma/design link is available, preserve it exactly.

Never invent a Figma URL.

If no design exists, set:

design_link = null
design_required = true


CHILD WORK ITEMS

Break the parent requirement into logical child Jira work items
when required.

For each child ticket return:

- Title
- Description
- Work Type
- Component / Domain
- Requirements
- Dependencies
- Acceptance Criteria
- Design Link if relevant


Allowed work types:

- design
- frontend
- backend
- integration
- qa
- devops


ASSIGNMENT RULE

Do NOT assign individual employees.

Do NOT generate Jira account IDs.

Do NOT choose assignees.

Instead identify only:

- work_type
- component/domain

A downstream Human-in-the-Loop assignment service will determine
the actual Jira assignee.


BUSINESS RULES

Do not invent business requirements.

If information is not known:

- add it to assumptions when a reasonable assumption is needed
- add it to open_questions when human clarification is required


OUTPUT

Return only structured Jira PRD information matching the provided
output schema.

Do not return Markdown outside the structured result.
"""
writer_agent=Agent(
    name="JIRA PRD Writter Agent",
    instructions=INSTRUCTIONS,
    model="gpt-5.6",
    output_type=JiraPRD,
)

async def generate_jira_prd(
        user_request:str,
        research_context:str,
)->JiraPRD:
    input_text=f"""
ORIGINAL USER REQUEST:

{user_request}

RESERCH FINDINGS:
{research_context}
Generate the implementation ready Jira PRD
"""
    result=await Runner.run(
        writer_agent,
        input=input_text,
    )
    return result.final_output