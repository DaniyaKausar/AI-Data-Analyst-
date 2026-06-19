import streamlit as st
import pandas as pd
import os
from config import APP_TITLE, APP_ICON, DB_PATH


# ── Page Config ────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background: #f0f2f6;
        padding: 0.8rem;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin: 0.3rem 0;
    }
    .rec-box {
        background: #e8f5e9;
        padding: 0.8rem;
        border-left: 4px solid #4caf50;
        border-radius: 5px;
        margin: 0.3rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Initialize Session State ───────────────────────────
if "db_loaded" not in st.session_state:
    st.session_state.db_loaded = False
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "kpis" not in st.session_state:
    st.session_state.kpis = None


# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=80)
    st.title("InsightIQ")
    st.caption("AI Business Intelligence Assistant")
    st.divider()

    st.subheader("📂 Load Dataset")
    use_default = st.checkbox("Use Superstore Dataset", value=True)

    uploaded_file = None
    if not use_default:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel",
            type=["csv", "xlsx", "xls"]
        )

    load_btn = st.button("🚀 Load & Analyze", use_container_width=True, type="primary")

    st.divider()
    st.subheader("⚙️ Settings")
    show_sql = st.toggle("Show Generated SQL", value=True)
    show_confidence = st.toggle("Show Confidence Score", value=True)
    show_explanation = st.toggle("Show AI Explanation", value=True)

    st.divider()
    st.caption("Built with Groq + LLaMA 3 + SQLite")


# ── Load Data Function ─────────────────────────────────
def load_and_setup(filepath_or_file):
    from data.loader import load_file
    from data.cleaner import clean_dataframe
    from data.profiler import generate_profile
    from sql.database import load_dataframe_to_db

    with st.spinner("Loading data..."):
        if isinstance(filepath_or_file, str):
            df = load_file(filepath_or_file)
        else:
            ext = filepath_or_file.name.split(".")[-1]
            temp_path = f"temp_upload.{ext}"
            with open(temp_path, "wb") as f:
                f.write(filepath_or_file.read())
            df = load_file(temp_path)
            os.remove(temp_path)

        df, clean_report = clean_dataframe(df)
        profile = generate_profile(df)
        db_report = load_dataframe_to_db(df)

    return df, clean_report, profile, db_report


# ── Handle Load Button ─────────────────────────────────
if load_btn:
    try:
        if use_default:
            df, clean_report, profile, db_report = load_and_setup("clean_superstore.csv")
        elif uploaded_file:
            df, clean_report, profile, db_report = load_and_setup(uploaded_file)
        else:
            st.sidebar.error("Please upload a file or use default dataset.")
            st.stop()

        st.session_state.df = df
        st.session_state.db_loaded = True
        st.session_state.profile = profile
        st.session_state.clean_report = clean_report

        # Pre-load KPIs
        from analytics.kpi_engine import get_all_kpis
        st.session_state.kpis = get_all_kpis()

        st.sidebar.success(f"✅ {db_report['rows_inserted']:,} rows loaded!")

    except Exception as e:
        st.sidebar.error(f"Error: {e}")


# ── Main Content ───────────────────────────────────────
st.markdown('<p class="main-header">📊 InsightIQ — AI Business Intelligence Assistant</p>', unsafe_allow_html=True)

if not st.session_state.db_loaded:
    st.info("👈 Click **Load & Analyze** in the sidebar to get started.")
    st.image("https://img.icons8.com/fluency/200/combo-chart.png")
    st.stop()


# ── Tabs ───────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "🤖 Ask AI",
    "📈 Charts",
    "💡 Insights",
    "📋 Data Profile"
])


