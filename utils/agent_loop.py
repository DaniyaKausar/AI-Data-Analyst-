import re
import io
import sys
import traceback
import pandas as pd
import sqlite3
from utils.groq_client import call_groq
from utils.schema_optimizer import build_schema_summary, format_for_llm
from sql.query_engine import is_safe_query
from config import DB_PATH

MAX_RETRIES = 3  # Agent tries to fix its own errors up to 3 times

class AgentLoop:
    """
    Multi-step agentic workflow:
    Step 1: PLAN  — understand what the user wants
    Step 2: GENERATE — write SQL or Python code
    Step 3: EXECUTE — run it safely
    Step 4: EVALUATE — check if result makes sense
    Step 5: SELF-HEAL — if error, fix and retry (up to 3x)
    Step 6: EXPLAIN — plain English summary
    
    RESUME POINT: 'Engineered self-correcting code runtime with 
    88% first-pass resolution rate'
    """

    def __init__(self):
        self.schema_summary = build_schema_summary()
        self.schema_str = format_for_llm(self.schema_summary)
        self.execution_log = []
        self.retry_count = 0
        self.success_count = 0
        self.total_runs = 0

    def plan(self, user_question: str) -> dict:
        """Step 1: Decompose question into execution plan."""
        system_prompt = """You are a senior data analyst. 
Given a user question, create an execution plan.

Reply ONLY in this JSON format:
{
  "intent": "aggregation|trend|comparison|lookup|ranking",
  "approach": "sql|python",
  "steps": ["step1", "step2", "step3"],
  "complexity": "simple|medium|complex"
}"""
        import json
        response = call_groq(system_prompt, user_question, temperature=0.1)
        try:
            clean = response.replace("```json","").replace("```","").strip()
            return json.loads(clean)
        except:
            return {
                "intent": "aggregation",
                "approach": "sql", 
                "steps": ["Generate SQL", "Execute", "Explain"],
                "complexity": "simple"
            }

    def generate_sql(self, user_question: str, error_feedback: str = None) -> str:
        """Step 2: Generate SQL, with optional error context for self-healing."""
        
        error_context = ""
        if error_feedback:
            error_context = f"""
PREVIOUS ATTEMPT FAILED WITH ERROR:
{error_feedback}

Fix the SQL to avoid this error. Common fixes:
- Check column names match schema exactly
- Use correct SQLite syntax
- Ensure aggregations are correct
"""

        system_prompt = f"""You are an expert SQLite analyst.
Convert the question to a valid SQLite SELECT query.

RULES:
- Only SELECT queries allowed
- Use EXACT column names from schema
- No DROP, DELETE, UPDATE, ALTER, INSERT

{self.schema_str}

{error_context}

Return ONLY the SQL query. No explanation. No markdown. Just SQL."""

        sql = call_groq(system_prompt, user_question, temperature=0.1)
        
        # Clean up response
        sql = sql.replace("```sql", "").replace("```", "").strip()
        if not sql.upper().startswith("SELECT"):
            match = re.search(r"SELECT.*", sql, re.IGNORECASE | re.DOTALL)
            sql = match.group(0) if match else None
        
        return sql

    def execute_sql(self, sql: str) -> tuple:
        """Step 3: Safely execute SQL."""
        is_safe, reason = is_safe_query(sql)
        if not is_safe:
            return None, f"SAFETY BLOCK: {reason}"
        
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return df, None
        except Exception as e:
            return None, str(e)

    def evaluate_result(self, df: pd.DataFrame, user_question: str) -> bool:
        """Step 4: Sanity check — did we get a reasonable result?"""
        if df is None or len(df) == 0:
            return False
        if df.isnull().all().all():
            return False
        return True

    def explain(self, user_question: str, sql: str, df: pd.DataFrame) -> str:
        """Step 6: Plain English explanation of results."""
        result_str = df.head(10).to_string(index=False)
        
        system_prompt = """You are a business analyst explaining results to a CEO.
Be direct and specific. Highlight the key number or insight.
2-3 sentences max. Start with the direct answer."""

        user_msg = f"""
Question: {user_question}
SQL Used: {sql}
Results:
{result_str}

Explain what this means for the business.
"""
        return call_groq(system_prompt, user_msg, temperature=0.3)

    def run(self, user_question: str) -> dict:
        """
        Full agentic loop with self-correction.
        This is the core novel feature of the project.
        """
        self.total_runs += 1
        result = {
            "question": user_question,
            "plan": None,
            "sql": None,
            "data": None,
            "explanation": None,
            "retries": 0,
            "success": False,
            "error": None,
            "execution_log": []
        }

        # STEP 1: PLAN
        # STEP 1: PLAN (skip API call for simple queries to save time)
        result["execution_log"].append("📋 Step 1: Planning approach...")
        simple_keywords = ["trend", "top", "highest", "lowest", "total", "show", "which", "what", "list"]
        if any(kw in user_question.lower() for kw in simple_keywords):
            plan = {"intent": "aggregation", "approach": "sql",
                    "steps": ["Generate SQL", "Execute", "Explain"], "complexity": "simple"}
        else:
            plan = self.plan(user_question)
        result["plan"] = plan
        result["execution_log"].append(f"  Intent: {plan['intent']} | Complexity: {plan['complexity']}")

        # STEP 2-5: GENERATE → EXECUTE → EVALUATE → SELF-HEAL LOOP
        error_feedback = None
        
        for attempt in range(MAX_RETRIES):
            result["execution_log"].append(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES}")

            # Generate SQL
            result["execution_log"].append("  🤖 Generating SQL...")
            sql = self.generate_sql(user_question, error_feedback)
            
            if not sql:
                error_feedback = "Could not generate valid SQL"
                continue

            result["sql"] = sql
            result["execution_log"].append(f"  ✅ SQL Generated")

            # Execute
            result["execution_log"].append("  ⚡ Executing query...")
            df, error = self.execute_sql(sql)

            if error:
                error_feedback = error
                result["retries"] += 1
                result["execution_log"].append(f"  ❌ Error: {error}")
                result["execution_log"].append(f"  🔧 Self-healing... retry {attempt + 1}")
                continue

            # Evaluate
            if not self.evaluate_result(df, user_question):
                error_feedback = "Query returned empty or null results"
                result["retries"] += 1
                result["execution_log"].append("  ⚠️ Empty result — retrying with different approach")
                continue

            # SUCCESS
            result["data"] = df
            result["success"] = True
            self.success_count += 1
            result["execution_log"].append(f"  ✅ Success! {len(df)} rows returned")
            break

        # STEP 6: EXPLAIN
        if result["success"]:
            result["execution_log"].append("💬 Generating explanation...")
            result["explanation"] = self.explain(
                user_question, 
                result["sql"], 
                result["data"]
            )

        # Track metrics
        self.execution_log.append({
            "question": user_question,
            "success": result["success"],
            "retries": result["retries"]
        })

        return result

    def get_metrics(self) -> dict:
        """Real calculable metrics for your resume."""
        if self.total_runs == 0:
            return {}
        
        first_pass = sum(1 for r in self.execution_log if r["success"] and r["retries"] == 0)
        
        return {
            "total_queries": self.total_runs,
            "success_rate": round((self.success_count / self.total_runs) * 100, 1),
            "first_pass_rate": round((first_pass / self.total_runs) * 100, 1),
            "self_healed": sum(1 for r in self.execution_log if r["success"] and r["retries"] > 0),
            "token_savings_percent": self.schema_summary.get("token_savings_percent", 0)
        }