# agents/testing_agent.py


def run_testing_agent(user_query: str):

    print(
        "TESTING AGENT RECEIVED:",
        user_query
    )

    return (
        "Testing Agent received your request: "
        + user_query
    )