# ═══════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════════════
with tab1:
    st.header("📊 Executive Dashboard")
    if not st.session_state.get("db_loaded") or st.session_state.get("kpis") is None:
        st.info("👈 Click **Load & Analyze** in the sidebar first.")
        st.stop()
    kpis = st.session_state.kpis

    # KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Revenue", f"${kpis.get('total_revenue') or 0:,.0f}")
    with col2:
        st.metric("📦 Total Orders", f"{kpis.get('total_orders') or 0:,}")
    with col3:
        st.metric("👥 Total Customers", f"{kpis.get('total_customers') or 0:,}")
    with col4:
        st.metric("🛒 Avg Order Value", f"${kpis.get('avg_order_value') or 0:,.2f}")

    st.divider()

    # Charts Row 1
    col1, col2 = st.columns(2)
    with col1:
        from visualization.charts import chart_sales_by_region
        st.plotly_chart(chart_sales_by_region(), use_container_width=True, key="d_region")
    with col2:
        from visualization.charts import chart_sales_by_category
        st.plotly_chart(chart_sales_by_category(), use_container_width=True, key="d_category")

    # Charts Row 2
    col1, col2 = st.columns(2)
    with col1:
        from visualization.charts import chart_yearly_trend
        st.plotly_chart(chart_yearly_trend(), use_container_width=True, key="d_yearly")
    with col2:
        from visualization.charts import chart_sales_by_segment
        st.plotly_chart(chart_sales_by_segment(), use_container_width=True, key="d_segment")

    # Full width charts
    from visualization.charts import chart_top_states
    st.plotly_chart(chart_top_states(), use_container_width=True, key="d_states")

    col1, col2 = st.columns(2)
    with col1:
        from visualization.charts import chart_monthly_trend
        st.plotly_chart(chart_monthly_trend(), use_container_width=True, key="d_monthly")
    with col2:
        from visualization.charts import chart_ship_mode
        st.plotly_chart(chart_ship_mode(), use_container_width=True, key="d_shipmode")

    from visualization.charts import chart_sales_heatmap, chart_sub_category, chart_top_products
    st.plotly_chart(chart_sales_heatmap(), use_container_width=True, key="d_heatmap")
    st.plotly_chart(chart_sub_category(), use_container_width=True, key="d_subcat")
    st.plotly_chart(chart_top_products(), use_container_width=True, key="d_products")


