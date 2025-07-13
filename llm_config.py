import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Initialize ChatGroq model ---
llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0.2,
    max_retries=2
)