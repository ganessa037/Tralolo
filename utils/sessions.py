import pandas as pd
import streamlit as st

class SessionState:
    _defaults = {
        "df": None,
        "recent_questions": [],
        "full_code": "",
        "in_app_code": "",
        "filename": "",
        "explanation": "",
        "suggested_questions": [],
        "question_input": "",
    }

    @classmethod
    def initialize(cls):
        for key, default in cls._defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @classmethod
    def add_recent_question(cls, question):
        current = cls.get_recent_questions()
        st.session_state["recent_questions"] = [question] + current[:4]

    @classmethod
    def get_columns_as_list(cls):
        df = cls.get_df()
        return df.columns.tolist() if df is not None else []
    
    @classmethod
    def remove_recent_question(cls, index):
        questions = cls.get_recent_questions()
        if 0 <= index < len(questions):
            questions.pop(index)
            st.session_state["recent_questions"] = questions

    # --- Getters ---
    @classmethod
    def get_df(cls):
        return st.session_state.get("df")

    @classmethod
    def get_filename(cls):
        return st.session_state.get("filename")
    
    @classmethod
    def get_columns(cls):
        df = cls.get_df()
        return ", ".join(df.columns) if df is not None else ""
    
    @classmethod
    def get_suggested_questions(cls):
        return st.session_state.get("suggested_questions", [])
    
    @classmethod
    def get_question_input(cls):
        return st.session_state.get("question_input", "")
    
    @classmethod
    def get_recent_questions(cls):
        return st.session_state.get("recent_questions", [])
    
    @classmethod
    def get_full_code(cls):
        return st.session_state.get("full_code", "")
    
    @classmethod
    def get_in_app_code(cls):
        return st.session_state.get("in_app_code", "")
    
    @classmethod
    def get_explanation(cls):
        return st.session_state.get("explanation", "")

    # --- Setters ---
    @classmethod
    def set_df(self, value):
        st.session_state["df"] = value
    
    @classmethod
    def set_filename(cls, value):
        st.session_state["filename"] = value

    @classmethod
    def set_suggested_questions(cls, value):
        st.session_state["suggested_questions"] = value

    @classmethod
    def set_question_input(cls, value):
        st.session_state["question_input"] = value

    @classmethod
    def set_recent_questions(cls, questions):
        st.session_state["recent_questions"] = questions
    
    @classmethod
    def set_full_code(cls, value):
        st.session_state["full_code"] = value

    @classmethod
    def set_in_app_code(cls, value):
        st.session_state["in_app_code"] = value

    @classmethod
    def set_explanation(cls, value):
        st.session_state["explanation"] = value