import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils.formats import strip_lines
from langchain.chat_models import ChatOpenAI

from utils.prompt_template import PromptTemplate

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("GROQ_API_KEY")

# --- Initialize ChatGroq model ---
llm_groq = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0.2,
    max_retries=2
)

llm_mistral = ChatOpenAI(
    model_name="mistral-medium",
    temperature=0.2,
    max_retries=2,
    openai_api_key=os.getenv("MISTRAL_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

def clean_llm_output(text: str) -> str:
    lines = text.strip().splitlines()
    filler_prefixes = ("here is", "here are", "below is", "code:", "output:")

    # Remove triple backticks (with or without "python")
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().endswith("```"):
        lines = lines[:-1]

    # Filter out filler lines
    filtered = [
        line for line in lines
        if not line.strip().lower().startswith(filler_prefixes)
    ]

    return "\n".join(filtered).strip()

def ask_llm_groq(prompt: str) -> list[str]:
    print(f"Groq LLM prompt: {prompt}")
    response = llm_groq.invoke(prompt)
    cleaned_text = clean_llm_output(response.content)
    return strip_lines(cleaned_text) 

def review_code_with_mistral(code: str, dataset_columns: list[str]) -> str:
    cols_str = ", ".join(dataset_columns)
    review_prompt = PromptTemplate.REVIEW_CODE.value.format(
        cols_str=cols_str,
        code = code,
    )

    try:
        response = llm_mistral.invoke(review_prompt)
        return clean_llm_output(response.content)
    except Exception as e:
        return f"Mistral error: {e}"
    