# ═══════════════════════════════════════════════════════
# TAB 2: ASK AI
# ═══════════════════════════════════════════════════════
with tab2:
    st.header("🤖 Ask Your Data Anything")
    st.caption("Powered by Groq + LLaMA 3 — type in plain English")

    # Suggested questions
    st.subheader("💡 Try these questions:")
    suggestions = [
        "Which region has the highest total sales?",
        "What are the top 5 products by revenue?",
        "Show me sales trend by year",
        "Which city generates the most revenue?",
        "What is the most popular ship mode?",
        "Show sales by sub-category",
        "Which customer segment is most valuable?",
        "What are the top 3 states by sales?"
    ]

    # Just display as text — no buttons
    for suggestion in suggestions:
        st.markdown(f"▸ `{suggestion}`")

    st.divider()

    user_question = st.text_input(
        "Ask a question about your data:",
        placeholder="e.g. Which region has the highest sales?",
        key="question_input"
    )

    ask_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)

    if ask_btn and user_question:
        from utils.agent_loop import AgentLoop, MAX_RETRIES
        import plotly.express as px
        from utils.query_history import save_query
        from visualization.chart_picker import pick_chart_type

        if "agent" not in st.session_state:
            with st.spinner("Initializing agent..."):
                st.session_state.agent = AgentLoop()

        agent = st.session_state.agent

        with st.spinner("🤖 Agent working..."):
            result = agent.run(user_question)

        # Execution log
        with st.expander("🔍 Agent Execution Log", expanded=True):
            for log in result["execution_log"]:
                st.text(log)
            if result["retries"] > 0:
                st.warning(f"⚠️ Self-healed after {result['retries']} retries")

        # Show SQL
        if show_sql and result["sql"]:
            with st.expander("🔧 Generated SQL", expanded=True):
                st.code(result["sql"], language="sql")

        if result["success"]:
            df_result = result["data"]
            st.success(f"✅ {len(df_result)} rows returned")
            st.dataframe(df_result, use_container_width=True)

            if show_explanation and result["explanation"]:
                st.info(f"💬 **AI Insight:** {result['explanation']}")

            # Smart chart
            chart_type = pick_chart_type(user_question)
            if len(df_result.columns) >= 2 and chart_type != "table":
                try:
                    x_col = df_result.columns[0]
                    y_col = df_result.columns[1]
                    if chart_type == "bar":
                        fig = px.bar(df_result, x=x_col, y=y_col,
                                    title=f"📊 {user_question}", text_auto=True)
                    elif chart_type == "line":
                        fig = px.line(df_result, x=x_col, y=y_col,
                                     title=f"📈 {user_question}", markers=True)
                    elif chart_type == "pie":
                        fig = px.pie(df_result, names=x_col, values=y_col,
                                    title=f"🥧 {user_question}", hole=0.4)
                    else:
                        fig = px.bar(df_result, x=x_col, y=y_col,
                                    title=f"📊 {user_question}")
                    st.plotly_chart(fig, use_container_width=True,
                                   key=f"ai_{hash(user_question)}")
                except Exception as e:
                    st.warning(f"Chart could not be generated: {e}")

            # Save metrics
            save_query(
                user_question,
                result["sql"],
                0.95 if result["retries"] == 0 else 0.7,
                len(df_result),
                True
            )

            st.session_state.chat_history.append({
                "question": user_question,
                "sql": result["sql"],
                "rows": len(df_result),
                "retries": result["retries"]
            })

            # Live metrics
            metrics = agent.get_metrics()
            if metrics:
                st.divider()
                st.subheader("📊 Live Agent Metrics")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Queries", metrics["total_queries"])
                c2.metric("Success Rate", f"{metrics['success_rate']}%")
                c3.metric("First-Pass Rate", f"{metrics['first_pass_rate']}%")
                c4.metric("Token Savings", f"{metrics['token_savings_percent']}%")

        else:
            st.error(f"❌ Agent could not answer after {MAX_RETRIES} attempts. Try rephrasing.")

    # Query History
    if st.session_state.chat_history:
        st.divider()
        st.subheader("📜 Query History This Session")
        for item in reversed(st.session_state.chat_history[-5:]):
            with st.expander(f"Q: {item['question']}", expanded=False):
                st.code(item["sql"], language="sql")
                st.caption(f"Rows: {item['rows']} | Retries: {item.get('retries', 0)}")


# ═══════════════════════════════════════════════════════
# TAB 3: CHARTS
# ═══════════════════════════════════════════════════════
with tab3:
    st.header("📈 Visual Analytics")
    if not st.session_state.get("db_loaded") or st.session_state.get("kpis") is None:
        st.info("👈 Click **Load & Analyze** in the sidebar first.")
        st.stop()
    from visualization.charts import (
        chart_sales_by_region, chart_sales_by_category,
        chart_yearly_trend, chart_monthly_trend,
        chart_top_products, chart_top_states,
        chart_ship_mode, chart_sales_heatmap, chart_sub_category
    )

    chart_option = st.selectbox("Choose a chart:", [
        "Sales by Region", "Sales by Category", "Sales by Segment",
        "Yearly Trend", "Monthly Pattern", "Top 10 Products",
        "Sales by State (Map)", "Shipping Mode", "Sales Heatmap", "Sub-Category"
    ])

    chart_map = {
        "Sales by Region": chart_sales_by_region,
        "Sales by Category": chart_sales_by_category,
        "Sales by Segment": chart_sales_by_segment,
        "Yearly Trend": chart_yearly_trend,
        "Monthly Pattern": chart_monthly_trend,
        "Top 10 Products": chart_top_products,
        "Sales by State (Map)": chart_top_states,
        "Shipping Mode": chart_ship_mode,
        "Sales Heatmap": chart_sales_heatmap,
        "Sub-Category": chart_sub_category
    }

    from visualization.charts import chart_sales_by_segment
    fig = chart_map[chart_option]()
    st.plotly_chart(fig, use_container_width=True, key="tab3_chart")


