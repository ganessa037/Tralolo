# MyQuery.AI - NLP to Code for Data Analysis

An AI-powered web tool that converts natural language questions into executable Python/SQL code for instant data analysis.

## What it does
- Upload CSV datasets 
- Ask questions in plain English (e.g., "Show me total sales by month")
- Get AI-generated Python/SQL code
- See results as tables or visualizations
- Code explanations for learning

## Tech Stack
- **Frontend**: Streamlit
- **AI Models**: Groq (Llama3-70B), Mistral
- **Data Processing**: Pandas, SQLite
- **Visualization**: Matplotlib, Seaborn

## Quick Start
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   - Get free API key from [Groq Console](https://console.groq.com/)
   - Create `.env` file:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```

3. **Run the app:**
   ```bash
   streamlit run main.py
   ```

4. **Start analyzing:**
   - Upload your CSV file
   - Ask questions about your data
   - Get instant code and results!

## Example Questions
- "What's the average sales by category?"
- "Show me a trend chart of monthly revenue"
- "Which products have the highest profit margin?"

---
*Built with Streamlit & Groq LLMs*