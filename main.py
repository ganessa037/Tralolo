import os
import streamlit as st
import pandas as pd
from langchain_groq import ChatGroq

# --- Set up Groq API key ---
os.environ["GROQ_API_KEY"] = "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"  # Replace with your actual key

# --- Initialize Groq model ---
llm = ChatGroq(
    model_name="llama3-70b-8192",
    temperature=0.2,
    max_retries=2
)

# --- Set up Streamlit page ---
st.set_page_config(page_title="AskMyData AI", layout="wide")

# --- Patch missing imports helper ---
def patch_missing_imports(code):
    patched = code
    if "sns." in code and "import seaborn" not in code:
        patched = "import seaborn as sns\n" + patched
    if "datetime" in code and "import datetime" not in code and "from datetime" not in code:
        patched = "from datetime import datetime\n" + patched
    if "np." in code and "import numpy" not in code:
        patched = "import numpy as np\n" + patched
    return patched

# --- Initialize session state ---
defaults = {
    "df": None,
    "filename": "",
    "recent_questions": [],
    "suggested_questions": [],
    "question_input": "",
    "full_code": "",
    "in_app_code": "",
    "explanation": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- SIDEBAR: New Chat + Previous Questions ---
with st.sidebar:
    st.title("🧠 AskMyData AI")
    if st.button("🆕 New Chat"):
        for key in defaults:
            st.session_state[key] = defaults[key]
        st.rerun()

    st.markdown("### 📜 Chat History")
    if st.session_state.recent_questions:
        for i, q in enumerate(st.session_state.recent_questions):
            if st.button(q, key=f"history-{i}"):
                st.session_state.question_input = q
                st.rerun()
    else:
        st.info("No previous chats yet.")

# --- MAIN CONTENT AREA ---
st.markdown("<h1 style='text-align: center;'>Welcome to your Data Assistant</h1>", unsafe_allow_html=True)

# --- Upload CSV in center ---
if st.session_state.df is None:
    st.markdown("### 📁 Upload a CSV file to get started", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV", type="csv", label_visibility="collapsed")
    if uploaded_file:
        st.session_state.filename = uploaded_file.name
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success(f"✅ {uploaded_file.name} uploaded!")
        st.rerun()
else:
    st.success(f"✅ Working with: {st.session_state.filename}")

    # --- Suggested Questions Button ---
    if st.button("✨ Try Asking (AI Suggestions)"):
        cols = ", ".join(st.session_state.df.columns)
        prompt = f"Suggest 5 analytical questions for dataset columns: {cols}"
        try:
            res = llm.invoke(prompt).content
            st.session_state.suggested_questions = [s.strip().lstrip("–-") for s in res.splitlines() if s.strip()]
        except Exception as e:
            st.error(f"Suggestion error: {e}")

    # --- Show Suggestions ---
    if st.session_state.suggested_questions:
        st.markdown("#### 💡 Suggested Questions")
        for s in st.session_state.suggested_questions:
            if st.button(s, key=f"suggest-{s}"):
                st.session_state.question_input = s
                st.rerun()

    # --- Ask Question & Educational Mode ---
    st.divider()
    edu_mode = st.radio("🎓 Educational Mode", ["Just Code", "Explain for Beginners"], horizontal=True)
    question = st.text_input("💬 Ask your question:", value=st.session_state.question_input)

    if st.button("🔍 Submit"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            st.session_state.recent_questions = [question] + st.session_state.recent_questions[:4]
            explain_flag = ("and add beginner-friendly comments" if edu_mode.startswith("Explain")
                            else "and keep it concise and professional.")
            cols = ", ".join(st.session_state.df.columns)
            filename = st.session_state.filename

            prompt = f"""
You are a helpful data scientist.
1. Write a standalone script loading '{filename}', using [{cols}], and answer: "{question}" {explain_flag}
   Store result in `result`. Use Streamlit for plots.
2. Then give a short in-app version assuming `df` is loaded.
# Standalone Code
# In-App Version
"""
            try:
                res = llm.invoke(prompt).content
                if "# In-App Version" in res:
                    parts = res.split("# In-App Version")
                    full, in_app = parts[0].replace("# Standalone Code", "").strip(), parts[1].strip()
                else:
                    full, in_app = res.strip(), res.strip()
                full = full.replace("data.csv", filename)
                in_app = in_app.replace("plt.show()", "st.pyplot(plt.gcf())")
                st.session_state.full_code = full
                st.session_state.in_app_code = patch_missing_imports(in_app)
                st.session_state.explanation = ""
            except Exception as e:
                st.error(f"Code generation error: {e}")

    # --- Show Generated Code ---
    if st.session_state.full_code:
        st.markdown("### 🧪 Full Script")
        st.code(st.session_state.full_code, "python")

    if st.session_state.in_app_code:
        st.markdown("### ⚙️ In-App Code")
        st.code(st.session_state.in_app_code, "python")
        if st.button("▶️ Run In-App Code"):
            local = {"df": st.session_state.df.copy()}
            try:
                exec(st.session_state.in_app_code, {}, local)
                if "result" in local:
                    result = local["result"]
                    if isinstance(result, pd.DataFrame):
                        st.dataframe(result)
                    else:
                        st.write(result)
                else:
                    st.warning("No result variable found.")
            except Exception as e:
                st.error(f"Run error: {e}")

    # --- Explain the Code ---
    if st.session_state.in_app_code:
        if st.button("🔎 Explain Code"):
            try:
                prompt = f"Explain this Python pandas code line‑by‑line:\n{st.session_state.in_app_code}"
                st.session_state.explanation = llm.invoke(prompt).content
            except Exception as e:
                st.error(f"Explain error: {e}")
        if st.session_state.explanation:
            st.markdown("### 💡 Explanation")
            st.markdown(st.session_state.explanation)
