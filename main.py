import re
from matplotlib import pyplot as plt
import nltk
import numpy as np
import streamlit as st
import pandas as pd
import seaborn as sns
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from llm_config import ask_llm_groq, review_code_with_mistral ,llm_groq
from utils import patch_missing_imports
import warnings

nltk.download('punkt')
nltk.download('stopwords')

# --- Page Setup ---
st.set_page_config(page_title="AskMyData AI", layout="wide")

# --- Initialize session state, to save the states for rerun ---
for key in ["df", "recent_questions", "full_code", "in_app_code",
            "filename", "explanation", "suggested_questions", "question_input"]:
    if key not in st.session_state:
        if key == "df":
            st.session_state[key] = None
        elif "questions" in key:
            st.session_state[key] = []
        else:
            st.session_state[key] = ""

# --- Sidebar for upload ---
with st.sidebar:
    st.title("📊 Data Assistant")
    uploaded_file = st.file_uploader("Upload your CSV file here", type="csv")
    if uploaded_file:
        st.session_state.filename = uploaded_file.name
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success(f"✅ {uploaded_file.name} uploaded!")

# --- Main UI ---
st.markdown("<h1>Welcome to your Data Assistant!</h1>", unsafe_allow_html=True)
st.write("Ask questions about your data — I'll generate Python code and explain it!")

# --- Show uploaded data ---
if st.session_state.get("df") is not None:
    st.dataframe(st.session_state.df.head(10))

# --- Suggest questions ---
if st.session_state.df is not None and st.button("✨ Try Asking (AI Suggestions)"):
    cols = ", ".join(st.session_state.df.columns)
    prompt = (
        f"List only 5 analytical questions based on these dataset columns: {cols}. "
        f"Output only the questions in plain bullet points. Do not include any introductory or concluding sentence."
    )
    try:
        st.session_state.suggested_questions = ask_llm_groq(prompt)
    except Exception as e:
        st.error(f"Suggestion error: {e}")

# --- Show suggestions ---
for i, s in enumerate(st.session_state.suggested_questions):
    if s.strip():  # skip empty or blank entries
        if st.button(s, key=f"suggestion_{i}"):
            st.session_state.question_input = s

# --- Ask & generate code ---
if st.session_state.df is not None:
    st.divider()
    edu_mode = st.radio("🎓 Educational Mode", ["Just Code", "Explain for Beginners"], horizontal=True)
    question = st.text_input("💬 Ask your question:", value=st.session_state.question_input or "")

    if st.button("🔍 Submit"):
        if not question:
            st.warning("Ask something!")
        else:
            st.session_state.recent_questions = [question] + st.session_state.recent_questions[:4]
            explain_flag = ("and add beginner-friendly comments" if edu_mode.startswith("Explain")
                            else "and keep it concise and professional.")
            cols = ", ".join(st.session_state.df.columns)
            filename = st.session_state.filename

            prompt = f"""
                You are a Python coding assistant. Return only valid Python code — no markdown, no explanations.

                Write two code outputs:

                1. # Standalone Code
                - Write clean logic to answer: "{question}" using the file '{filename}' and columns [{cols}]
                - Use only common libraries: pandas, numpy, matplotlib, seaborn, sklearn, nltk
                - Always assign the final output (e.g., result DataFrame, numeric value, or message string) to a variable named `result`
                - If displaying a chart or message only, assign `result = "Chart displayed"` or similar

                2. # In-App Version
                - Same as above, but format as a full Streamlit script
                - Use `st.pyplot()` instead of `plt.show()`
                - If using `word_tokenize` or `stopwords`, include:
                    import nltk
                    nltk.download('punkt')
                    nltk.download('stopwords')
                - Always assign something meaningful to `result`
                """

            try:
                res = ask_llm_groq(prompt)
                if isinstance(res, list):
                    res = "\n".join(res)

                normalized = res.replace("**In-App Version (Streamlit)**", "# In-App Version").replace("**Standalone Code**", "# Standalone Code").replace("**In-App Version**", "# In-App Version")

                if "# In-App Version" in normalized:
                    parts = normalized.split("# In-App Version")
                    full = parts[0].replace("# Standalone Code", "").strip()
                    in_app = parts[1].strip()
                else:
                    full = in_app = normalized.strip()

                full = full.replace("data.csv", filename)
                in_app = in_app.replace("plt.show()", "st.pyplot(plt.gcf())")
                in_app = in_app.replace("@st.cache", "@st.cache_data")
                st.session_state.full_code = full
                st.session_state.in_app_code = patch_missing_imports(in_app)
                st.session_state.explanation = ""
                with st.spinner("🤖 Mistral is reviewing your code..."):
                    print("Reviewing code with Mistral...")
                    mistral_review = review_code_with_mistral(st.session_state.in_app_code, st.session_state.df.columns.tolist())
                    st.session_state.in_app_code = mistral_review
                
            except Exception as e:
                st.error(f"Code generation error: {e}")

# --- Display outputs ---
if st.session_state.full_code:
    st.markdown("### 🧪 Standalone Code (for integration)")
    st.code(st.session_state.full_code, "python")

if st.session_state.in_app_code:
    st.markdown("### ⚙️ Full Script")
    in_app = st.session_state.in_app_code
    in_app = re.sub(r'pd\.read_csv\s*\((?:[^)(]+|\([^)]*\))*\)', "df.copy()", in_app)
    in_app = re.sub(r'df\s*=\s*pd\.DataFrame\s*\(\s*\)', "df = df.copy()", in_app)
    in_app = re.sub(r'set\s*\(\s*stopwords_words\s*\)', "stopwords_words", in_app)
    st.code(in_app, "python")
    
    if st.button("▶️ Run In-App Code"):
        local = {
            "df": st.session_state.df.copy(),
            "pd": pd,
            "np": np,
            "plt": plt,
            "sns": sns,
            "nltk": nltk,
            "st": st,
            "word_tokenize": word_tokenize,
            "stopwords": stopwords,
            "stopwords_words": list(stopwords.words("english")),  # ✅ FIXED
            "__builtins__": __builtins__,
        }

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)  # 👈 Ignore only deprecation warnings
                exec(in_app, local, local)
                
            func_candidates = [v for v in local.values() if callable(v)]
            if len(func_candidates) == 1:
                func_candidates[0]()  # attempt to run the single defined function

        except Exception as e:
            st.error(f"Run error: {e}")

# --- Explain code block ---
if st.session_state.in_app_code:
    if st.button("🔎 Explain Code"):
        try:
            prompt = f"Explain this Python pandas code line‑by‑line:\n{st.session_state.in_app_code}"
            st.session_state.explanation = llm_groq.invoke(prompt).content  # ✅ FIXED
        except Exception as e:
            st.error(f"Explain error: {e}")
    if st.session_state.explanation:
        st.markdown("### 💡 Explanation")
        st.markdown(st.session_state.explanation)

# --- Recent questions ---
if st.session_state.recent_questions:
    st.markdown("### 📌 Recent Questions")
    for i, q in enumerate(st.session_state.recent_questions):
        cols = st.columns([8, 1])
        cols[0].write(f"- {q}")
        if cols[1].button("❌", key=f"delete-{i}"):
            st.session_state.recent_questions.pop(i)
            st.experimental_rerun()