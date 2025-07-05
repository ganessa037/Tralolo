# Tralolo: AskMyData AI

Tralolo is an interactive Streamlit app that lets you upload your own CSV data and ask questions in plain English. It uses an Ollama-hosted LLM (like CodeLlama) to generate Python (pandas) code or SQL queries to answer your questions, and can even explain the code line-by-line.

## Features
- **Upload CSV datasets** and preview them instantly
- **Ask questions in English** about your data (e.g., "What is the average revenue by year?")
- **AI-generated Python code** (standalone and in-app versions)
- **Run generated code** directly in the app and see results
- **Get code explanations** (line-by-line, beginner-friendly)
- **AI-suggested questions** based on your dataset
- **Educational mode** for more detailed, commented code
- **Recent questions** history for quick access

## Requirements
- Python 3.7+
- [Streamlit](https://streamlit.io/)
- pandas
- requests
- Ollama running locally with a supported LLM (e.g., CodeLlama)

## Installation
1. Clone this repository or copy `main.py` to your project folder.
2. Install dependencies:
   ```powershell
   pip install streamlit pandas requests
   ```
3. Download and run [Ollama](https://ollama.com/) locally, and pull a model (e.g., `codellama`):
   ```powershell
   ollama run codellama
   ```
   Make sure Ollama is running at `http://localhost:11434` (default).

## Usage
1. Start the Streamlit app:
   ```powershell
   streamlit run main.py
   ```
2. Open the app in your browser (the terminal will show the local URL).
3. Upload a CSV file, ask questions, and interact with the generated code and explanations.

## Customization
- You can change the LLM model by editing the `LLM_MODEL` variable in `main.py`.
- The app can be extended to support SQL generation or other data sources.

## Example Questions
- "Show the top 5 products by sales."
- "Plot the monthly trend of revenue."
- "Which country has the highest average order value?"

---

*Built with ❤️ using Streamlit, pandas, and Ollama LLMs.*
