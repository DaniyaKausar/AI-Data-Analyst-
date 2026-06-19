from analytics.kpi_engine import get_all_kpis

def generate_insights(kpis: dict = None) -> list[dict]:
    """
    Auto-generate business insights from KPI data.
    Returns list of insight dicts with title, value, type.
    This is 100% rule-based = always accurate.
    """
    if kpis is None:
        kpis = get_all_kpis()

    insights = []
    total_revenue = kpis["total_revenue"]

    # ── Regional Insights ──────────────────────────────
    regional = kpis["regional_sales"]
    total_reg = sum(regional.values())

    for region, sales in regional.items():
        pct = round((sales / total_reg) * 100, 1)
        insights.append({
            "type": "regional",
            "title": f"{region} Region Revenue Share",
            "value": f"${sales:,.0f} ({pct}% of total)",
            "raw_value": pct,
            "region": region
        })

    # ── Top Region Alert ───────────────────────────────
    top_region = kpis["top_region"]
    top_sales = regional[top_region]
    insights.append({
        "type": "highlight",
        "title": "🏆 Top Performing Region",
        "value": f"{top_region} leads with ${top_sales:,.0f} in revenue",
        "raw_value": top_sales
    })

    # ── Category Insights ──────────────────────────────
    category = kpis["category_sales"]
    total_cat = sum(category.values())

    for cat, sales in category.items():
        pct = round((sales / total_cat) * 100, 1)
        insights.append({
            "type": "category",
            "title": f"{cat} Category Share",
            "value": f"${sales:,.0f} ({pct}% of revenue)",
            "raw_value": pct
        })

    # ── Segment Insights ───────────────────────────────
    segment = kpis["segment_sales"]
    total_seg = sum(segment.values())

    for seg, sales in segment.items():
        pct = round((sales / total_seg) * 100, 1)
        insights.append({
            "type": "segment",
            "title": f"{seg} Segment",
            "value": f"${sales:,.0f} ({pct}% of revenue)",
            "raw_value": pct
        })

    # ── Year-over-Year Growth ──────────────────────────
    yearly = kpis["yearly_sales"]
    years = sorted(yearly.keys())

    if len(years) >= 2:
        for i in range(1, len(years)):
            prev = yearly[years[i-1]]
            curr = yearly[years[i]]
            growth = round(((curr - prev) / prev) * 100, 1)
            emoji = "📈" if growth > 0 else "📉"
            insights.append({
                "type": "growth",
                "title": f"{emoji} YoY Growth {years[i-1]}→{years[i]}",
                "value": f"{'+' if growth > 0 else ''}{growth}% (${curr:,.0f})",
                "raw_value": growth
            })

    # ── Avg Order Value ────────────────────────────────
    insights.append({
        "type": "kpi",
        "title": "💰 Average Order Value",
        "value": f"${kpis['avg_order_value']:,.2f} per order",
        "raw_value": kpis["avg_order_value"]
    })

    insights.append({
        "type": "kpi",
        "title": "👤 Revenue Per Customer",
        "value": f"${kpis['revenue_per_customer']:,.2f}",
        "raw_value": kpis["revenue_per_customer"]
    })

    return insights