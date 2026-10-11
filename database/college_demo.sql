-- MedCare Pharmacy: DBMS Lab Demonstration Data and Queries
-- Engine: SQLite
-- First run database/schema.sql, then run this file.
-- All records below are clearly labelled college-demo examples.
-- Do not use this sample dataset as real pharmacy/medical inventory.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT OR IGNORE INTO suppliers(name, phone, email, address)
VALUES ('College Demo Supplier', '9000090001', 'college-demo@example.test', 'Sample address for DBMS demonstration');

INSERT OR IGNORE INTO customers(full_name, phone)
VALUES ('College Demo Customer', '9000090002');

-- Add a few extra named medicines if they do not already exist.
INSERT INTO medicines(name, category, manufacturer, unit, reorder_level)
SELECT 'Demo Medicine A - Aspirin 75 mg', 'Demo / Pain relief', 'College Demo Pharma', 'strip', 10
WHERE NOT EXISTS (SELECT 1 FROM medicines WHERE name='Demo Medicine A - Aspirin 75 mg');

INSERT INTO medicines(name, category, manufacturer, unit, reorder_level)
SELECT 'Demo Medicine B - Antacid Tablets', 'Demo / Antacid', 'College Demo Pharma', 'strip', 8
WHERE NOT EXISTS (SELECT 1 FROM medicines WHERE name='Demo Medicine B - Antacid Tablets');

INSERT INTO medicines(name, category, manufacturer, unit, reorder_level)
SELECT 'Demo Medicine C - ORS Sachet', 'Demo / Rehydration', 'College Demo Pharma', 'piece', 12
WHERE NOT EXISTS (SELECT 1 FROM medicines WHERE name='Demo Medicine C - ORS Sachet');

INSERT INTO medicines(name, category, manufacturer, unit, reorder_level)
SELECT 'Demo Medicine D - Vitamin C 500 mg', 'Demo / Supplement', 'College Demo Pharma', 'strip', 15
WHERE NOT EXISTS (SELECT 1 FROM medicines WHERE name='Demo Medicine D - Vitamin C 500 mg');

-- Insert one batch per demo medicine only if it does not already exist.
INSERT INTO medicine_batches(medicine_id, supplier_id, batch_number, expiry_date, quantity, purchase_price, selling_price)
SELECT m.medicine_id, s.supplier_id, 'COLLEGE-ASP-001', date('now','+240 days'), 40, 5.00, 8.00
FROM medicines m CROSS JOIN suppliers s
WHERE m.name='Demo Medicine A - Aspirin 75 mg'
  AND s.name='College Demo Supplier'
  AND NOT EXISTS (SELECT 1 FROM medicine_batches b WHERE b.medicine_id=m.medicine_id AND b.batch_number='COLLEGE-ASP-001');

INSERT INTO medicine_batches(medicine_id, supplier_id, batch_number, expiry_date, quantity, purchase_price, selling_price)
SELECT m.medicine_id, s.supplier_id, 'COLLEGE-ANT-001', date('now','+35 days'), 25, 9.00, 14.00
FROM medicines m CROSS JOIN suppliers s
WHERE m.name='Demo Medicine B - Antacid Tablets'
  AND s.name='College Demo Supplier'
  AND NOT EXISTS (SELECT 1 FROM medicine_batches b WHERE b.medicine_id=m.medicine_id AND b.batch_number='COLLEGE-ANT-001');

INSERT INTO medicine_batches(medicine_id, supplier_id, batch_number, expiry_date, quantity, purchase_price, selling_price)
SELECT m.medicine_id, s.supplier_id, 'COLLEGE-ORS-001', date('now','+300 days'), 4, 3.00, 6.00
FROM medicines m CROSS JOIN suppliers s
WHERE m.name='Demo Medicine C - ORS Sachet'
  AND s.name='College Demo Supplier'
  AND NOT EXISTS (SELECT 1 FROM medicine_batches b WHERE b.medicine_id=m.medicine_id AND b.batch_number='COLLEGE-ORS-001');

INSERT INTO medicine_batches(medicine_id, supplier_id, batch_number, expiry_date, quantity, purchase_price, selling_price)
SELECT m.medicine_id, s.supplier_id, 'COLLEGE-VTC-001', date('now','+400 days'), 60, 10.00, 16.00
FROM medicines m CROSS JOIN suppliers s
WHERE m.name='Demo Medicine D - Vitamin C 500 mg'
  AND s.name='College Demo Supplier'
  AND NOT EXISTS (SELECT 1 FROM medicine_batches b WHERE b.medicine_id=m.medicine_id AND b.batch_number='COLLEGE-VTC-001');

-- Record the initial stock as demo stock movements.
INSERT INTO stock_movements(batch_id, movement_type, quantity_change, reference_text)
SELECT batch_id, 'PURCHASE', quantity, 'COLLEGE-DEMO-SEED — sample data'
FROM medicine_batches b
WHERE b.batch_number IN ('COLLEGE-ASP-001','COLLEGE-ANT-001','COLLEGE-ORS-001','COLLEGE-VTC-001')
AND NOT EXISTS (SELECT 1 FROM stock_movements sm WHERE sm.batch_id=b.batch_id AND sm.reference_text='COLLEGE-DEMO-SEED — sample data');

