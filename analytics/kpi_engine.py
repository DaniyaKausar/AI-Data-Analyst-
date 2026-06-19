import pandas as pd
import sqlite3
from config import DB_PATH

def get_all_kpis(table_name: str = "superstore") -> dict:
    """
    Generate all KPIs using trusted hardcoded SQL.
    No AI involved here = 100% accurate numbers.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    kpis = {}
    
    # ── Core Revenue KPIs ──────────────────────────────
    cursor.execute(f"SELECT ROUND(SUM(sales), 2) FROM {table_name}")
    kpis["total_revenue"] = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT COUNT(DISTINCT order_id) FROM {table_name}")
    kpis["total_orders"] = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT COUNT(DISTINCT customer_id) FROM {table_name}")
    kpis["total_customers"] = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT COUNT(DISTINCT product_name) FROM {table_name}")
    kpis["total_products"] = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) FROM {table_name}")
    kpis["avg_order_value"] = cursor.fetchone()[0] or 0

    cursor.execute(f"SELECT ROUND(SUM(sales) / COUNT(DISTINCT customer_id), 2) FROM {table_name}")
    kpis["revenue_per_customer"] = cursor.fetchone()[0] or 0

    # ── Regional KPIs ──────────────────────────────────
    cursor.execute(f"""
        SELECT region, ROUND(SUM(sales), 2) as total
        FROM {table_name}
        GROUP BY region
        ORDER BY total DESC
    """)
    regional = cursor.fetchall()
    kpis["regional_sales"] = {row[0]: row[1] for row in regional}
    kpis["top_region"] = regional[0][0] if regional else "N/A"

    # ── Category KPIs ──────────────────────────────────
    cursor.execute(f"""
        SELECT category, ROUND(SUM(sales), 2) as total
        FROM {table_name}
        GROUP BY category
        ORDER BY total DESC
    """)
    cat = cursor.fetchall()
    kpis["category_sales"] = {row[0]: row[1] for row in cat}
    kpis["top_category"] = cat[0][0] if cat else "N/A"

    # ── Segment KPIs ───────────────────────────────────
    cursor.execute(f"""
        SELECT segment, ROUND(SUM(sales), 2) as total
        FROM {table_name}
        GROUP BY segment
        ORDER BY total DESC
    """)
    seg = cursor.fetchall()
    kpis["segment_sales"] = {row[0]: row[1] for row in seg}
    kpis["top_segment"] = seg[0][0] if seg else "N/A"

    # ── Time KPIs ──────────────────────────────────────
    cursor.execute(f"""
        SELECT order_year, ROUND(SUM(sales), 2)
        FROM {table_name}
        GROUP BY order_year
        ORDER BY order_year
    """)
    yearly = cursor.fetchall()
    kpis["yearly_sales"] = {str(row[0]): row[1] for row in yearly}

    cursor.execute(f"""
        SELECT order_month, ROUND(SUM(sales), 2)
        FROM {table_name}
        GROUP BY order_month
        ORDER BY order_month
    """)
    monthly = cursor.fetchall()
    kpis["monthly_sales"] = {str(row[0]): row[1] for row in monthly}

    # ── Top Products ───────────────────────────────────
    cursor.execute(f"""
        SELECT product_name, ROUND(SUM(sales), 2) as total
        FROM {table_name}
        GROUP BY product_name
        ORDER BY total DESC
        LIMIT 10
    """)
    kpis["top_10_products"] = cursor.fetchall()

    # ── Top Cities ─────────────────────────────────────
    cursor.execute(f"""
        SELECT city, ROUND(SUM(sales), 2) as total
        FROM {table_name}
        GROUP BY city
        ORDER BY total DESC
        LIMIT 5
    """)
    kpis["top_5_cities"] = cursor.fetchall()

    # ── Ship Mode ──────────────────────────────────────
    cursor.execute(f"""
        SELECT ship_mode, COUNT(*) as orders
        FROM {table_name}
        GROUP BY ship_mode
        ORDER BY orders DESC
    """)
    kpis["shipmode_distribution"] = cursor.fetchall()

    conn.close()
    return kpis