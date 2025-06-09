from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv()

model = init_chat_model("gemini-2.0-flash", model_provider="google_genai",
 GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"))
