# SQL lab exercises and DBMS concepts

These queries target the SQLite schema in `database/schema.sql`. Use the Oracle examples in `database/oracle_plsql_examples.sql` for the Oracle-specific PL/SQL syllabus. Run write statements only against a disposable test database.

## DDL
```sql
CREATE TABLE IF NOT EXISTS categories_demo (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE
);
```

## DML
```sql
INSERT INTO customers(full_name, phone) VALUES ('Demo Customer', '9000000002');
UPDATE medicines SET reorder_level = 12 WHERE name = 'Paracetamol 500 mg';
SELECT medicine_id, name, category FROM medicines ORDER BY name;
-- Delete is subject to foreign-key constraints and may be rejected if referenced.
```

## Join: bill details
```sql
SELECT s.invoice_number, s.sale_date, c.full_name, m.name,
       si.quantity, si.unit_price, si.line_total
FROM sales s
LEFT JOIN customers c ON c.customer_id = s.customer_id
JOIN sale_items si ON si.sale_id = s.sale_id
JOIN medicine_batches b ON b.batch_id = si.batch_id
JOIN medicines m ON m.medicine_id = b.medicine_id
ORDER BY s.sale_date DESC;
```

## Subquery: medicines with stock below their reorder level
```sql
SELECT m.name, m.reorder_level,
       (SELECT COALESCE(SUM(b.quantity), 0)
          FROM medicine_batches b
         WHERE b.medicine_id = m.medicine_id
           AND b.expiry_date >= date('now')) AS available_stock
FROM medicines m
WHERE (SELECT COALESCE(SUM(b.quantity), 0)
         FROM medicine_batches b
        WHERE b.medicine_id = m.medicine_id
          AND b.expiry_date >= date('now')) <= m.reorder_level;
```

## Aggregate query
```sql
SELECT date(sale_date) AS sale_day, COUNT(*) AS bill_count,
       SUM(total_amount) AS revenue, AVG(total_amount) AS average_bill
FROM sales
GROUP BY date(sale_date)
ORDER BY sale_day DESC;
```

## View and index
```sql
SELECT * FROM v_low_stock;
SELECT * FROM v_expiring_batches;
EXPLAIN QUERY PLAN SELECT * FROM medicines WHERE name LIKE 'Para%';
```

## Transactions and concurrency
The Flask sale handler uses a single SQLite connection per request, a transaction, foreign-key enforcement, a busy timeout, and a conditional stock decrement. The conditional update and quantity check prevent overselling in this simple demonstration. SQLite serializes writes; for many concurrent pharmacy terminals, use a server database such as PostgreSQL or Oracle and review isolation/locking requirements.

## Constraint checks to demonstrate
- Duplicate `(medicine_id, batch_number)` violates a UNIQUE constraint.
- Quantity and reorder level cannot be negative due to CHECK constraints.
- A sale item cannot reference a missing sale or batch due to foreign keys.
- Sale quantity must be positive.
