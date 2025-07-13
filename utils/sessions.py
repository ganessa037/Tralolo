import streamlit as st

def initialize_state():
    for key in ["df", "recent_questions", "full_code", "in_app_code",
            "filename", "explanation", "suggested_questions", "question_input"]:
        
        if key not in st.session_state:
            if key == "df":
                st.session_state[key] = None
            elif "questions" in key:
                st.session_state[key] = []
            else:
                st.session_state[key] = ""

def get_columns():
    return ", ".join(st.session_state.df.columns)

def get_columns_as_list():
    return (st.session_state.df.columns.tolist())

def get_filename():
    if "filename" not in st.session_state:
        st.session_state.filename = ""
    return st.session_state.filename