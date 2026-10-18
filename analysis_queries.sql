-- Retail Sales Analysis (SQLite). Run this file against retail_sales.db.

-- revenue_by_region
SELECT region, ROUND(SUM(revenue),2) revenue, COUNT(*) orders, ROUND(SUM(revenue)*100.0/(SELECT SUM(revenue) FROM orders),1) pct_share FROM orders GROUP BY region ORDER BY revenue DESC;

-- revenue_by_category
SELECT category, ROUND(SUM(revenue),2) revenue, ROUND(AVG(revenue),2) avg_order_value FROM orders GROUP BY category ORDER BY revenue DESC;

-- monthly_trend
SELECT substr(order_date,1,7) month, ROUND(SUM(revenue),2) revenue, COUNT(*) orders FROM orders GROUP BY month ORDER BY month;

-- top_10_customers
SELECT customer_id, COUNT(*) orders, ROUND(SUM(revenue),2) revenue FROM orders GROUP BY customer_id ORDER BY revenue DESC LIMIT 10;

-- discount_impact
SELECT discount_pct, COUNT(*) orders, ROUND(AVG(quantity),2) avg_qty, ROUND(AVG(revenue),2) avg_order_value FROM orders GROUP BY discount_pct ORDER BY discount_pct;

-- repeat_customers
SELECT CASE WHEN n>1 THEN 'Repeat' ELSE 'One-time' END type, COUNT(*) customers FROM (SELECT customer_id, COUNT(*) n FROM orders GROUP BY customer_id) GROUP BY type;