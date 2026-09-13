import asyncio

from ai_agents.design_agent.design_agent import generate_design
from ai_agents.design_agent.figma_generator import generate_figma_design

async def main():

    prd = """
    Create a nominee management screen.

    User should be able to:
    - Add nominee
    - Remove nominee
    - Add maximum 3 nominees
    - Total allocation must equal 100%
    """

    design = await generate_design(prd)
    figma_result= await generate_figma_design(design)

    print(figma_result)


if __name__ == "__main__":
    asyncio.run(main())