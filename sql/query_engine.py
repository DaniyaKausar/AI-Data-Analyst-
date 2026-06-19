import sqlite3
import pandas as pd
import re
import time
from config import DB_PATH

# These keywords are BLOCKED for safety
DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "ALTER", 
    "INSERT", "TRUNCATE", "CREATE", "REPLACE"
]

def is_safe_query(sql: str) -> tuple[bool, str]:
    """
    Check if SQL query is safe to execute.
    Blocks any destructive operations.
    Returns (is_safe, reason)
    """
    sql_upper = sql.upper()
    
    for keyword in DANGEROUS_KEYWORDS:
        # Use word boundary to avoid false positives
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return False, f"Blocked: '{keyword}' operations are not allowed."
    
    # Must be a SELECT query
    stripped = sql_upper.strip()
    if not stripped.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."
    
    return True, "OK"


def execute_query(sql: str) -> tuple[pd.DataFrame | None, dict]:
    """
    Safely execute SQL and return results + metadata.
    This is the core engine of the project.
    """
    metadata = {
        "sql": sql,
        "success": False,
        "error": None,
        "rows_returned": 0,
        "execution_time_ms": 0
    }
    
    # Safety check first
    is_safe, reason = is_safe_query(sql)
    if not is_safe:
        metadata["error"] = reason
        return None, metadata
    
    # Execute query
    start = time.time()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        
        elapsed = round((time.time() - start) * 1000, 2)
        
        metadata["success"] = True
        metadata["rows_returned"] = len(df)
        metadata["execution_time_ms"] = elapsed
        
        print(f"✅ Query returned {len(df)} rows in {elapsed}ms")
        return df, metadata
    
    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 2)
        metadata["error"] = str(e)
        metadata["execution_time_ms"] = elapsed
        print(f"❌ Query failed: {e}")
        return None, metadata


def get_quick_stats(table_name: str = "superstore") -> dict:
    """
    Pre-built trusted queries for common KPIs.
    These don't go through AI — 100% accurate.
    """
    conn = sqlite3.connect(DB_PATH)
    stats = {}
    
    queries = {
        "total_sales": f"SELECT ROUND(SUM(sales), 2) FROM {table_name}",
        "total_profit": f"SELECT ROUND(SUM(profit), 2) FROM {table_name}",
        "total_orders": f"SELECT COUNT(DISTINCT order_id) FROM {table_name}",
        "total_customers": f"SELECT COUNT(DISTINCT customer_id) FROM {table_name}",
        "avg_discount": f"SELECT ROUND(AVG(discount) * 100, 2) FROM {table_name}",
        "profit_margin": f"SELECT ROUND((SUM(profit) / SUM(sales)) * 100, 2) FROM {table_name}",
    }
    
    cursor = conn.cursor()
    for key, query in queries.items():
        try:
            cursor.execute(query)
            stats[key] = cursor.fetchone()[0]
        except Exception as e:
            stats[key] = None
    
    conn.close()
    return stats