import os
import streamlit as st
import pandas as pd
from langchain_groq import ChatGroq

# --- Set up Groq API key ---
os.environ["GROQ_API_KEY"] = "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"  # 🔁 Replace with your real key

# --- Initialize ChatGroq model ---
llm = ChatGroq(
    model_name="llama3-70b-8192",  # ✅ Valid model
    temperature=0.2,
    max_retries=2
)

# --- Page Setup ---
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

# --- Suggest questions ---
if st.session_state.df is not None and st.button("✨ Try Asking (AI Suggestions)"):
    cols = ", ".join(st.session_state.df.columns)
    prompt = f"Suggest 5 analytical questions for dataset columns: {cols}"
    try:
        res = llm.invoke(prompt).content  # ✅ FIXED
        st.session_state.suggested_questions = [s.strip().lstrip("–-") for s in res.splitlines() if s.strip()]
    except Exception as e:
        st.error(f"Suggestion error: {e}")

# --- Show suggestions ---
if st.session_state.suggested_questions:
    st.markdown("#### 💡 Suggestions:")
    for s in st.session_state.suggested_questions:
        if st.button(s, key=s):
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
You are a helpful data scientist.
1. Write a standalone script loading '{filename}', using [{cols}], and answer: "{question}" {explain_flag}
   Store result in `result`. Use Streamlit for plots.
2. Then give a short in-app version assuming `df` is loaded.
# Standalone Code
# In-App Version
"""
            try:
                res = llm.invoke(prompt).content  # ✅ FIXED
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

# --- Display outputs ---
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
                res = local["result"]
                if isinstance(res, pd.DataFrame):
                    st.dataframe(res)
                else:
                    st.write(res)
            else:
                st.warning("No result variable found.")
        except Exception as e:
            st.error(f"Run error: {e}")

# --- Explain code block ---
if st.session_state.in_app_code:
    if st.button("🔎 Explain Code"):
        try:
            prompt = f"Explain this Python pandas code line‑by‑line:\n{st.session_state.in_app_code}"
            st.session_state.explanation = llm.invoke(prompt).content  # ✅ FIXED
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
