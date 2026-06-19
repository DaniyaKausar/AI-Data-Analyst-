from analytics.kpi_engine import get_all_kpis
from utils.groq_client import call_groq
import json

def generate_rule_based_recommendations(kpis: dict) -> list[str]:
    """
    Rule-based recommendations — fast, no AI needed.
    Always runs even without internet.
    """
    recs = []
    regional = kpis["regional_sales"]
    total = sum(regional.values())

    # Find underperforming regions
    for region, sales in regional.items():
        pct = (sales / total) * 100
        if pct < 15:
            recs.append(
                f"⚠️ {region} region contributes only {pct:.1f}% of revenue. "
                f"Consider targeted marketing campaigns or discount strategies."
            )

    # AOV insight
    aov = kpis["avg_order_value"]
    if aov < 300:
        recs.append(
            f"💡 Average Order Value is ${aov:.2f}. "
            f"Implement bundle deals or upsell strategies to increase AOV above $300."
        )
    else:
        recs.append(
            f"✅ Strong Average Order Value of ${aov:.2f}. "
            f"Focus on retaining high-value customers."
        )

    # Top category
    top_cat = kpis["top_category"]
    recs.append(
        f"🏆 {top_cat} is the top revenue category. "
        f"Prioritize inventory and promotions for this category."
    )

    # Segment insight
    segment = kpis["segment_sales"]
    top_seg = max(segment, key=segment.get)
    recs.append(
        f"👥 {top_seg} segment drives the most revenue. "
        f"Develop loyalty programs targeting this segment."
    )

    # YoY growth
    yearly = kpis["yearly_sales"]
    years = sorted(yearly.keys())
    if len(years) >= 2:
        growth = ((yearly[years[-1]] - yearly[years[-2]]) / yearly[years[-2]]) * 100
        if growth < 5:
            recs.append(
                f"📉 Revenue growth was only {growth:.1f}% last year. "
                f"Explore new customer acquisition channels."
            )
        else:
            recs.append(
                f"📈 Revenue grew {growth:.1f}% YoY. "
                f"Scale current strategies to maintain momentum."
            )

    return recs


def generate_ai_recommendations(kpis: dict) -> str:
    """
    AI-powered executive recommendations using Groq.
    Novel feature — combines KPIs with LLM reasoning.
    """
    kpi_summary = f"""
Total Revenue: ${kpis['total_revenue']:,.2f}
Total Orders: {kpis['total_orders']}
Total Customers: {kpis['total_customers']}
Avg Order Value: ${kpis['avg_order_value']:,.2f}
Top Region: {kpis['top_region']}
Top Category: {kpis['top_category']}
Top Segment: {kpis['top_segment']}
Regional Sales: {kpis['regional_sales']}
Category Sales: {kpis['category_sales']}
Yearly Sales: {kpis['yearly_sales']}
"""

    system_prompt = """You are a senior business consultant presenting to a CEO.
Analyze the KPI data and provide exactly 5 strategic recommendations.
Each recommendation must:
- Start with an emoji
- Be specific with numbers from the data
- Include a clear action item
- Be 2 sentences max

Format as a numbered list. Be direct and executive-level."""

    user_message = f"Based on these KPIs, give 5 strategic business recommendations:\n{kpi_summary}"

    return call_groq(system_prompt, user_message, temperature=0.4)