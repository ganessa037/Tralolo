# main.py
import re
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from llm_config import llm_groq
from utils.sessions import SessionState
from utils.handlers import FileHandler, ExecutionHandler
from utils.invokers import AIActionInvoker

state = SessionState()

# --- Page Setup ---
st.set_page_config(page_title="AskMyData AI", layout="wide")

# --- Initialize session state, to save the states for rerun ---
state.initialize()

# --- file upload, appear in sidebar ---
FileHandler.upload_files()

# --- Main UI ---
st.markdown("<h1>Welcome to your Data Assistant!</h1>", unsafe_allow_html=True)
st.write("Ask questions about your data — I'll generate Python code and explain it!")


if state.get_df() is not None:
    st.dataframe(state.get_df().head(10))

    # Global SQLite connection object (I don't know where to put this, so I put it here)
    if "sqlite_conn" not in st.session_state:
        st.session_state.sqlite_conn = None


    # --- Suggest questions ---
    if st.button("✨ Try Asking (AI Suggestions)"):
        AIActionInvoker.get_questions_suggestions()

    # --- Show suggested questions ---
    for i, s in enumerate(state.get_suggested_questions()):
        if s.strip():
            if st.button(s, key=f"suggestion_{i}"):
                state.set_question_input(s)

     # --- Inputs for code generation ---
    st.divider()
    mode = st.radio("🎓 Educational Mode", ["Just Code", "Explain for Beginners"], horizontal=True)
    question = st.text_input("💬 Ask your question:", value=state.get_question_input() or "")
    language = st.radio("🗣️ Language", ["Python", "SQL"], horizontal=True)

    if st.button("🔍 Submit"):
        if not question:
            st.warning("Ask something!")
        else:
            state.set_question_input(question) 
            state.add_recent_question(question)
            AIActionInvoker.generate_code(question, mode, language)

# --- Display outputs ---
if state.get_full_code() != "":
    st.markdown("### 🧪 Standalone Code (for integration)")
    st.code(state.get_full_code(), "python")

if state.get_in_app_code() != "":
    st.markdown("### ⚙️ Full Script (Streamlit Compatible)")
    in_app = state.get_in_app_code()
    in_app = re.sub(r'pd\.read_csv\s*\((?:[^)(]+|\([^)]*\))*\)', "df.copy()", in_app)
    in_app = re.sub(r'df\s*=\s*pd\.DataFrame\s*\(\s*\)', "df = df.copy()", in_app)
    in_app = re.sub(r'set\s*\(\s*stopwords_words\s*\)', "stopwords_words", in_app)
    st.code(in_app, "python")
    
    if st.button("▶️ Run In-App Code"):
        ExecutionHandler.execute_code(in_app, language)

    if st.button("🔎 Explain Code"):
        try:
            if language == "Python":
                prompt = f"Explain this Python pandas code line‑by‑line:\n{in_app}"
            else:
                prompt = f"Explain this SQL code line‑by‑line:\n{in_app}"
            state.set_explanation(llm_groq.invoke(prompt).content)
        except Exception as e:
            st.error(f"Explain error: {e}")

    if state.get_explanation():
        st.markdown("### 💡 Explanation")
        st.markdown(state.get_explanation())
        
        

# --- Helper: Detect column types ---
def get_column_types(df):
    numerical = df.select_dtypes(include=['number']).columns.tolist()
    categorical = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    datetime = df.select_dtypes(include=['datetime64', 'datetime']).columns.tolist()
    return numerical, categorical, datetime

# --- AI-Driven Visualization Based on User Question ---
if state.get_df() is not None:
    st.divider()
    st.markdown("### :bar_chart: Custom Visualization")

    df = state.get_df().copy()

    chart_type = st.selectbox("Select chart type", [
        "Histogram", "Bar Chart", "Line Chart", "Scatter Plot", "Heatmap"])

    question_for_plot = state.get_question_input()

    st.markdown(f"Using your question: **{question_for_plot}**")

    if st.button(":bar_chart: Generate Visualization"):

        columns_list = df.columns.tolist()

        vis_prompt = f"""
        You are a helpful Python assistant that creates data visualizations using matplotlib or seaborn in Streamlit.

        The user asked: '{question_for_plot}'
        They selected: '{chart_type}'

        Here are the available DataFrame columns: {columns_list}

        Instructions:
        - Do NOT combine numerical columns into strings (e.g., avoid 'rpm-torque' keys)
        - Use numeric columns as-is for axes, especially when analyzing correlations
        - If question implies correlation, use a seaborn.heatmap on a correlation matrix (df.corr())
        - If the question involves days, months, or datetime grouping, always convert columns like df["Date"] using pd.to_datetime(df["Date"], errors="coerce")
        - If the question is about counts by category, group appropriately using groupby
        - Automatically select appropriate columns for x and y based on the question
        - Create the chart using this structure:

            fig, ax = plt.subplots()
            # your charting code here using ax
            st.pyplot(fig)

        - Do NOT include print statements, comments, or explanations
        - Assume df = df.copy() is already defined
        """


        try:
            vis_code = llm_groq.invoke(vis_prompt).content
            if isinstance(vis_code, list):
                vis_code = "\n".join(vis_code)

            vis_code = re.sub(r"```(?:python)?", "", vis_code).strip("`")
            vis_code = re.sub(r"\bst\.pyplot\s*\(\s*\)", "st.pyplot(fig)", vis_code)
            if "fig, ax = plt.subplots()" not in vis_code:
                vis_code = "fig, ax = plt.subplots()\n" + vis_code

            local = {"df": df.copy(), "st": st, "plt": plt, "sns": sns, "pd": pd}

            with st.spinner("Generating chart..."):
                exec(vis_code, {}, local)

        except Exception as e:
            st.error(f"Visualization error: {e}")

# --- Recent questions ---
if state.get_recent_questions() != []:
    st.markdown("### 📌 Recent Questions")
    for i, q in enumerate(state.get_recent_questions()):
        cols = st.columns([8, 1])
        cols[0].write(f"- {q}")
        if cols[1].button("❌", key=f"delete-{i}"):
            state.remove_recent_question(i)
            st.experimental_rerun()