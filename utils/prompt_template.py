from enum import Enum

class PromptTemplate(Enum):
    SUGGEST_QUESTIONS ="""List only 5 analytical questions based on these dataset columns: {cols}. 
            Output only the questions in plain bullet points. Do not include any introductory or concluding sentence.
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