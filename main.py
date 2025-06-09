# Load environment variables

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from langchain.chains.llm import LLMChain
from langchain.chat_models import init_chat_model
from starlette.middleware.cors import CORSMiddleware

from agent_model import model
from prompt.prompt import LLM_PROMPT_TEMPLATE_ESCAPED, PRISMA_SCHEMA_FOR_LLM, PYMONGO_OUTPUT_FORMAT_INSTRUCTIONS, \
    FEW_SHOT_EXAMPLES
from pydantic import BaseModel
from langchain.prompts import PromptTemplate


from langchain.agents import initialize_agent, AgentType, load_tools
from langchain.memory import ConversationBufferMemory

from tools.main import natural_language_query_executor
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from typing import AsyncGenerator
import asyncio

load_dotenv()


# Dictionary to store memory per user/session
user_memory_store = {}
tools = [
    natural_language_query_executor,  # The main tool for DB interaction
]


def get_agent_for_user(user_id):
    if user_id not in user_memory_store:
        user_memory_store[user_id] = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="input",  # or whatever your input var name is
            return_messages=True
        )


    memory = user_memory_store[user_id]

    return initialize_agent(
        tools=tools,
        llm=model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=False
    )






app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # caution: don't use in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentModel(BaseModel):
    query: str
    kinde_id:str

class AgentResponse(BaseModel):
    status: str
    result: str




import traceback

# @app.post("/ask", response_model=AgentResponse)
# async def get_answer_from_prompt(prompt: AgentModel):
#     try:
#         agent = get_agent_for_user(prompt.kinde_id)
#         result = agent.invoke({"input": prompt.query})
#         print(result)

#         return {
#             "status": "success",
#             "result": result.get('output')
#         }

#     except Exception as e:
#         traceback.print_exc()
#         return {
#             "status": "error",
#             "result": f"Exception occurred: {str(e)}"
#         }

@app.post("/ask")
async def get_answer_from_prompt(prompt: AgentModel):
    try:
        agent = get_agent_for_user(prompt.kinde_id)

        async def stream_generator() -> AsyncGenerator[str, None]:
            try:
                async for event in agent.astream({"input": prompt.query}):  # use `.astream` if your model supports it
                    token = event.get("output", "")
                    yield token
            except Exception as e:
                yield f"\n[Stream Error]: {str(e)}"

        return StreamingResponse(stream_generator(), media_type="text/plain")

    except Exception as e:
        return StreamingResponse(iter([f"[Error]: {str(e)}"]), media_type="text/plain")