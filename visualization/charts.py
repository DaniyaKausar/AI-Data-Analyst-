import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
from config import DB_PATH

def get_df(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def chart_sales_by_region() -> go.Figure:
    """Bar chart — Sales by Region."""
    df = get_df("SELECT region, ROUND(SUM(sales),2) as total_sales FROM superstore GROUP BY region ORDER BY total_sales DESC")
    fig = px.bar(
        df, x="region", y="total_sales",
        title="💰 Total Sales by Region",
        color="region",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(showlegend=False, xaxis_title="Region", yaxis_title="Sales ($)")
    return fig


def chart_sales_by_category() -> go.Figure:
    """Pie chart — Sales by Category."""
    df = get_df("SELECT category, ROUND(SUM(sales),2) as total_sales FROM superstore GROUP BY category")
    fig = px.pie(
        df, names="category", values="total_sales",
        title="📦 Revenue Split by Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def chart_sales_by_segment() -> go.Figure:
    """Bar chart — Sales by Customer Segment."""
    df = get_df("SELECT segment, ROUND(SUM(sales),2) as total_sales FROM superstore GROUP BY segment ORDER BY total_sales DESC")
    fig = px.bar(
        df, x="segment", y="total_sales",
        title="👥 Sales by Customer Segment",
        color="segment",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(showlegend=False)
    return fig


def chart_yearly_trend() -> go.Figure:
    """Line chart — Year over Year Sales Trend."""
    df = get_df("SELECT order_year, ROUND(SUM(sales),2) as total_sales FROM superstore GROUP BY order_year ORDER BY order_year")
    fig = px.line(
        df, x="order_year", y="total_sales",
        title="📈 Year-over-Year Sales Trend",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#00CC96"]
    )
    fig.update_layout(xaxis_title="Year", yaxis_title="Sales ($)")
    fig.update_traces(line=dict(width=3), marker=dict(size=10))
    return fig


def chart_monthly_trend() -> go.Figure:
    """Line chart — Monthly Sales Pattern."""
    df = get_df("SELECT order_month, ROUND(SUM(sales),2) as total_sales FROM superstore GROUP BY order_month ORDER BY order_month")
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    df["month_name"] = df["order_month"].apply(lambda x: months[int(x)-1])
    fig = px.line(
        df, x="month_name", y="total_sales",
        title="📅 Monthly Sales Pattern",
        markers=True,
        color_discrete_sequence=["#EF553B"]
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
    return fig


def chart_top_products() -> go.Figure:
    """Horizontal bar — Top 10 Products by Sales."""
    df = get_df("""
        SELECT product_name, ROUND(SUM(sales),2) as total_sales
        FROM superstore GROUP BY product_name
        ORDER BY total_sales DESC LIMIT 10
    """)
    # Shorten long product names
    df["product_name"] = df["product_name"].str[:40]
    fig = px.bar(
        df, x="total_sales", y="product_name",
        orientation="h",
        title="🏆 Top 10 Products by Revenue",
        color="total_sales",
        color_continuous_scale="Blues",
        text_auto=True
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    return fig


def chart_top_states() -> go.Figure:
    """Choropleth map — Sales by US State."""
    df = get_df("SELECT state, ROUND(SUM(sales),2) as total_sales FROM superstore GROUP BY state")
    fig = px.choropleth(
        df,
        locations="state",
        locationmode="USA-states",
        color="total_sales",
        scope="usa",
        title="🗺️ Sales Heatmap by State",
        color_continuous_scale="Viridis",
        labels={"total_sales": "Sales ($)"}
    )
    return fig


def chart_ship_mode() -> go.Figure:
    """Donut chart — Shipping Mode Distribution."""
    df = get_df("SELECT ship_mode, COUNT(*) as orders FROM superstore GROUP BY ship_mode ORDER BY orders DESC")
    fig = px.pie(
        df, names="ship_mode", values="orders",
        title="🚚 Shipping Mode Distribution",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    return fig


def chart_sales_heatmap() -> go.Figure:
    """Heatmap — Sales by Month and Year."""
    df = get_df("""
        SELECT order_year, order_month, ROUND(SUM(sales),2) as total_sales
        FROM superstore GROUP BY order_year, order_month
        ORDER BY order_year, order_month
    """)
    pivot = df.pivot(index="order_year", columns="order_month", values="total_sales")
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot.columns = [months[int(m)-1] for m in pivot.columns]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=[str(y) for y in pivot.index.tolist()],
        colorscale="YlOrRd",
        text=pivot.values.round(0),
        texttemplate="%{text:,.0f}",
    ))
    fig.update_layout(title="🔥 Sales Heatmap (Year × Month)")
    return fig


def chart_sub_category() -> go.Figure:
    """Bar chart — Sales by Sub-Category."""
    df = get_df("""
        SELECT sub_category, ROUND(SUM(sales),2) as total_sales
        FROM superstore GROUP BY sub_category
        ORDER BY total_sales DESC
    """)
    fig = px.bar(
        df, x="sub_category", y="total_sales",
        title="📊 Sales by Sub-Category",
        color="total_sales",
        color_continuous_scale="Teal",
        text_auto=True
    )
    fig.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    return fig