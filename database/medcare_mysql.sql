-- MedCare Pharmacy DBMS Lab Project
-- MySQL 8.0+ compatible (tested syntax target: MySQL Community Server 8.4)
-- B.Tech 2nd Year, 1st Semester: beginner/intermediate SQL practice.
--
-- HOW TO RUN IN MYSQL COMMAND LINE:
-- 1. Save this file as medcare_mysql.sql.
-- 2. At mysql> run: SOURCE C:/full/path/to/medcare_mysql.sql;
-- 3. Then try the practice queries at the bottom, one at a time.
--
-- IMPORTANT: This setup drops tables with these names in medcare_pharmacy
-- and recreates them. Use a practice database, not important existing data.

CREATE DATABASE IF NOT EXISTS medcare_pharmacy;
USE medcare_pharmacy;

SET FOREIGN_KEY_CHECKS = 0;
DROP VIEW IF EXISTS v_low_stock;
DROP VIEW IF EXISTS v_inventory;
DROP TABLE IF EXISTS stock_movements;
DROP TABLE IF EXISTS sale_items;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS purchase_items;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS medicine_batches;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS suppliers;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. SUPPLIERS: companies from which medicines are purchased.
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(200),
    CHECK (CHAR_LENGTH(TRIM(name)) > 0)
);

-- 2. CUSTOMERS: people who purchase medicines.
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    CHECK (CHAR_LENGTH(TRIM(full_name)) > 0)
);

-- 3. MEDICINES: general medicine details.
CREATE TABLE medicines (
    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    unit VARCHAR(20) NOT NULL DEFAULT 'strip',
    reorder_level INT NOT NULL DEFAULT 10,
    CHECK (reorder_level >= 0)
);

