import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from main_utils import strip_lines
from langchain.chat_models import ChatOpenAI

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
    openai_api_base="https://api.mistral.ai/v1",
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
    review_prompt = f"""
        You are a Python expert. Please review and revise the following code.

        Your tasks:
        1. Check for any syntax or logic errors.
        2. Verify that the column names used match the actual dataset columns: [{cols_str}].
        3. If any column names are incorrect or unclear, correct them using the provided column names.
        4. Apply improvements based on Python and data analysis best practices.
        5. Ensure the code is clean, professional, and safe to execute.
        6. Do not explain — just return the revised, executable Python code.
        7. Do not define a data loading function; use `df = df.copy()` directly to access the dataset.
        8. Replace any `plt.show()` with `st.pyplot(plt.gcf())` for Streamlit compatibility if there's any.
        Code:
        {code}
        """
    try:
        response = llm_mistral.invoke(review_prompt)
        return clean_llm_output(response.content)
    except Exception as e:
        return f"❌ Mistral error: {e}"
    