from langchain.chat_models import init_chat_model
import os


model = init_chat_model("gemini-2.0-flash", model_provider="google_genai",
 api_key=os.getenv("GOOGLE_API_KEY"))