-- 4. MEDICINE_BATCHES: stock, expiry and prices for each batch.
CREATE TABLE medicine_batches (
    batch_id INT PRIMARY KEY AUTO_INCREMENT,
    medicine_id INT NOT NULL,
    supplier_id INT,
    batch_number VARCHAR(40) NOT NULL,
    expiry_date DATE NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    purchase_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    UNIQUE (medicine_id, batch_number),
    CHECK (quantity >= 0),
    CHECK (purchase_price >= 0),
    CHECK (selling_price >= 0),
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 5. PURCHASES: one record per supplier invoice.
CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_id INT,
    invoice_number VARCHAR(40) NOT NULL UNIQUE,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    CHECK (total_amount >= 0),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 6. PURCHASE_ITEMS: medicines included in each purchase.
CREATE TABLE purchase_items (
    purchase_item_id INT PRIMARY KEY AUTO_INCREMENT,
    purchase_id INT NOT NULL,
    batch_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    CHECK (quantity > 0),
    CHECK (unit_cost >= 0),
    CHECK (line_total >= 0),
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
    FOREIGN KEY (batch_id) REFERENCES medicine_batches(batch_id)
);

-- 7. SALES: one record per customer bill.
CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    invoice_number VARCHAR(40) NOT NULL UNIQUE,
    sale_date DATE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    CHECK (total_amount >= 0),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 8. SALE_ITEMS: medicines included in each bill.
CREATE TABLE sale_items (
    sale_item_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_id INT NOT NULL,
    batch_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    CHECK (quantity > 0),
    CHECK (unit_price >= 0),
    CHECK (line_total >= 0),
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (batch_id) REFERENCES medicine_batches(batch_id)
);

-- 9. STOCK_MOVEMENTS: simple record of stock changes.
CREATE TABLE stock_movements (
    movement_id INT PRIMARY KEY AUTO_INCREMENT,
    batch_id INT NOT NULL,
    movement_type VARCHAR(20) NOT NULL,
    quantity_change INT NOT NULL,
    note VARCHAR(150),
    movement_date DATE NOT NULL,
    CHECK (movement_type IN ('PURCHASE', 'SALE', 'ADJUSTMENT')),
    CHECK (quantity_change <> 0),
    FOREIGN KEY (batch_id) REFERENCES medicine_batches(batch_id)
);

-- SAMPLE DATA: synthetic classroom demonstration records.
INSERT INTO suppliers (supplier_id, name, phone, email, address) VALUES
(1, 'Demo Medical Distributors', '9000000001', 'demo1@example.test', 'Demo address'),
(2, 'Sample Health Supplies', '9000000002', 'demo2@example.test', 'Demo address'),
(3, 'Training Pharma Wholesale', '9000000003', 'demo3@example.test', 'Demo address');

INSERT INTO customers (customer_id, full_name, phone) VALUES
(1, 'Demo Walk-in Customer', '9000010001'),
(2, 'Sample Customer A', '9000010002'),
(3, 'Sample Customer B', '9000010003');

INSERT INTO medicines (medicine_id, name, category, manufacturer, unit, reorder_level) VALUES
(1, 'Paracetamol 500 mg', 'Pain Relief', 'Demo Pharma', 'strip', 20),
(2, 'Cetirizine 10 mg', 'Allergy', 'Demo Pharma', 'strip', 12),
(3, 'ORS Sachet', 'Rehydration', 'Demo Labs', 'piece', 10),
(4, 'Vitamin C 500 mg', 'Supplement', 'Demo Labs', 'strip', 15),
(5, 'Antacid Tablets', 'Digestive Health', 'Training Pharma', 'strip', 12),
(6, 'Bandage Roll', 'First Aid', 'Sample Health Supplies', 'roll', 8),
(7, 'Cough Syrup 100 ml', 'Cough Care', 'Demo Pharma', 'bottle', 10),
(8, 'Calamine Lotion 100 ml', 'Skin Care', 'Training Pharma', 'bottle', 8);

INSERT INTO medicine_batches
(batch_id, medicine_id, supplier_id, batch_number, expiry_date, quantity, purchase_price, selling_price) VALUES
(1, 1, 1, 'PAR-101', '2028-12-31', 100, 10.00, 15.00),
(2, 2, 1, 'CET-101', '2028-11-30', 45, 8.00, 12.00),
(3, 3, 2, 'ORS-101', '2028-10-31', 80, 4.00, 7.00),
(4, 4, 2, 'VTC-101', '2028-09-30', 8, 12.00, 18.00),
(5, 5, 3, 'ANT-101', '2026-11-15', 6, 9.00, 14.00),
(6, 6, 2, 'BAN-101', '2028-06-30', 50, 7.00, 12.00),
(7, 7, 1, 'CSY-101', '2026-12-05', 30, 25.00, 38.00),
(8, 8, 3, 'CAL-101', '2026-11-22', 27, 18.00, 28.00);

INSERT INTO purchases (purchase_id, supplier_id, invoice_number, purchase_date, total_amount) VALUES
(1, 1, 'PUR-DEMO-001', '2026-10-01', 1360.00),
(2, 2, 'PUR-DEMO-002', '2026-10-02', 656.00);

INSERT INTO purchase_items (purchase_item_id, purchase_id, batch_id, quantity, unit_cost, line_total) VALUES
(1, 1, 1, 100, 10.00, 1000.00),
(2, 1, 2, 45, 8.00, 360.00),
(3, 2, 3, 80, 4.00, 320.00),
(4, 2, 4, 28, 12.00, 336.00);

INSERT INTO sales (sale_id, customer_id, invoice_number, sale_date, total_amount) VALUES
(1, 1, 'SALE-DEMO-001', '2026-10-05', 45.00),
(2, 2, 'SALE-DEMO-002', '2026-10-06', 36.00);

INSERT INTO sale_items (sale_item_id, sale_id, batch_id, quantity, unit_price, line_total) VALUES
(1, 1, 1, 3, 15.00, 45.00),
(2, 2, 4, 2, 18.00, 36.00);

INSERT INTO stock_movements (movement_id, batch_id, movement_type, quantity_change, note, movement_date) VALUES
(1, 1, 'PURCHASE', 100, 'Demo stock received', '2026-10-01'),
(2, 2, 'PURCHASE', 45, 'Demo stock received', '2026-10-01'),
(3, 1, 'SALE', -3, 'Demo sale', '2026-10-05'),
(4, 4, 'SALE', -2, 'Demo sale', '2026-10-06');

-- SIMPLE REPORT VIEWS: a view is a saved SELECT query.
CREATE VIEW v_inventory AS
SELECT m.medicine_id, m.name AS medicine_name, m.category, m.unit,
       m.reorder_level, COALESCE(SUM(b.quantity), 0) AS total_stock
FROM medicines m
LEFT JOIN medicine_batches b ON m.medicine_id = b.medicine_id
GROUP BY m.medicine_id, m.name, m.category, m.unit, m.reorder_level;

CREATE VIEW v_low_stock AS
SELECT * FROM v_inventory
WHERE total_stock <= reorder_level;

-- ------------------------------------------------------------
-- PRACTICE QUERIES: run these separately after setup finishes.
-- ------------------------------------------------------------

-- Q1. Show every medicine.
-- SELECT * FROM medicines;

-- Q2. Search for a medicine by name.
-- SELECT * FROM medicines WHERE name LIKE '%Cough%';

-- Q3. Sort medicines alphabetically.
-- SELECT name, category FROM medicines ORDER BY name;

-- Q4. Count how many medicines are in the catalogue.
-- SELECT COUNT(*) AS medicine_count FROM medicines;

-- Q5. Find minimum, maximum and average selling price.
-- SELECT MIN(selling_price) AS lowest_price,
--        MAX(selling_price) AS highest_price,
--        AVG(selling_price) AS average_price
-- FROM medicine_batches;

-- Q6. Total stock for each medicine (JOIN + GROUP BY).
-- SELECT m.name, SUM(b.quantity) AS total_stock
-- FROM medicines m JOIN medicine_batches b ON m.medicine_id = b.medicine_id
-- GROUP BY m.medicine_id, m.name ORDER BY total_stock DESC;

-- Q7. Categories with more than one medicine (GROUP BY + HAVING).
-- SELECT category, COUNT(*) AS medicine_count
-- FROM medicines GROUP BY category HAVING COUNT(*) > 1;

-- Q8. Medicine and supplier names (JOIN).
-- SELECT m.name, s.name AS supplier_name, b.batch_number, b.quantity
-- FROM medicine_batches b
-- JOIN medicines m ON b.medicine_id = m.medicine_id
-- JOIN suppliers s ON b.supplier_id = s.supplier_id
-- ORDER BY m.name;

-- Q9. Show all medicines, including those with no batch yet (LEFT JOIN).
-- SELECT m.name, b.batch_number, b.quantity
-- FROM medicines m LEFT JOIN medicine_batches b ON m.medicine_id = b.medicine_id
-- ORDER BY m.name;

-- Q10. Medicines priced above the average selling price (subquery).
-- SELECT m.name, b.selling_price
-- FROM medicines m JOIN medicine_batches b ON m.medicine_id = b.medicine_id
-- WHERE b.selling_price > (SELECT AVG(selling_price) FROM medicine_batches);

-- Q11. Low-stock report using a view.
-- SELECT * FROM v_low_stock;

-- Q12. Purchase invoices with supplier names.
-- SELECT p.invoice_number, s.name AS supplier_name, p.purchase_date, p.total_amount
-- FROM purchases p LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id;

-- Q13. Sales totals by customer.
-- SELECT c.full_name, SUM(s.total_amount) AS total_spent
-- FROM customers c JOIN sales s ON c.customer_id = s.customer_id
-- GROUP BY c.customer_id, c.full_name;

-- Q14. UNION example: list names from both suppliers and customers.
-- SELECT name AS person_or_company FROM suppliers
-- UNION
-- SELECT full_name FROM customers;

-- Q15. Check the tables.
-- SHOW TABLES;

-- Q16. Display sales line items and calculate the line total.
-- SELECT s.invoice_number, m.name, si.quantity, si.unit_price,
--        si.quantity * si.unit_price AS calculated_total
-- FROM sale_items si
-- JOIN sales s ON si.sale_id = s.sale_id
-- JOIN medicine_batches b ON si.batch_id = b.batch_id
-- JOIN medicines m ON b.medicine_id = m.medicine_id;

SELECT 'MedCare Pharmacy sample database created successfully.' AS setup_message;