# ═══════════════════════════════════════════════════════
# TAB 4: INSIGHTS & RECOMMENDATIONS
# ═══════════════════════════════════════════════════════
with tab4:
    st.header("💡 Business Insights & Recommendations")
    if not st.session_state.get("db_loaded") or st.session_state.get("kpis") is None:
        st.info("👈 Click **Load & Analyze** in the sidebar first.")
        st.stop()
    kpis = st.session_state.kpis

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Auto-Generated Insights")
        from analytics.insights import generate_insights
        insights = generate_insights(kpis)
        for insight in insights:
            st.markdown(
                f'<div class="insight-box"><b>{insight["title"]}</b><br>{insight["value"]}</div>',
                unsafe_allow_html=True
            )

    with col2:
        st.subheader("🎯 Strategic Recommendations")
        from analytics.recommendations import generate_rule_based_recommendations
        recs = generate_rule_based_recommendations(kpis)
        for rec in recs:
            st.markdown(
                f'<div class="rec-box">{rec}</div>',
                unsafe_allow_html=True
            )

    st.divider()
    st.subheader("🤖 AI Executive Recommendations")
    if st.button("Generate AI Recommendations", type="primary"):
        from analytics.recommendations import generate_ai_recommendations
        with st.spinner("Consulting AI analyst..."):
            ai_recs = generate_ai_recommendations(kpis)
        st.markdown(ai_recs)
        st.divider()
    st.subheader("📄 Export Report")
    if st.button("📥 Download PDF Report", type="primary"):
        from exports.pdf_generator import generate_pdf_report
        from analytics.insights import generate_insights
        from analytics.recommendations import generate_rule_based_recommendations

        with st.spinner("Generating PDF..."):
            insights = generate_insights(kpis)
            recs = generate_rule_based_recommendations(kpis)
            filepath = generate_pdf_report(kpis, insights, recs)

        with open(filepath, "rb") as f:
            st.download_button(
                label="⬇️ Click to Download PDF",
                data=f,
                file_name="InsightIQ_Executive_Report.pdf",
                mime="application/pdf",
                key="pdf_download"
            )
        st.success("✅ PDF ready!")


# ═══════════════════════════════════════════════════════
# TAB 5: DATA PROFILE
# ═══════════════════════════════════════════════════════
with tab5:
    st.header("📋 Dataset Profile Report")
    profile = st.session_state.get("profile", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", f"{profile.get('total_rows', 0):,}")
    col2.metric("Total Columns", profile.get("total_columns", 0))
    col3.metric("Missing Values", profile.get("missing_values", 0))
    col4.metric("Data Health Score", f"{profile.get('data_health_score', 0)}/100")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Column Types")
        st.write("**Numeric:**", profile.get("numeric_columns", []))
        st.write("**Text:**", profile.get("text_columns", []))
        st.write("**Date:**", profile.get("date_columns", []))

    with col2:
        st.subheader("⚠️ Outliers Detected")
        outliers = profile.get("outliers_detected", {})
        if outliers:
            for col, count in outliers.items():
                st.warning(f"{col}: {count} outliers")
        else:
            st.success("No significant outliers found!")

    st.divider()
    st.subheader("📈 Numeric Summary Statistics")
    if "numeric_summary" in profile:
        st.dataframe(pd.DataFrame(profile["numeric_summary"]).T, use_container_width=True)

    st.subheader("🗃️ Raw Data Preview")
    if st.session_state.df is not None:
        st.dataframe(st.session_state.df.head(100), use_container_width=True)