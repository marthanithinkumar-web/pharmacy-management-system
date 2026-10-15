-- MedCare Pharmacy: desktop GUI + MySQL college DBMS project
-- MySQL 8.0+. WARNING: this demo script drops/recreates tables in medcare_pharmacy.
-- Do not run against a database containing valuable data.
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

CREATE TABLE suppliers (
 supplier_id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 phone VARCHAR(20), email VARCHAR(100), address VARCHAR(255),
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE customers (
 customer_id INT AUTO_INCREMENT PRIMARY KEY,
 full_name VARCHAR(100) NOT NULL,
 phone VARCHAR(20), email VARCHAR(100), address VARCHAR(255),
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE medicines (
 medicine_id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 category VARCHAR(80), manufacturer VARCHAR(100),
 unit VARCHAR(30) DEFAULT 'strip', reorder_level INT DEFAULT 10,
 prescription_required BOOLEAN DEFAULT FALSE
);
CREATE TABLE medicine_batches (
 batch_id INT AUTO_INCREMENT PRIMARY KEY,
 medicine_id INT NOT NULL, supplier_id INT,
 batch_number VARCHAR(50) NOT NULL UNIQUE,
 purchase_price DECIMAL(10,2) NOT NULL,
 selling_price DECIMAL(10,2) NOT NULL,
 quantity INT NOT NULL DEFAULT 0,
 expiry_date DATE,
 FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
 FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
CREATE TABLE purchases (
 purchase_id INT AUTO_INCREMENT PRIMARY KEY,
 supplier_id INT, purchase_date DATE NOT NULL,
 total_amount DECIMAL(12,2) DEFAULT 0,
 FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
CREATE TABLE purchase_items (
 purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
 purchase_id INT NOT NULL, batch_id INT NOT NULL,
 quantity INT NOT NULL, unit_cost DECIMAL(10,2) NOT NULL,
 FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
 FOREIGN KEY (batch_id) REFERENCES medicine_batches(batch_id)
);
CREATE TABLE sales (
 sale_id INT AUTO_INCREMENT PRIMARY KEY,
 customer_id INT, sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
 total_amount DECIMAL(12,2) DEFAULT 0,
 FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE sale_items (
 sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
 sale_id INT NOT NULL, batch_id INT NOT NULL,
 quantity INT NOT NULL, unit_price DECIMAL(10,2) NOT NULL,
 FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
 FOREIGN KEY (batch_id) REFERENCES medicine_batches(batch_id)
);
CREATE TABLE stock_movements (
 movement_id INT AUTO_INCREMENT PRIMARY KEY,
 batch_id INT NOT NULL,
 movement_type ENUM('PURCHASE','SALE','ADJUSTMENT') NOT NULL,
 quantity_change INT NOT NULL,
 movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 notes VARCHAR(255),
 FOREIGN KEY (batch_id) REFERENCES medicine_batches(batch_id)
);

INSERT INTO suppliers (name,phone,email,address) VALUES
('Healthy Life Distributors','9876501001','healthy@example.com','Hyderabad'),
('Care Medical Supplies','9876501002','care@example.com','Secunderabad'),
('Prime Pharma Wholesale','9876501003','prime@example.com','Warangal');
INSERT INTO customers (full_name,phone,email,address) VALUES
('Rahul Sharma','9000001001','rahul@example.com','Hyderabad'),
('Priya Reddy','9000001002','priya@example.com','Secunderabad'),
('Arjun Kumar','9000001003','arjun@example.com','Warangal');

INSERT INTO medicines (name,category,manufacturer,unit,reorder_level,prescription_required) VALUES
('Paracetamol 500mg','Analgesic','ABC Pharma','tablet',20,FALSE),
('Amoxicillin 250mg','Antibiotic','HealthCare Labs','capsule',15,TRUE),
('Cetirizine 10mg','Antihistamine','Prime Pharma','tablet',10,FALSE),
('Vitamin C 500mg','Supplement','Wellness Labs','tablet',12,FALSE),
('Omeprazole 20mg','Gastrointestinal','ABC Pharma','capsule',10,TRUE),
('ORS Sachet','Rehydration','Care Labs','sachet',15,FALSE),
('Iron + Folic Acid','Supplement','Healthy Labs','tablet',12,TRUE),
('Cough Syrup 100ml','Cough and cold','Prime Pharma','bottle',8,FALSE);

-- Batch quantities are current stock after the sample sales below.
INSERT INTO medicine_batches
(medicine_id,supplier_id,batch_number,purchase_price,selling_price,quantity,expiry_date) VALUES
(1,1,'PCM101',1.50,2.50,90,'2027-12-31'),
(2,2,'AMX201',4.00,6.00,57,'2027-08-31'),
(3,1,'CTZ301',1.00,2.00,6,'2028-03-31'),
(4,3,'VTC401',2.00,3.50,48,'2026-11-30'),
(5,2,'OMP501',3.00,5.00,5,'2027-06-30'),
(6,2,'ORS601',2.00,4.00,7,'2027-05-31'),
(7,1,'IRN701',1.25,2.50,9,'2026-11-20'),
(8,3,'CS801',18.00,28.00,4,'2026-12-05');

INSERT INTO purchases (supplier_id,purchase_date,total_amount) VALUES
(1,'2026-10-01',171.25),
(2,'2026-10-02',275.00),
(3,'2026-10-03',172.00);
-- Purchase item quantities equal opening quantities before sample sales.
INSERT INTO purchase_items (purchase_id,batch_id,quantity,unit_cost) VALUES
(1,1,100,1.50),(1,3,8,1.00),(1,7,9,1.25),
(2,2,60,4.00),(2,5,7,3.00),(2,6,7,2.00),
(3,4,50,2.00),(3,8,4,18.00);

INSERT INTO sales (customer_id,sale_date,total_amount) VALUES
(1,'2026-10-05 10:30:00',25.00),
(2,'2026-10-05 11:15:00',18.00),
(3,'2026-10-06 12:00:00',10.00),
(1,'2026-10-07 14:00:00',7.00),
(2,'2026-10-08 15:00:00',10.00);
INSERT INTO sale_items (sale_id,batch_id,quantity,unit_price) VALUES
(1,1,10,2.50),(2,2,3,6.00),(3,5,2,5.00),(4,3,2,2.00),(5,4,2,3.50);

INSERT INTO stock_movements (batch_id,movement_type,quantity_change,notes) VALUES
(1,'PURCHASE',100,'Opening purchase'),(2,'PURCHASE',60,'Opening purchase'),
(3,'PURCHASE',8,'Opening purchase'),(4,'PURCHASE',50,'Opening purchase'),
(5,'PURCHASE',7,'Opening purchase'),(6,'PURCHASE',7,'Opening purchase'),
(7,'PURCHASE',9,'Opening purchase'),(8,'PURCHASE',4,'Opening purchase'),
(1,'SALE',-10,'Sample sale 1'),(2,'SALE',-3,'Sample sale 2'),
(5,'SALE',-2,'Sample sale 3'),(3,'SALE',-2,'Sample sale 4'),
(4,'SALE',-2,'Sample sale 5');

CREATE VIEW v_inventory AS
SELECT m.medicine_id,m.name AS medicine_name,m.category,m.manufacturer,
 b.batch_id,b.batch_number,b.purchase_price,b.selling_price,b.quantity,
 b.expiry_date,s.name AS supplier_name
FROM medicines m
JOIN medicine_batches b ON m.medicine_id=b.medicine_id
LEFT JOIN suppliers s ON b.supplier_id=s.supplier_id;

CREATE VIEW v_low_stock AS
SELECT m.medicine_id,m.name AS medicine_name,m.reorder_level,
 COALESCE(SUM(b.quantity),0) AS total_stock
FROM medicines m LEFT JOIN medicine_batches b ON m.medicine_id=b.medicine_id
GROUP BY m.medicine_id,m.name,m.reorder_level
HAVING COALESCE(SUM(b.quantity),0)<=m.reorder_level;

-- Useful checks/reports
SELECT * FROM v_inventory ORDER BY medicine_name;
SELECT * FROM v_low_stock ORDER BY total_stock;
SELECT medicine_name,batch_number,quantity,expiry_date
FROM v_inventory
WHERE expiry_date BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE,INTERVAL 90 DAY)
ORDER BY expiry_date;
SELECT COALESCE(SUM(total_amount),0) AS total_sales_revenue FROM sales;
SELECT COALESCE(SUM(total_amount),0) AS total_purchase_cost FROM purchases;
