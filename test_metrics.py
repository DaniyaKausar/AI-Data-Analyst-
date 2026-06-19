from analytics.kpi_engine import get_all_kpis
from utils.schema_optimizer import build_schema_summary

kpis = get_all_kpis()
schema = build_schema_summary()

print('=== RESUME METRICS ===')
print(f'Total Revenue Analyzed: ${kpis["total_revenue"]:,.2f}')
print(f'Total Orders Processed: {kpis["total_orders"]:,}')
print(f'Total Customers: {kpis["total_customers"]:,}')
print(f'Total Products: {kpis["total_products"]:,}')
print(f'Dataset Size: {schema["total_rows"]:,} rows x {schema["total_columns"]} columns')
print(f'Token Savings: {schema["token_savings_percent"]}%')
print(f'Raw CSV tokens: {schema["raw_csv_tokens_estimate"]:,}')
print(f'Optimized tokens: {schema["summary_tokens_estimate"]:,}')
print('KPIs Generated: 15+')
print('Charts Available: 10')
print(f'Regions Analyzed: {len(kpis["regional_sales"])}')
print(f'Categories: {len(kpis["category_sales"])}')
print(f'Years of Data: {len(kpis["yearly_sales"])}')