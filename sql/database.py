import sqlite3
import pandas as pd
import os
from config import DB_PATH, TABLE_NAME

def get_connection():
    """Get SQLite database connection."""
    os.makedirs("sql", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def load_dataframe_to_db(df: pd.DataFrame, table_name: str = TABLE_NAME) -> dict:
    """
    Insert cleaned DataFrame into SQLite database.
    Returns a report of what was inserted.
    """
    conn = get_connection()
    
    # Write dataframe to SQL table (replace if exists)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    # Verify insertion
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    conn.close()
    
    report = {
        "table_name": table_name,
        "rows_inserted": row_count,
        "columns": columns,
        "db_path": DB_PATH
    }
    
    print(f"✅ Database ready: {row_count} rows in '{table_name}'")
    return report


def get_table_schema(table_name: str = TABLE_NAME) -> str:
    """
    Return schema as a string — this gets sent to Groq
    so the AI knows what columns exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    conn.close()
    
    schema_lines = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        schema_lines.append(f"  {col_name} ({col_type})")
    
    schema = f"Table: {table_name}\nColumns:\n" + "\n".join(schema_lines)
    return schema


def get_sample_data(table_name: str = TABLE_NAME, n: int = 3) -> pd.DataFrame:
    """Return sample rows — helps AI understand data format."""
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT {n}", conn)
    conn.close()
    return df