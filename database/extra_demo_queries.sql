-- MedCare Pharmacy: Extra DBMS Viva and Demonstration Queries
-- Run AFTER database/schema.sql and database/college_demo.sql (or medcare_complete.sql).
-- SQLite compatible. Run each SELECT separately to display its result grid.
-- These queries are read-only and do not alter inventory.

-- 1. Search medicines by part of their name (edit the text between % signs)
SELECT medicine_id, name, category, manufacturer, unit
FROM medicines
WHERE name LIKE '%Vitamin%'
ORDER BY name;

-- 2. Search by category
SELECT medicine_id, name, category, manufacturer
FROM medicines
WHERE category LIKE '%Demo%'
ORDER BY category, name;

-- 3. Medicine and batch details with supplier (JOIN)
SELECT m.name AS medicine_name, m.category, b.batch_number,
       b.expiry_date, b.quantity, b.purchase_price, b.selling_price,
       s.name AS supplier_name
FROM medicines m
JOIN medicine_batches b ON b.medicine_id = m.medicine_id
LEFT JOIN suppliers s ON s.supplier_id = b.supplier_id
ORDER BY m.name, b.expiry_date;

-- 4. Count of batches for each medicine (LEFT JOIN also shows medicines with no batches)
SELECT m.name AS medicine_name, COUNT(b.batch_id) AS batch_count
FROM medicines m
LEFT JOIN medicine_batches b ON b.medicine_id = m.medicine_id
GROUP BY m.medicine_id, m.name
ORDER BY batch_count DESC, m.name;

-- 5. Total stock by medicine across unexpired batches
SELECT m.name AS medicine_name,
       COALESCE(SUM(CASE WHEN b.expiry_date >= date('now') THEN b.quantity ELSE 0 END), 0) AS available_units
FROM medicines m
LEFT JOIN medicine_batches b ON b.medicine_id = m.medicine_id
GROUP BY m.medicine_id, m.name
ORDER BY available_units DESC, m.name;

-- 6. Estimated stock value at purchase cost (current batch quantity × purchase price)
SELECT ROUND(SUM(b.quantity * b.purchase_price), 2) AS stock_value_at_cost
FROM medicine_batches b
WHERE b.expiry_date >= date('now');

-- 7. Estimated stock value at selling price (not profit; excludes no batches)
SELECT ROUND(SUM(b.quantity * b.selling_price), 2) AS potential_sales_value
FROM medicine_batches b
WHERE b.expiry_date >= date('now');

-- 8. Purchase total by supplier
SELECT COALESCE(s.name, 'Supplier not recorded') AS supplier_name,
       COUNT(p.purchase_id) AS invoice_count,
       ROUND(COALESCE(SUM(p.total_amount), 0), 2) AS total_purchase_amount
FROM purchases p
LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id
GROUP BY p.supplier_id, s.name
ORDER BY total_purchase_amount DESC;

-- 9. Sales total by customer (NULL customer IDs are shown as walk-in/unrecorded)
SELECT COALESCE(c.full_name, 'Walk-in / customer not recorded') AS customer_name,
       COUNT(s.sale_id) AS invoice_count,
       ROUND(COALESCE(SUM(s.total_amount), 0), 2) AS total_sales_amount
FROM sales s
LEFT JOIN customers c ON c.customer_id = s.customer_id
GROUP BY s.customer_id, c.full_name
ORDER BY total_sales_amount DESC;

-- 10. Top-selling medicines by recorded sale-item quantity
SELECT m.name AS medicine_name,
       SUM(si.quantity) AS units_recorded_sold,
       ROUND(SUM(si.line_total), 2) AS recorded_sales_value
FROM sale_items si
JOIN medicine_batches b ON b.batch_id = si.batch_id
JOIN medicines m ON m.medicine_id = b.medicine_id
GROUP BY m.medicine_id, m.name
ORDER BY units_recorded_sold DESC, recorded_sales_value DESC;

-- 11. Medicines priced above the average batch selling price
SELECT m.name AS medicine_name, b.batch_number, b.selling_price
FROM medicine_batches b
JOIN medicines m ON m.medicine_id = b.medicine_id
WHERE b.selling_price > (SELECT AVG(selling_price) FROM medicine_batches)
ORDER BY b.selling_price DESC;

-- 12. Duplicate medicine names (should normally return no rows if names are unique)
-- The current schema does not enforce unique medicine names, so this query detects duplicates.
SELECT name, COUNT(*) AS occurrences
FROM medicines
GROUP BY name
HAVING COUNT(*) > 1;

-- 13. Data integrity: batches with missing medicine references (should return no rows)
SELECT b.batch_id, b.medicine_id, b.batch_number
FROM medicine_batches b
LEFT JOIN medicines m ON m.medicine_id = b.medicine_id
WHERE m.medicine_id IS NULL;

-- 14. Invoice detail with computed line total for comparison
SELECT p.invoice_number, m.name AS medicine_name,
       pi.quantity, pi.unit_cost, pi.line_total,
       ROUND(pi.quantity * pi.unit_cost, 2) AS recalculated_line_total
FROM purchase_items pi
JOIN purchases p ON p.purchase_id = pi.purchase_id
JOIN medicine_batches b ON b.batch_id = pi.batch_id
JOIN medicines m ON m.medicine_id = b.medicine_id
ORDER BY p.invoice_number, m.name;

-- 15. Show SQLite foreign-key enforcement setting for this connection
PRAGMA foreign_keys;

-- 16. List tables and views in the database
SELECT type, name
FROM sqlite_master
WHERE type IN ('table', 'view')
  AND name NOT LIKE 'sqlite_%'
ORDER BY type, name;

-- 17. Explain an inventory query plan (index/viva discussion)
EXPLAIN QUERY PLAN
SELECT * FROM medicines WHERE name = 'Demo Medicine A - Aspirin 75 mg';

-- Viva points:
-- PRIMARY KEY: uniquely identifies each row.
-- FOREIGN KEY: links records between related tables.
-- CHECK: rejects values that violate a condition.
-- JOIN: combines related rows from tables.
-- GROUP BY: aggregates records into groups.
-- HAVING: filters grouped results.
-- VIEW: saved query presented like a virtual table.
-- INDEX: can speed up lookups; it adds storage/write overhead.
-- TRANSACTION: COMMIT saves changes; ROLLBACK cancels uncommitted changes.
