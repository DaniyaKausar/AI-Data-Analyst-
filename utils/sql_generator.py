import re
from utils.groq_client import call_groq
from sql.database import get_table_schema, get_sample_data

def generate_sql(user_question: str, table_name: str = "superstore") -> dict:
    """
    Convert natural language question to SQL query.
    Returns sql, confidence score, and explanation.
    """
    # Get schema and sample so AI knows the data
    schema = get_table_schema(table_name)
    sample = get_sample_data(table_name, n=3).to_string(index=False)

    system_prompt = f"""You are an expert SQL analyst. 
Your job is to convert natural language questions into SQLite SQL queries.

RULES:
1. Only write SELECT queries. Never use DROP, DELETE, UPDATE, ALTER, INSERT.
2. Always use the table name: {table_name}
3. Use exact column names from the schema below.
4. Return ONLY this JSON format, nothing else:

{{
  "sql": "SELECT ...",
  "confidence": 0.95,
  "explanation": "This query does X by Y..."
}}

SCHEMA:
{schema}

SAMPLE DATA (first 3 rows):
{sample}

IMPORTANT COLUMNS IN THIS DATASET:
- sales: revenue amount
- order_year, order_month: use these for time-based queries (no 'profit' or 'discount' column)
- region, state, city: geographic columns
- category, sub_category, product_name: product columns
- segment: Customer, Corporate, Home Office
- ship_mode: shipping type
"""

    user_message = f"Convert this question to SQL: {user_question}"
    
    raw_response = call_groq(system_prompt, user_message, temperature=0.1)
    
    if not raw_response:
        return {
            "sql": None,
            "confidence": 0.0,
            "explanation": "Failed to connect to Groq API."
        }
    
    # Parse JSON response
    try:
        # Strip markdown code blocks if present
        clean = raw_response.replace("```json", "").replace("```", "").strip()
        import json
        result = json.loads(clean)
        return result
    
    except Exception:
        # Fallback: try to extract SQL directly
        sql_match = re.search(r"SELECT.*?;", raw_response, re.IGNORECASE | re.DOTALL)
        if sql_match:
            return {
                "sql": sql_match.group(0).strip(),
                "confidence": 0.6,
                "explanation": "SQL extracted from response."
            }
        
        return {
            "sql": None,
            "confidence": 0.0,
            "explanation": f"Could not parse response: {raw_response[:200]}"
        }


def explain_results(user_question: str, sql: str, result_summary: str) -> str:
    """
    After running SQL, explain the results in plain English.
    This is the Query Explanation Layer — novel feature.
    """
    system_prompt = """You are a business analyst explaining data results to a non-technical manager.
Be concise, clear, and highlight the most important insight in 2-3 sentences.
Start directly with the insight. No preamble."""

    user_message = f"""
Question asked: {user_question}
SQL that ran: {sql}
Results summary: {result_summary}

Explain what this means for the business in plain English.
"""
    
    return call_groq(system_prompt, user_message, temperature=0.3)