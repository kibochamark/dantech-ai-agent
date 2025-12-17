from langchain.chat_models import init_chat_model
import os


model = init_chat_model("gpt-5-nano", model_provider="openai",
 api_key=os.getenv("GOOGLE_API_KEY"))
