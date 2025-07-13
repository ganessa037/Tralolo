import re
import streamlit as st
from .prompt_template import PromptTemplate
from .sessions import get_columns, get_filename, get_columns_as_list
from main_utils import patch_missing_imports
from llm_config import ask_llm_groq, review_code_with_mistral ,llm_groq

class AIActionInvoker:

    @staticmethod
    def call_llm_groq(prompt: str) -> str:
        return ask_llm_groq(prompt)
    
    @staticmethod
    def call_llm_mistral(code: str, dataset_columns: list[str]) -> str:
        return review_code_with_mistral(code, dataset_columns)

    @staticmethod
    def get_questions_suggestions():
        prompt = PromptTemplate.SUGGEST_QUESTIONS.value.format(
            cols=get_columns(),
        )
        try:
            st.session_state.suggested_questions = AIActionInvoker.call_llm_groq(prompt)
        except Exception as e:
            st.error(f"Suggestion error: {e}")

    @staticmethod
    def generate_code(question:str, mode:str):
        # explain_flag = ("and add beginner-friendly comments" if mode.startswith("Explain") else "and keep it concise and professional.")

        prompt = PromptTemplate.CODE_GENERATION.value.format(
            question=question,
            filename=get_filename(),
            cols=get_columns(),
        )

        try:
            with st.spinner("🤖 Generating code..."):
                res = AIActionInvoker.call_llm_groq(prompt)
                AIResponseFormatHandler.prep_code(res)
                mistral_review = AIActionInvoker.call_llm_mistral(st.session_state.full_code, get_columns_as_list())
                st.session_state.in_app_code = mistral_review
                
        except Exception as e:
            st.error(f"Code generation error: {e}")

class AIResponseFormatHandler:

    @staticmethod
    def prep_code(res, filename=get_filename()):
        if isinstance(res, list):
            res = AIResponseFormatHandler.join_lines(res)

        normalized = AIResponseFormatHandler.code_normalizer(res if isinstance(res, str) else "")
        
        if "# In-App Version" in normalized:
            parts = normalized.split("# In-App Version")
            full = parts[0].replace("# Standalone Code", "").strip()
            in_app = parts[1].strip()
        else:
            full = in_app = normalized.strip()

        # ✅ Replacements
        full = full.replace("data.csv", filename)
        in_app = patch_missing_imports(in_app)
        in_app = re.sub(r'plt\s*\.\s*show\s*\(\s*\)', 'st.pyplot(plt.gcf())', in_app)
        in_app = re.sub(r'@st\.cache\b', '@st.cache_data', in_app)

        # ✅ Save
        st.session_state.full_code = full
        st.session_state.in_app_code = in_app
        st.session_state.explanation = ""

    def code_normalizer(res: str) -> str:
        return (re.sub(r'^\*\*(In-App Version(?: \(Streamlit\))?|Standalone Code)\*\*', 
                       lambda m: f"# {m.group(1)}", res, flags=re.MULTILINE))
    
    def join_lines(lines: list[str]) -> str:
        return ("\n".join(lines))