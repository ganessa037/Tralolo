# main.py
import re
import streamlit as st
from llm_config import llm_groq
from utils.sessions import initialize_state
from utils.handlers import FileHandler, ExecutionHandler
from utils.invokers import AIActionInvoker

# --- Page Setup ---
st.set_page_config(page_title="AskMyData AI", layout="wide")

# --- Initialize session state, to save the states for rerun ---
initialize_state()

# --- file upload, appear in sidebar ---
FileHandler.upload_files()

# --- Main UI ---
st.markdown("<h1>Welcome to your Data Assistant!</h1>", unsafe_allow_html=True)
st.write("Ask questions about your data — I'll generate Python code and explain it!")


if st.session_state.get("df") is not None:
    st.dataframe(st.session_state.df.head(10))

    # --- Suggest questions ---
    if st.button("✨ Try Asking (AI Suggestions)"):
        AIActionInvoker.get_questions_suggestions()

    # --- Show suggested questions ---
    for i, s in enumerate(st.session_state.suggested_questions):
        if s.strip():
            if st.button(s, key=f"suggestion_{i}"):
                st.session_state.question_input = s

     # --- Inputs for code generation ---
    st.divider()
    mode = st.radio("🎓 Educational Mode", ["Just Code", "Explain for Beginners"], horizontal=True)
    question = st.text_input("💬 Ask your question:", value=st.session_state.question_input or "")

    if st.button("🔍 Submit"):
        if not question:
            st.warning("Ask something!")
        else:
            st.session_state.recent_questions = [question] + st.session_state.recent_questions[:4]
            AIActionInvoker.generate_code(question, mode)

# --- Display outputs ---
if st.session_state.full_code:
    st.markdown("### 🧪 Standalone Code (for integration)")
    st.code(st.session_state.full_code, "python")

if st.session_state.in_app_code:
    st.markdown("### ⚙️ Full Script (Streamlit Compatible)")
    in_app = st.session_state.in_app_code
    in_app = re.sub(r'pd\.read_csv\s*\((?:[^)(]+|\([^)]*\))*\)', "df.copy()", in_app)
    in_app = re.sub(r'df\s*=\s*pd\.DataFrame\s*\(\s*\)', "df = df.copy()", in_app)
    in_app = re.sub(r'set\s*\(\s*stopwords_words\s*\)', "stopwords_words", in_app)
    st.code(in_app, "python")
    
    if st.button("▶️ Run In-App Code"):
        ExecutionHandler.execute_code(in_app)

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