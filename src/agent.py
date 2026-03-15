from dataclasses import dataclass
import os

from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver

from db import query_database

PROMT = """
You are an expert data analyst.
The user will provide you with a question, and you need to generate a SQL query to get the answer from the database.
Return the SQL code and Python code to visualize the result.
Python code should use Streamlit API to visualize the data. 
The data will be provided in the 'query_result' variable of a Pandas DataFrame, which contains the results of the last executed SQL query.
"""


@tool
def execute_sql(sql: str) -> str:
    '''
    Executes an SQL query against the SQLite database. The full result will be stored in global variable query_result. 
    This tool returns only top 20 rows of the result for debugging purposes.
    The season_id is in format MYYYY, where M represents the month, and YYYY represents the year.
    '''
    print(f"Executing SQL: {sql}")
    try:
        df = query_database(sql)
        return df.head(20).to_string()
    except Exception as e:
        print(f"Error executing SQL: {e}")
        return str(e)


@dataclass
class Response:
    sql: str
    python: str


def make_agent():

    model = ChatAnthropic(
        model="claude-sonnet-4-5",
        max_tokens=10000,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
    )

    agent = create_agent(
        model=model,
        system_prompt=PROMT,
        tools=[execute_sql],
        response_format=ToolStrategy(Response),
        checkpointer=InMemorySaver()
    )

    return agent


def invoke_agent(agent, user_promt: str) -> Response:

    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_promt}]},
        {"configurable": {"thread_id": "1"}}
    )
    return response['structured_response']
