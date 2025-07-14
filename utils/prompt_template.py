from enum import Enum

class PromptTemplate(Enum):
    SUGGEST_QUESTIONS ="""List only 5 analytical questions based on these dataset columns: {cols}. 
            Output only the questions in plain bullet points. Do not include any introductory or concluding sentence.
        """

    REVIEW_CODE = """You are a Python expert. Please review and revise the following code.
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

    CODE_GENERATION = """ You are a Python coding assistant. Return only valid Python code — no markdown, no explanations.
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
        """