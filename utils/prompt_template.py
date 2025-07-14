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
        7. Do not define a data loading function; use `df = df.copy()` directly to access the dataset.
        8. Replace any `plt.show()` with `st.pyplot(plt.gcf())` for Streamlit compatibility if there's any.
        Code:
        {code}
    """

    Python_CODE_GENERATION = """ You are a Python coding assistant. Return only valid Python code — no markdown, no explanations.
        Write two code outputs:
            1. # Standalone Code
                - Write clean logic to answer: "{question}" using the file '{filename}' and columns [{cols}]
                - Use only common libraries: pandas, numpy, matplotlib, seaborn, sklearn, nltk
                - Always assign the final output (e.g., result DataFrame, numeric value, or message string) to a variable named `result`
                - If displaying a chart or message only, assign `result = "Chart displayed"` or similar

            2. # In-App Version
                - Same as above, but format as a full Streamlit script
                - Use `st.pyplot()` instead of `plt.show()`
                - If using `word_tokenize` or `stopwords`, include:
                    import nltk
                    nltk.download('punkt')
                    nltk.download('stopwords')
                - Always assign something meaningful to `result`
                - The results should be presentable in the app
        """

    SQL_CODE_GENERATION = """
            You are a SQL coding assistant. Your task is to generate only valid SQL code — do not include any markdown, explanations, or extra text.
            You have to understand the "{question}" and the dataset columns: [{cols}] beforehand so you can come up with a SQL query that answers the question.
            Provide two separate outputs:

            1. # Standalone SQL Query
                - Write a clean, readable, and logically correct SQL query that answers the following question: "{question}"
                - Use the table name: '{filename}'
                - Use only the following columns: [{cols}]
                - Ensure the query uses standard SQL syntax (compatible with DuckDB or PostgreSQL — avoid proprietary extensions unless explicitly needed)
                - Assign the final SQL string to a Python variable named `result`, like so:
                
                result = \"\"\"SELECT ... FROM '{filename}' ...\"\"\"

            2. # In-App Version
                - Same query logic as above, but intended for execution inside a Streamlit app using DuckDB
                - Again, assign the SQL string to a variable named `result`
                - Do not include markdown or any UI code — just valid SQL wrapped in a string

            Important:
            - Do not wrap your output in markdown blocks or add any comments unless they are part of the SQL query.
            - Do not include print statements, explanations, or variable outputs — only assign the SQL string to `result`.
            - Always ensure the SQL query is executable directly using DuckDB, and references the exact table name '{filename}'.
        """
