import streamlit as st
import pandas as pd
import requests
import io


# Fix missing imports if seaborn or datetime usage is detected
def patch_missing_imports(code):
    patched = code
    if "sns." in code and "import seaborn" not in code:
        patched = "import seaborn as sns\n" + patched
    if "datetime" in code and "import datetime" not in code and "from datetime" not in code:
        patched = "from datetime import datetime\n" + patched
    if "np." in code and "import numpy" not in code:
        patched = "import numpy as np\n" + patched
    return patched

st.set_page_config(page_title="Tralolo", layout="wide")
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "codellama"

# ---- Session State ----
for key in ["df", "recent_questions", "full_code", "in_app_code", "filename", "explanation", "suggested_questions"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "questions" in key else ""

# ---- Title ----
st.markdown("""<h1 style='font-size: 2.5em; margin-bottom: 0;'>📊 AskMyData AI</h1>
<p style='color: gray; margin-top: 0;'>Upload a dataset. Ask questions in English. Get Python code, visualizations, and explanations.</p>
""", unsafe_allow_html=True)

# ---- File Upload ----
uploaded_file = st.file_uploader("📁 Upload your CSV file here", type="csv")
if uploaded_file:
    st.session_state.filename = uploaded_file.name
    st.session_state.df = pd.read_csv(uploaded_file)
    st.success(f"✅ {uploaded_file.name} uploaded and loaded!")
    st.dataframe(st.session_state.df, use_container_width=True)

    # --- AI Suggested Questions ---
    if st.button("✨ Try Asking (AI Suggestions)"):
        cols = ", ".join(st.session_state.df.columns)
        prompt = f"Suggest 5 plain-English analytical questions someone might ask based on a dataset with columns: {cols}."
        try:
            res = requests.post(OLLAMA_URL, json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False
            })
            if res.ok:
                suggestions = res.json()["response"]
                st.session_state.suggested_questions = [s.strip("- ").strip() for s in suggestions.splitlines() if s.strip()]
            else:
                st.error("❌ Ollama error during suggestion.")
        except Exception as e:
            st.error(f"⚠️ Suggestion API Error: {e}")

    if st.session_state.suggested_questions:
        st.markdown("#### 💡 Try Asking:")
        for s in st.session_state.suggested_questions:
            if st.button(s, key=f"suggested_{s}"):
                st.session_state.question_input = s

# ---- Educational Mode Toggle ----
edu_mode = st.radio("🎓 Educational Mode:", ["🧑‍💻 Just Give Me the Code", "📘 Explain as a Beginner"], horizontal=True)

# ---- Ask a Question ----
if st.session_state.df is not None:
    question = st.text_input("💬 Ask a question about your data:", value=st.session_state.get("question_input", ""), key="user_question")

    if st.button("🔍 Generate Python Code"):
        if not question:
            st.warning("Please ask a question.")
        else:
            st.session_state.recent_questions.insert(0, question)
            if len(st.session_state.recent_questions) > 5:
                st.session_state.recent_questions = st.session_state.recent_questions[:5]

            # Construct LLM prompt
            columns = ", ".join(st.session_state.df.columns)
            filename = st.session_state.filename

            explain_flag = "and explain it with inline comments suitable for beginners." if "Beginner" in edu_mode else "and keep it concise and professional."

            prompt = f"""You are a helpful data scientist.


1. First, write a complete standalone Python script using pandas that:
- loads a CSV file named '{filename}',
- uses these columns: [{columns}],
- and answers this question: "{question}" {explain_flag}
Store the final result in a variable named `result`.
If charting is involved, make it compatible with Streamlit using `st.pyplot(fig)`.

2. Then give a short version assuming `df` is already loaded.
Label using:
# Standalone Code
# In-App Version
"""

            try:
                response = requests.post(OLLAMA_URL, json={
                    "model": LLM_MODEL,
                    "prompt": prompt,
                    "stream": False
                })

                if response.ok:
                    output = response.json()["response"]
                    full_code, in_app_code = "", ""
                    if "# In-App Version" in output:
                        parts = output.split("# In-App Version")
                        full_code = parts[0].replace("# Standalone Code", "").strip()
                        in_app_code = parts[1].strip()
                    else:
                        full_code = output.strip()

                    full_code = full_code.replace("data.csv", filename)
                    in_app_code = in_app_code.replace("plt.show()", "st.pyplot(plt.gcf())")

                    st.session_state.full_code = full_code
                    st.session_state.in_app_code = patch_missing_imports(in_app_code)
                    st.session_state.explanation = ""
                else:
                    st.error("❌ Ollama generation failed.")
            except Exception as e:
                st.error(f"⚠️ API Error: {e}")

# ---- Show Generated Code ----
if st.session_state.full_code:
    st.markdown("<h3>🧪 Full Standalone Python Script</h3>", unsafe_allow_html=True)
    st.code(st.session_state.full_code, language="python")

if st.session_state.in_app_code:
    st.markdown("<h3>⚙️ In-App Python Code (uses `df`)</h3>", unsafe_allow_html=True)
    st.code(st.session_state.in_app_code, language="python")

    if st.button("▶️ Run In-App Code"):
        local_vars = {"df": st.session_state.df.copy()}
        try:
            exec(st.session_state.in_app_code, {}, local_vars)
            if "result" in local_vars:
                result = local_vars["result"]
                if isinstance(result, pd.DataFrame):
                    st.success("✅ Code ran successfully. Here's the result:")
                    st.dataframe(result, use_container_width=True)
                else:
                    st.write("Result:")
                    st.write(result)
            else:
                st.warning("⚠️ No result returned.")
        except Exception as e:
            st.error(f"❌ Execution error: {e}")

# ---- Explain Code ----
if st.session_state.in_app_code:
    if st.button("🔎 Explain This Code"):
        try:
            res = requests.post(OLLAMA_URL, json={
                "model": LLM_MODEL,
                "prompt": f"""Explain the following Python pandas code line-by-line:
{st.session_state.in_app_code}""",
                "stream": False
            })
            if res.ok:
                st.session_state.explanation = res.json()["response"]
            else:
                st.error("⚠️ Explanation request failed.")
        except Exception as e:
            st.error(f"LLM Explain Error: {e}")

    if st.session_state.explanation:
        st.markdown("### 💡 Code Explanation")
        st.markdown(st.session_state.explanation)

# ---- Recent Questions ----
if st.session_state.recent_questions:
    st.markdown("<h3>📌 Recent Questions</h3>", unsafe_allow_html=True)
    for i, q in enumerate(st.session_state.recent_questions):
        cols = st.columns([8, 1])
        cols[0].markdown(f"- {q}")
        if cols[1].button("❌", key=f"delete_{i}"):
            del st.session_state.recent_questions[i]
            st.experimental_rerun()
