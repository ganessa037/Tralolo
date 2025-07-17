from enum import Enum

class PromptTemplate(Enum):
    SUGGEST_QUESTIONS ="""List only 5 analytical questions based on these dataset columns: {cols}. 
            Output only the questions in plain bullet points. Do not include any introductory or concluding sentence.
        """

    Python_REVIEW_CODE = """You are a Python expert. Please review and revise the following code.
        Your tasks:
        1. Check for any syntax or logic errors.
        2. Verify that the column names used match the actual dataset columns: [{cols_str}].
        3. If any column names are incorrect or unclear, correct them using the provided column names.
        4. Apply improvements based on Python and data analysis best practices.
        5. Ensure the code is clean, professional, and safe to execute.
        6. Do not explain — just return the revised, executable Python code.
        7. Do not define a data loading function; use `df = df.copy()` directly to access the dataset.
        8. Replace any `plt.show()` with `st.pyplot(plt.gcf())` for Streamlit compatibility if there's any.
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

    Python_CODE_GENERATION = """ You are a Python coding assistant. Think step-by-step:=
        STEP 1 - ANALYZE: What does "{question}" require? What columns from [{cols}] are needed? What's the best approach for '{explain_flag}' level?

        STEP 2 - PLAN: Choose methodology, required libraries (pandas, numpy, matplotlib, seaborn, sklearn, nltk), and output format.

        STEP 3 - IMPLEMENT: Write two code outputs following your analysis:

        1. # Standalone Code
        - Answer: "{question}" using '{filename}' and columns [{cols}]
        - Educational focus: '{explain_flag}'
        - Use logical step-by-step approach
        - Always assign final output to `result`
        - If chart only: `result = "Chart displayed"`

        2. # In-App Version
        - Same logic as standalone but Streamlit-optimized
        - Use `st.pyplot()` instead of `plt.show()`
        - Use `st.write()` instead of `print()`
        - For NLTK: include download commands
        - Always show result with `st.write(result)`
        - No markdown - just executable code

        Return only valid Python code with clear reasoning flow.
        """

    SQL_CODE_GENERATION_SIMPLE = """ You are a SQL coding assistant. Think step-by-step:

        STEP 1 - ANALYZE: What does "{question}" require? What columns from [{cols}] are needed? What's the best SQL approach for '{explain_flag}' level?

        STEP 2 - PLAN: Choose SQL methodology (SELECT, GROUP BY, aggregation, filtering) and query structure for DuckDB compatibility.

        STEP 3 - IMPLEMENT: Write two SQL outputs following your analysis:

        1. # Standalone SQL Query
        - Answer: "{question}" using table '{filename}' and columns [{cols}]
        - Educational focus: '{explain_flag}'
        - Standard SQL syntax (DuckDB/PostgreSQL compatible)
        - Assign to: result = \"\"\"SELECT ... FROM '{filename}' ...\"\"\"

        2. # In-App Version
        - Same query logic for Streamlit app using DuckDB
        - Assign SQL string to variable named `result`
        - No UI code - just executable SQL wrapped in string

        Important:
        - No markdown blocks or explanations
        - No print statements - only assign SQL string to `result`
        - Ensure query references exact table name '{filename}'

        Return only valid SQL code assignments with clear reasoning flow.
        """
