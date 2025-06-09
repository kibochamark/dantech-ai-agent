from langchain.chains import LLMChain
from langchain.chat_models import init_chat_model


import datetime
import json
import re
from typing import Any, Union

from langchain_core.prompts import PromptTemplate
from pymongo import MongoClient
from langchain.tools import tool

from agent_model import model
from helpers.main import replace_placeholders
from prompt.prompt import LLM_PROMPT_TEMPLATE_ESCAPED, PRISMA_SCHEMA_FOR_LLM, PYMONGO_OUTPUT_FORMAT_INSTRUCTIONS,FEW_SHOT_EXAMPLES

prompt_temp = PromptTemplate(template=LLM_PROMPT_TEMPLATE_ESCAPED, input_variables=["user_query", "PRISMA_SCHEMA_FOR_LLM", "PYMONGO_OUTPUT_FORMAT_INSTRUCTIONS", "FEW_SHOT_EXAMPLES", "fewShotExamples"])

@tool
def natural_language_to_pymongo(user_query: str) -> str: 

  """ Converts natural language query to a PyMongo executable query, capable of handling requests for the latest data by inferring sorting based on a date or timestamp field and applying limits.
  Args: user_query: The user's query in natural language. Returns: A JSON string representing the PyMongo query.
  """


  chain = LLMChain(llm=model, prompt=prompt_temp)
  result = chain.run({
  "user_query": user_query,   
"PRISMA_SCHEMA_FOR_LLM":PRISMA_SCHEMA_FOR_LLM,
"PYMONGO_OUTPUT_FORMAT_INSTRUCTIONS":PYMONGO_OUTPUT_FORMAT_INSTRUCTIONS,
"FEW_SHOT_EXAMPLES":FEW_SHOT_EXAMPLES,
      "fewShotExamples":FEW_SHOT_EXAMPLES,
  "yesterday_start":None,
    "today_start":None,
    "last_month_start":None,
    "last_month_end":None,
    "last_7_days_start":None,
    "now":None,
    "YYYY-MM-DD_start":None,
    "YYYY-MM-DD_end":None,
 
  })

  return result


@tool
def run_pymongo_query(result: str) -> Union[str, list]:
    """Parses a PyMongo JSON string from LLM, replaces date placeholders, runs the query, and returns the results."""
    try:
        # Parse the JSON block (with or without markdown)
        if result.strip().startswith("```json"):
            result = result.strip().removeprefix("```json").removesuffix("```").strip()

        parsed_json = json.loads(result)
        final_query = replace_placeholders(parsed_json)

        # Connect to MongoDB
        client = MongoClient("mongodb+srv://thesirfire:D95lUHfKygx9819S@dantech.w9lwt.mongodb.net/dantech?retryWrites=true&w=majority&appName=Dantech")  # Replace with env-safe version
        db = client["dantech"]
        collection = db[final_query["collection"]]

        # Handle operation
        operation = final_query["operation"]
        if operation == "aggregate":
            return list(collection.aggregate(final_query["pipeline"]))
        elif operation == "find":
            cursor = collection.find(final_query.get("query", {}), final_query.get("projection", {}))
            if "sort" in final_query:
                cursor = cursor.sort(list(final_query["sort"].items()))
            if "limit" in final_query:
                cursor = cursor.limit(final_query["limit"])
            return list(cursor)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    except json.JSONDecodeError as e:
        return f"JSON decoding error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    finally:
        try:
            client.close()
        except:
            pass


@tool
def natural_language_query_executor(nl_query: str) -> str:
    """
    Executes MongoDB queries from natural language instructions.

    This tool serves as a high-level wrapper that enables users to perform MongoDB operations 
    simply by expressing their intent in natural language. It abstracts away the complexity 
    of query construction and execution by chaining two sub-tools:

    1. `natural_language_to_pymongo`: Converts a plain English question (e.g., 
       "Show me all orders from last month") into a structured PyMongo-style JSON query.
    
    2. `run_pymongo_query`: Takes the generated PyMongo JSON, resolves any dynamic 
       placeholders (e.g., `{{last_month}}`), and runs the query against a live MongoDB 
       database. It supports both `find` and `aggregate` operations.

    Parameters:
    ----------
    nl_query : str
        A natural language question or instruction that describes the user's data retrieval need.
        Example: "List all users who signed up this week."

    Returns:
    -------
    str
        A JSON-formatted string representing the results of the MongoDB query. If an error occurs 
        during processing or execution, a descriptive error message is returned instead.

    Use Case:
    --------
    Ideal for chatbots, dashboards, or data assistant agents where users can query MongoDB 
    without needing to understand the query syntax.

    """
    pymongo_query = natural_language_to_pymongo.run(nl_query)
    print(pymongo_query)
    result = run_pymongo_query.run(pymongo_query)
    return result
