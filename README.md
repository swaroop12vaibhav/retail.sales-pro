# Retail Sales SQL Analysis

This project analyzes synthetic retail sales data using Python, SQL, and Excel outputs.

## Objective

The goal is to generate realistic retail sales data, clean it, load it into SQLite, run SQL queries for business insights, and export the results for reporting.

## What this project includes

- Synthetic retail sales data generation using Python
- Data cleaning for duplicates, missing values, and inconsistent categories
- Revenue calculation using quantity, unit price, and discount
- SQLite database creation and analysis
- SQL-based KPI queries
- Excel export of analysis results

## Files in this project

- `build_projects.py` — main script that generates and analyzes the data
- `raw_retail_orders.csv` — raw generated sales data
- `analysis_queries.sql` — SQL queries for the analysis
- `retail_sales.db` — SQLite database containing cleaned sales data
- `retail_sales_analysis.xlsx` — Excel workbook with summary reports

## How to run

From the project folder, run:

```bash
python3 build_projects.py
```

## Skills used

- Python programming
- NumPy for random data generation
- Pandas for data processing and analysis
- SQLite database operations
- SQL queries such as GROUP BY, SUM, AVG, COUNT, and CASE WHEN
- Data cleaning and validation
- Excel report generation

## Business questions answered

- Which region generates the most revenue?
- Which product category performs best?
- What is the monthly revenue trend?
- Who are the top customers by revenue?
- What is the impact of discounts?
- How many customers are repeat buyers?

## Notes

This project uses simulated data for learning and practice. It is designed to demonstrate practical analytics and data quality workflows in a simple, beginner-friendly format.
