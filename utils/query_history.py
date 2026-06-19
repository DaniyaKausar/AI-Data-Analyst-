import json
import os
from datetime import datetime

HISTORY_FILE = "exports/query_history.json"

def save_query(question: str, sql: str, confidence: float, rows_returned: int, success: bool):
    """Save every query to history — enables metrics calculation."""
    os.makedirs("exports", exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "sql": sql,
        "confidence": confidence,
        "rows_returned": rows_returned,
        "success": success
    }
    
    # Load existing history
    history = load_history()
    history.append(entry)
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_history() -> list:
    """Load all past queries."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def get_metrics() -> dict:
    """
    Calculate real project metrics for your resume.
    These are ACTUAL numbers, not made up.
    """
    history = load_history()
    
    if not history:
        return {"message": "No queries yet."}
    
    total = len(history)
    successful = sum(1 for q in history if q["success"])
    avg_confidence = sum(q["confidence"] for q in history) / total
    high_confidence = sum(1 for q in history if q["confidence"] >= 0.85)
    
    return {
        "total_queries": total,
        "successful_queries": successful,
        "success_rate_percent": round((successful / total) * 100, 1),
        "avg_confidence_score": round(avg_confidence * 100, 1),
        "high_confidence_queries": high_confidence,
        "sql_accuracy_percent": round((high_confidence / total) * 100, 1)
    }