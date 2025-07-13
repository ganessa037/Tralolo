import streamlit as st
import pandas as pd
from llm_config import ask_llm, llm
from utils import patch_missing_imports

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
        st.session_state.suggested_questions = ask_llm(prompt)
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

            prompt = (
                f"You are a coding assistant. Return only valid Python code — no markdown, no text, and no explanations.\n\n"
                f"Write two code outputs:\n\n"
                f"1. # Standalone Code\n"
                f"Only include the logic needed to answer the following question based on the file '{filename}' using columns [{cols}]:\n"
                f"\"{question}\"\n"
                f"{explain_flag}\n"
                f"Do not include file loading, Streamlit layout, or UI code. Use Streamlit for plotting if needed. "
                f"Store the final result in a variable named 'result'.\n\n"
                f"2. # In-App Version\n"
                f"Write a full Streamlit script that:\n"
                f"- Loads the file '{filename}'\n"
                f"- Uses the columns [{cols}]\n"
                f"- Answers the same question: \"{question}\"\n"
                f"- Displays a chart\n"
                f"- Stores the final result in a variable called 'result'\n\n"
                f"Use clear and explicit variable and function names.\n"
                f"Do not include any comments, markdown formatting (like ```), or explanations. Return pure code only."
            )

            try:
                res = ask_llm(prompt)
                if isinstance(res, list):
                    res = "\n".join(res)

                normalized = res.replace("**In-App Version**", "# In-App Version").replace("**Standalone Code**", "# Standalone Code")

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
                
            except Exception as e:
                st.error(f"Code generation error: {e}")

# --- Display outputs ---
if st.session_state.full_code:
    st.markdown("### 🧪 Standalone Code (for integration)")
    st.code(st.session_state.full_code, "python")

if st.session_state.in_app_code:
    st.markdown("### ⚙️ Full Script")
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
                st.warning("idk why hmm")
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