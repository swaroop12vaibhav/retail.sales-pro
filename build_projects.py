"""
Project 1: Retail Sales SQL Analysis
------------------------------------
Pipeline: generate messy retail data -> clean it with pandas -> analyse it with SQL (SQLite) -> export to Excel.
Note: the data is SIMULATED (fixed random seed), so results are reproducible.

Run:  python project1_retail_sales_sql_analysis.py
Needs: pip install numpy pandas openpyxl
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- 1. SETUP
rng = np.random.default_rng(42)                      # fixed seed -> same data every run
OUT_DIR = Path(__file__).parent / "P1_Retail_Sales_SQL_Analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)           # create output folder if missing

# ------------------------------------------------- 2. GENERATE CLEAN ORDERS
N = 12_000
order_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 731, N), unit="D")

orders = pd.DataFrame({
    "order_id": np.arange(1001, 1001 + N),
    "order_date": order_dates.strftime("%Y-%m-%d"),
    "customer_id": rng.integers(1, 2001, N),
    "region": rng.choice(["North", "South", "East", "West"], N, p=[.30, .25, .25, .20]),
    "category": rng.choice(["Electronics", "Furniture", "Clothing", "Grocery", "Beauty"], N,
                           p=[.20, .15, .30, .25, .10]),
    "quantity": rng.integers(1, 6, N),
    "unit_price": 0.0,                                # filled in below
    "discount_pct": rng.choice([0, 5, 10, 15, 20], N, p=[.4, .2, .2, .1, .1]),
})

# unit price = category base price x random factor (0.7 to 1.3)
BASE_PRICE = {"Electronics": 320, "Furniture": 210, "Clothing": 45, "Grocery": 18, "Beauty": 30}
orders["unit_price"] = [round(BASE_PRICE[c] * rng.uniform(0.7, 1.3), 2) for c in orders.category]

# ---------------------------------------- 3. INJECT REAL-WORLD DATA PROBLEMS
raw = orders.copy()

dup_idx = rng.choice(N, 360, replace=False)                       # 360 duplicate rows
raw = pd.concat([raw, raw.iloc[dup_idx]], ignore_index=True)

raw.loc[rng.choice(len(raw), 250, replace=False), "region"] = None   # 250 missing regions

case_idx = rng.choice(len(raw), 400, replace=False)                  # 400 UPPERCASE categories
raw.loc[case_idx, "category"] = raw.loc[case_idx, "category"].str.upper()

raw.to_csv(OUT_DIR / "raw_retail_orders.csv", index=False)

# ------------------------------------------------------------- 4. CLEAN DATA
clean = raw.copy()
rows_raw = len(clean)

clean = clean.drop_duplicates()                       # exact duplicate rows only
dups_removed = rows_raw - len(clean)                  # 320, not 360: some duplicates were altered above

casing_fixed = int((clean.category != clean.category.str.title()).sum())
clean["category"] = clean["category"].str.title()     # 'ELECTRONICS' -> 'Electronics'

missing_regions = int(clean.region.isna().sum())
clean["region"] = clean["region"].fillna("Unknown")   # keep the rows, flag the gap

clean["revenue"] = (clean.quantity * clean.unit_price * (1 - clean.discount_pct / 100)).round(2)

# ------------------------------------------------------------ 5. SQL ANALYSIS
con = sqlite3.connect(":memory:")                     # temporary in-memory database
clean.to_sql("orders", con, index=False)

QUERIES = {
    "revenue_by_region": """
        SELECT region,
               ROUND(SUM(revenue), 2) AS revenue,
               COUNT(*) AS orders,
               ROUND(SUM(revenue) * 100.0 / (SELECT SUM(revenue) FROM orders), 1) AS pct_share
        FROM orders
        GROUP BY region
        ORDER BY revenue DESC""",
    "revenue_by_category": """
        SELECT category,
               ROUND(SUM(revenue), 2) AS revenue,
               ROUND(AVG(revenue), 2) AS avg_order_value
        FROM orders
        GROUP BY category
        ORDER BY revenue DESC""",
    "monthly_trend": """
        SELECT substr(order_date, 1, 7) AS month,
               ROUND(SUM(revenue), 2) AS revenue,
               COUNT(*) AS orders
        FROM orders
        GROUP BY month
        ORDER BY month""",
    "top_10_customers": """
        SELECT customer_id,
               COUNT(*) AS orders,
               ROUND(SUM(revenue), 2) AS revenue
        FROM orders
        GROUP BY customer_id
        ORDER BY revenue DESC
        LIMIT 10""",
    "discount_impact": """
        SELECT discount_pct,
               COUNT(*) AS orders,
               ROUND(AVG(quantity), 2) AS avg_qty,
               ROUND(AVG(revenue), 2) AS avg_order_value
        FROM orders
        GROUP BY discount_pct
        ORDER BY discount_pct""",
    "repeat_customers": """
        SELECT CASE WHEN n > 1 THEN 'Repeat' ELSE 'One-time' END AS type,
               COUNT(*) AS customers
        FROM (SELECT customer_id, COUNT(*) AS n FROM orders GROUP BY customer_id)
        GROUP BY type""",
}

# save the SQL as a reusable file
sql_text = "-- Retail Sales Analysis (SQLite). Table: orders (cleaned data)\n\n" + "\n\n".join(
    f"-- {name}\n{query.strip()};" for name, query in QUERIES.items())
(OUT_DIR / "analysis_queries.sql").write_text(sql_text)

results = {name: pd.read_sql(query, con) for name, query in QUERIES.items()}

# --------------------------------------------------------------- 6. EXPORT
cleaning_log = pd.DataFrame({
    "Metric": ["Raw rows", "Duplicates removed", "Missing regions filled",
               "Category casing fixed", "Clean rows", "Total revenue"],
    "Value": [rows_raw, dups_removed, missing_regions, casing_fixed, len(clean),
              round(clean.revenue.sum(), 2)],
})

with pd.ExcelWriter(OUT_DIR / "retail_sales_analysis.xlsx") as writer:
    cleaning_log.to_excel(writer, sheet_name="Data_Cleaning_Log", index=False)
    for name, df in results.items():
        df.to_excel(writer, sheet_name=name[:31], index=False)   # Excel sheet names max 31 chars
    clean.to_excel(writer, sheet_name="clean_data", index=False)

# ------------------------------------------------------------ 7. SUMMARY
region, category, repeat = (results["revenue_by_region"], results["revenue_by_category"],
                            results["repeat_customers"])
total_revenue = clean.revenue.sum()
print(cleaning_log.to_string(index=False))
print(f"\nTop region: {region.iloc[0].region} ({region.iloc[0].pct_share}% of revenue)")
print(f"Top category: {category.iloc[0].category} "
      f"({category.iloc[0].revenue * 100 / total_revenue:.1f}% of revenue)")
print(f"Repeat customers: {int(repeat[repeat.type == 'Repeat'].customers.iloc[0])} "
      f"of {int(repeat.customers.sum())}")
print(f"\nFiles saved in: {OUT_DIR}")