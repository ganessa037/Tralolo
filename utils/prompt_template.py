from enum import Enum

class PromptTemplate(Enum):
    SUGGEST_QUESTIONS ="""List only 5 analytical questions based on these dataset columns: {cols}. 
            Output only the questions in plain bullet points. Do not include any introductory or concluding sentence.
        """

    Python_REVIEW_CODE = """You are a Python expert. Revise the following code.

        Instructions:
        1. Check for syntax or logic errors.
        2. Verify that the column names match the dataset columns: [{cols_str}].
        3. Correct any incorrect or unclear column names using the provided list.
        4. Apply best practices for Python and data analysis.
        5. Ensure the code is clean, safe to run, and uses professional formatting.
        6. Do not include explanations — return only the revised Python code.
        7. Do not define a data loading function; keep `df = df.copy()` as the starting point.
        8. Replace `plt.show()` with `st.pyplot(plt.gcf())` if applicable.

        Code:
        {code}
    """

    SQL_REVIEW_CODE = """You are a SQL expert. Please review and revise the following code.
        Your tasks:
        1. Check for any syntax or logic errors.
        2. Verify that the column names used match the actual dataset columns: [{cols_str}].
        3. If any column names are incorrect or unclear, correct them using the provided column names.
        4. Apply improvements based on SQL and data analysis best practices.
        5. Ensure the code is clean, professional, and safe to execute.
        6. Do not explain — just return the revised, executable SQL code.
        7. Do not define a data loading function; directly to access the dataset.
        Code:
        {code}
    """

    Python_CODE_GENERATION = """You are a Python coding assistant. Your task is to generate Python code to answer the following question:
        - Question: "{question}"
        - Dataset: '{filename}' with columns [{cols}]
        - Educational focus: {explain_flag}

        Instructions:

        Generate only one version of the code based on the educational focus — do not generate both.

        - Always begin your response with: # Educational Level: {explain_flag}

        If the educational focus is "and add beginner-friendly comments":
        - Write the code with clear Python comments explaining each step.
        - Follow a 3-step reasoning structure:
            # STEP 1 - ANALYZE
            # STEP 2 - PLAN
            # STEP 3 - IMPLEMENT
        - Include inline comments to explain code logic.
        - Use comments to guide beginners through the thought process.

        If the educational focus is "a knowledgeable audience":
        - Write clean, professional code with **no comments** at all.
        - Do not include any markdown, `# STEP` labels, or inline explanations.
        - Just return executable Python code.

        Always:
        - Use pandas, matplotlib, seaborn, sklearn, or nltk as needed.
        - Start with: df = df.copy()
        - Clean column names by stripping spaces: df.columns = df.columns.str.strip()
        - If computing correlation:
            - Convert datetime columns using:
                df[col] = pd.to_datetime(df[col], errors='coerce').astype('int64')
            - Detect and encode all non-numeric object columns dynamically:
                object_cols = df.select_dtypes(include='object').columns
                for col in object_cols:
                    df[col] = pd.factorize(df[col])[0]
            - Ensure all columns used in correlation or plotting are numeric
        - Assign the final result to a variable called result.
        - If chart-only, set: result = "Chart displayed".

        Then, provide an "In-App Version":
        - Reuse the same logic already written above (no need to re-import, re-load, or re-process data).
        - Replace only the output and display functions with Streamlit equivalents:
            - st.write() instead of print()
            - st.pyplot() instead of plt.show()
            - nltk.download() if NLTK is used
        - Do not repeat preprocessing or df loading.
        - Always end with: st.write(result)
        - Do not include markdown, comments, or explanation in this section

        Only return valid Python code. No explanations outside the code.
    """

    SQL_CODE_GENERATION = """
        You are a SQL coding assistant. Your task is to generate SQL code to answer the following question:

        - Question: "{question}"
        - Dataset: '{filename}' with columns [{cols}]
        - Educational focus: {explain_flag}

        Your response must include exactly two parts, in this order:

        1. Standalone SQL Query (with comments):
        - Begin with: # Educational Level: {explain_flag}
        - If the educational focus is "and add beginner-friendly comments":
            - Output valid SQL starting at the SELECT clause
            - Use only `--` comments to explain each major clause:
                -- SELECT: explain each selected column
                -- FROM: describe the data source
                -- WHERE: explain filtering logic
                -- GROUP BY: explain grouping logic
                -- ORDER BY: explain sorting logic
            - Do NOT include:
                - Narration or explanation outside of comments
                - Markdown, bullet points, or variable assignments

        - If the educational focus is "a knowledgeable audience":
            - Output raw SQL only with no comments

        2. Clean SQL (no comments):
        - Repeat the same SQL logic without any comments
        - Do not include:
            - Any markdown
            - Any variable assignments like result = ...
            - Any explanation

        General Rules:
        - Use DuckDB/PostgreSQL-compatible SQL
        - Reference the table exactly as '{filename}' (with .csv if present)
        - Output only valid SQL — no markdown, no extra text, no narration
    """
