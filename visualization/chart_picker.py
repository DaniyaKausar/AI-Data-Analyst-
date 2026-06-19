from utils.groq_client import call_groq

def pick_chart_type(user_question: str) -> str:
    """
    AI decides which chart type fits the question.
    Novel feature — Smart Chart Recommender.
    Returns: 'bar' | 'line' | 'pie' | 'map' | 'heatmap' | 'table'
    """
    system_prompt = """You are a data visualization expert.
Given a user's question about business data, decide the best chart type.

Rules:
- Comparisons between categories → bar
- Trends over time → line  
- Part-of-whole / percentages → pie
- Geographic / by state or region → map
- Patterns across two dimensions → heatmap
- Specific numbers / lists → table

Reply with ONLY one word: bar, line, pie, map, heatmap, or table.
No explanation. No punctuation. Just the word."""

    result = call_groq(system_prompt, user_question, temperature=0.0)
    
    valid_types = ["bar", "line", "pie", "map", "heatmap", "table"]
    if result and result.strip().lower() in valid_types:
        return result.strip().lower()
    return "bar"  # safe default