import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils import patch_missing_imports, strip_lines

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Initialize ChatGroq model ---
llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0.2,
    max_retries=2
)

def clean_llm_output(text: str) -> str:
    lines = text.splitlines()
    filler_prefixes = ("here is", "here are", "below is", "code:", "output:")

    filtered = [
        line for line in lines
        if not line.strip().lower().startswith(filler_prefixes)
    ]

    return "\n".join(filtered)

def ask_llm(prompt: str) -> list[str]:
    print(f"LLM Prompt: {prompt}")
    response = llm.invoke(prompt)
    cleaned_text = clean_llm_output(response.content)
    return strip_lines(cleaned_text) 