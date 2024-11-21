from typing import Any, Dict

from dotenv import load_dotenv
from langchain import hub
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.agents.agent_toolkits import create_csv_agent

load_dotenv()


def main():
    print("Start...")
    instructions = """
    You are an agent designed to write and execute Python code to answer questions.
    You have access to a python REPL, which you can use to execute python code.
    You have qrcode package installed.
    If you get an error, debug your code and try again.
    Only use the output of your code to answer the question.
    You might know the answer without running any code, but you should still run the code to get the answer.
    If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
    """

    base_prompt = hub.pull("langchain-ai/react-agent-template")
    prompt = base_prompt.partial(instructions=instructions)

    tools = [PythonREPLTool()]
    python_agent = create_react_agent(
        prompt=prompt,
        llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=tools,
    )

    python_agent_executor = AgentExecutor(agent=python_agent, tools=tools, verbose=True)

    csv_agent_executor = create_csv_agent(
        llm=ChatOpenAI(temperature=0, model="gpt-4"),
        path="episode_info.csv",
        verbose=True,
        allow_dangerous_code=True,
    )

    tools = [
        Tool(
            name="Python Agent",
            func=python_agent_executor.invoke,
            description="""Useful when you need to transform natural language to Python 
            and execute the Python code, returning the results of the code execution.
            DOES NOT ACCEPT CODE AS INPUT""",
        ),
        Tool(
            name="CSV Agent",
            func=csv_agent_executor.invoke,
            description="""Useful when you need to answer questions over episode_info.csv.
            Takes as input the entire question and returns the answer after running pandas calculations.""",
        ),
    ]

    prompt = base_prompt.partial(instructions="")

    grand_agent = create_react_agent(
        prompt=prompt,
        llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
        tools=tools,
    )

    grand_agent_executor = AgentExecutor(
        agent=grand_agent,
        tools=tools,
        verbose=True
    )

    print(
        grand_agent_executor.invoke(
            {
                "input": "Which season has the most episodes?",
            }
        )
    )

    print(
        grand_agent_executor.invoke(
            {
                "input": "Generate and save in current working directory 15 QR codes that point to www.google.com",
            }
        )
    )


if __name__ == "__main__":
    main()