-- Add a sample purchase invoice and its line items.
INSERT OR IGNORE INTO purchases(supplier_id, invoice_number, purchase_date, total_amount)
SELECT supplier_id, 'COLLEGE-DEMO-PUR-001', date('now'), 200.00
FROM suppliers WHERE name='College Demo Supplier';

INSERT INTO purchase_items(purchase_id, batch_id, quantity, unit_cost, line_total)
SELECT p.purchase_id, b.batch_id, b.quantity, b.purchase_price, b.quantity*b.purchase_price
FROM purchases p
JOIN medicine_batches b ON b.batch_number='COLLEGE-ASP-001'
WHERE p.invoice_number='COLLEGE-DEMO-PUR-001'
AND NOT EXISTS (SELECT 1 FROM purchase_items pi WHERE pi.purchase_id=p.purchase_id AND pi.batch_id=b.batch_id);

-- Add one sample sale record without changing batch stock; it is an illustrative historical record.
INSERT OR IGNORE INTO sales(customer_id, invoice_number, sale_date, total_amount)
SELECT customer_id, 'COLLEGE-DEMO-SALE-001', CURRENT_TIMESTAMP, 16.00
FROM customers WHERE full_name='College Demo Customer';

INSERT INTO sale_items(sale_id, batch_id, quantity, unit_price, line_total)
SELECT s.sale_id, b.batch_id, 2, b.selling_price, 16.00
FROM sales s
JOIN medicine_batches b ON b.batch_number='COLLEGE-ASP-001'
WHERE s.invoice_number='COLLEGE-DEMO-SALE-001'
AND NOT EXISTS (SELECT 1 FROM sale_items si WHERE si.sale_id=s.sale_id AND si.batch_id=b.batch_id);

COMMIT;

-- ============================================================
-- RUN THESE QUERIES ONE AT A TIME in DB Browser's Execute SQL tab
-- ============================================================

-- 1. All medicine names and details
-- SELECT medicine_id, name, category, manufacturer, unit, reorder_level
-- FROM medicines ORDER BY name;

-- 2. Every medicine batch, supplier, expiry, stock and prices
-- SELECT m.name AS medicine_name, b.batch_number, b.expiry_date, b.quantity,
--        b.purchase_price, b.selling_price, s.name AS supplier_name
-- FROM medicine_batches b
-- JOIN medicines m ON m.medicine_id=b.medicine_id
-- LEFT JOIN suppliers s ON s.supplier_id=b.supplier_id
-- ORDER BY m.name, b.expiry_date;

-- 3. Complete inventory view
-- SELECT * FROM v_inventory ORDER BY medicine_name;

-- 4. Low-stock medicines
-- SELECT * FROM v_low_stock ORDER BY available_stock, medicine_name;

-- 5. Batches expiring in the next 90 days
-- SELECT * FROM v_expiring_batches ORDER BY expiry_date;

-- 6. Suppliers
-- SELECT * FROM suppliers ORDER BY name;

-- 7. Customers
-- SELECT * FROM customers ORDER BY full_name;

-- 8. Purchase invoices and line items
-- SELECT p.invoice_number, p.purchase_date, sup.name AS supplier,
--        m.name AS medicine, pi.quantity, pi.unit_cost, pi.line_total
-- FROM purchases p
-- LEFT JOIN suppliers sup ON sup.supplier_id=p.supplier_id
-- JOIN purchase_items pi ON pi.purchase_id=p.purchase_id
-- JOIN medicine_batches b ON b.batch_id=pi.batch_id
-- JOIN medicines m ON m.medicine_id=b.medicine_id
-- ORDER BY p.purchase_date DESC;

-- 9. Sales invoices and line items
-- SELECT s.invoice_number, s.sale_date, c.full_name AS customer,
--        m.name AS medicine, si.quantity, si.unit_price, si.line_total
-- FROM sales s
-- LEFT JOIN customers c ON c.customer_id=s.customer_id
-- JOIN sale_items si ON si.sale_id=s.sale_id
-- JOIN medicine_batches b ON b.batch_id=si.batch_id
-- JOIN medicines m ON m.medicine_id=b.medicine_id
-- ORDER BY s.sale_date DESC;

-- 10. Stock movement history
-- SELECT sm.created_at, m.name AS medicine, b.batch_number,
--        sm.movement_type, sm.quantity_change, sm.reference_text
-- FROM stock_movements sm
-- JOIN medicine_batches b ON b.batch_id=sm.batch_id
-- JOIN medicines m ON m.medicine_id=b.medicine_id
-- ORDER BY sm.created_at DESC;

-- 11. Total number of medicines, batches, suppliers, customers, purchases and sales
-- SELECT
--   (SELECT COUNT(*) FROM medicines) AS medicine_types,
--   (SELECT COUNT(*) FROM medicine_batches) AS batches,
--   (SELECT COUNT(*) FROM suppliers) AS suppliers,
--   (SELECT COUNT(*) FROM customers) AS customers,
--   (SELECT COUNT(*) FROM purchases) AS purchase_invoices,
--   (SELECT COUNT(*) FROM sales) AS sales_invoices;
