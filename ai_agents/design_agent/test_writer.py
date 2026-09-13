import asyncio


async def main():

    prd = """
    Feature: Add Others section in My Wealth Dashboard.

    Requirements:

    - Add an Others section.
    - Bank, Stocks and Mutual Funds should be displayed.
    - Each item should be clickable.
    - Both text and value area should be clickable.
    - Clicking should navigate to corresponding wealth details.
    """

    design = await generate_design(prd)

    print(design.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())