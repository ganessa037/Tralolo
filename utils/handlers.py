from matplotlib import pyplot as plt
import nltk
import warnings
import numpy as np
import streamlit as st
import pandas as pd
import seaborn as sns
from nltk.corpus import stopwords
from .sessions import SessionState
import duckdb

state = SessionState()

# --- nltk setup, ensure that its downloaded when needed, need to debug later ---
nltk.download('punkt')
nltk.download('stopwords')

class FileHandler:
    def upload_files():
        with st.sidebar:
            st.title("📊 Data Assistant")
            uploaded_file = st.file_uploader("Upload your CSV file here", type="csv")
            if uploaded_file:
                state.set_filename(uploaded_file.name)
                state.set_df(pd.read_csv(uploaded_file))
                st.success(f"✅ {uploaded_file.name} uploaded!")

class ExecutionHandler: 
    def execute_code(in_app,language):
        if language == "SQL":
            try:
                # Get the DataFrame and original filename
                df = state.get_df()
                filename = state.get_filename() 
                table_name = filename.replace(".csv", "").replace(" ", "_")  # sanitize table name

                # Connect and register table with original file name (no .csv)
                conn = duckdb.connect()
                conn.register(table_name, df)

                # Execute the query
                query = in_app.strip()
                result_df = conn.execute(query).fetchdf()

                st.dataframe(result_df)
                st.success("✅ SQL query ran successfully.")
                conn.close()
            except Exception as e:
                st.error(f"SQL run error: {e}")
        else:
            local = {
                "df": state.get_df().copy(),
                "pd": pd,
                "np": np,
                "plt": plt,
                "sns": sns,
                "nltk": nltk,
                "st": st,
                # "word_tokenize": word_tokenize,
                "stopwords": stopwords,
                "stopwords_words": list(stopwords.words("english")),
                "__builtins__": __builtins__,
            }

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=DeprecationWarning)
                    exec(in_app, local, local)

                func_candidates = [v for v in local.values() if callable(v)]
                if len(func_candidates) == 1:
                    func_candidates[0]()

                if "result" in local:
                    st.success("✅ Code ran successfully.")

            except Exception as e:
                st.error(f"Run error: {e}")



