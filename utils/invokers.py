import re
import streamlit as st
from .prompt_template import PromptTemplate
from .sessions import SessionState
from utils.formats import patch_missing_imports
from llm_config import ask_llm_groq, review_code_with_mistral, llm_groq

state = SessionState()

class AIActionInvoker:

    @staticmethod
    def call_llm_groq(prompt: str) -> str:
        return ask_llm_groq(prompt)

    @staticmethod
    def call_llm_mistral(code: str, dataset_columns: list[str], language: str = "Python") -> str:
        return review_code_with_mistral(code, dataset_columns, language)

    @staticmethod
    def get_questions_suggestions():
        prompt = PromptTemplate.SUGGEST_QUESTIONS.value.format(
            cols=state.get_columns(),
        )
        try:
            state.set_suggested_questions(AIActionInvoker.call_llm_groq(prompt))
        except Exception as e:
            st.error(f"Suggestion error: {e}")

    @staticmethod
    def generate_code(question:str, mode:str, language:str):
        explain_flag = ("and add beginner-friendly comments" if mode.startswith("Explain") else "a knowledgeable audience")
        if language == "Python":
            prompt = PromptTemplate.Python_CODE_GENERATION.value.format(
                question=question,
                filename=state.get_filename(),
                cols=state.get_columns(),
                explain_flag=explain_flag
            )
        else: #SQL
            prompt = PromptTemplate.SQL_CODE_GENERATION.value.format(
                question=question,
                filename=state.get_filename(),
                cols=state.get_columns(),
                explain_flag=explain_flag  
        )

        try:
            with st.spinner("🤖 Generating code..."):
                res = AIActionInvoker.call_llm_groq(prompt)
                AIResponseFormatHandler.prep_code(res)

                mistral_review = AIActionInvoker.call_llm_mistral(
                    state.get_full_code(), 
                    state.get_columns_as_list(),
                    language=language
                    
                )
                state.set_in_app_code(mistral_review)
                # print(state.get_in_app_code())

        except Exception as e:
            st.error(f"Code generation error: {e}")


class AIResponseFormatHandler:

    @staticmethod
    def prep_code(res, filename=None):
        if filename is None:
            filename = state.get_filename()

        if isinstance(res, list):
            res = AIResponseFormatHandler.join_lines(res)

        normalized = AIResponseFormatHandler.code_normalizer(res if isinstance(res, str) else "")

        if "# In-App Version" in normalized:
            parts = normalized.split("# In-App Version")
            full = parts[0].replace("# Standalone Code", "").strip()
            in_app = parts[1].strip()
        else:
            full = in_app = normalized.strip()

        if filename:
            full = full.replace("data.csv", filename)
        else:
            st.warning("⚠️ No filename found in session state. Skipping filename replacement.")

        # Additional streamlit-specific patches
        in_app = patch_missing_imports(in_app)
        in_app = re.sub(r'plt\s*\.\s*show\s*\(\s*\)', 'st.pyplot(plt.gcf())', in_app)
        in_app = re.sub(r'print\s*\((.*?)\)', r'st.write(\1)', in_app)
        in_app = re.sub(r'@st\.cache\b', '@st.cache_data', in_app)

        state.set_full_code(full)
        state.set_in_app_code(in_app)
        state.set_explanation("")

    @staticmethod
    def code_normalizer(res: str) -> str:
        # Replace "**Educational Focus: ...**" with "# Educational Focus: ..."
        res = re.sub(
            r'^\*\*(Educational Focus:.*?)\*\*',
            r'# \1',
            res,
            flags=re.MULTILINE
        )

        res = re.sub(
            r'^(.*\bSQL\b.*)$',
            r'# \1',
            res,
            flags=re.MULTILINE | re.IGNORECASE
        )

        # Replace any line containing "In-App" with "# In-App Version"
        res = re.sub(
            r'^.*In-App.*$',
            '# In-App Version',
            res,
            flags=re.MULTILINE
        )

        return res

    @staticmethod
    def join_lines(lines: list[str]) -> str:

        return "\n".join(lines)
