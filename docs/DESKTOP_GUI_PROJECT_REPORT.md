# MedCare Pharmacy Management System
## Course-End Project Report — Desktop GUI and MySQL DBMS

**Project title:** MedCare Pharmacy Management System  
**Project type:** DBMS college project with desktop graphical user interface  
**Academic year:** 2026–2027  
**Student name:** ____________________  
**Roll number:** ____________________  
**Branch / semester:** ____________________  
**Faculty guide:** ____________________  
**Institution:** ____________________

> Fill in your own details and transfer this content into the required college report template. Do not invent student, faculty, or institute details. Insert screenshots captured from your own successful run; no test screenshots are included in this draft.

## Certificate
This is to certify that the project titled **MedCare Pharmacy Management System** was prepared as part of the DBMS course requirements by the student named above. The final certificate must be completed and signed by the authorized faculty member according to the institution's rules.

## Acknowledgement
I would like to thank my faculty guide and institution for the opportunity to learn relational database design and application development through this project. I also acknowledge the official Python, Tkinter and MySQL documentation used during development.

## Abstract
MedCare Pharmacy Management System is a small desktop application designed to demonstrate pharmacy inventory data management using a relational MySQL database and a Python Tkinter graphical user interface. It stores medicine details, batch-level stock and expiry dates, supplier information, customer information, purchases and sales. The interface provides a dashboard and separate views for inventory, low stock, batches nearing expiry, suppliers, customers, purchases and sales. It is an educational prototype that uses synthetic demonstration data.

## 1. Introduction
Maintaining medicine and batch records manually can make it difficult to review current stock, identify items below their reorder level, and notice batches approaching their expiry date. This project demonstrates how a relational database and a desktop GUI can organize these records in a consistent, queryable form.

## 2. Problem Statement
A small pharmacy needs a structured way to store medicine, supplier, customer, purchase, sales and batch details. Manual records may be duplicated or become inconsistent. The project addresses this learning problem through relational tables, primary and foreign keys, views, SQL joins and summary queries.

## 3. Objectives
1. Design a relational database for medicines, batches, suppliers, customers, purchases and sales.
2. Apply primary keys, foreign keys and appropriate data types.
3. Display data through a simple desktop GUI.
4. Identify low-stock medicines using reorder levels.
5. Identify batches expiring within the next 90 days.
6. Demonstrate basic SQL reporting and database connectivity from Python.

## 4. Scope
The application is intended for a classroom demonstration with synthetic data. It provides read-only reports for inventory, low stock, expiry, purchases and sales. Basic Add forms are included for medicines, suppliers and customers. Full point-of-sale billing, real prescriptions, payment processing, user roles and regulatory checks are outside this version's scope.

## 5. Software and Hardware Requirements
- Operating system: Windows 10/11 or another OS supporting Python and MySQL
- Python 3.10 or later
- MySQL Server 8.0 or later
- MySQL Connector/Python
- Tkinter GUI toolkit
- MySQL Workbench (recommended for running and inspecting SQL)
- Minimum 4 GB RAM recommended for a normal student development computer

## 6. System Design
### 6.1 Architecture
The user interacts with the Tkinter desktop interface. Python sends SQL statements through MySQL Connector/Python. MySQL stores relational records and computes report views/queries. Results are shown in table grids and the dashboard.

### 6.2 Main Tables
- **suppliers**: supplier contact details.
- **customers**: customer contact details.
- **medicines**: medicine name, category, manufacturer, unit, reorder level and prescription flag.
- **medicine_batches**: batch number, supplier, prices, remaining quantity and expiry date.
- **purchases / purchase_items**: purchase header and item rows.
- **sales / sale_items**: sales header and item rows.
- **stock_movements**: purchase, sale and adjustment audit entries.

### 6.3 Relationships
One supplier can supply many batches and purchases. One medicine can have multiple batches. A purchase has multiple purchase-item rows, and a sale has multiple sale-item rows. Each batch can be referenced by purchase items, sale items and stock movements. Customers can be linked to many sales.

### 6.4 Views
- `v_inventory`: joins medicines, batches and suppliers to show inventory detail.
- `v_low_stock`: groups stock by medicine and filters totals at or below the reorder level.

## 7. Modules
1. **Dashboard:** total medicine types, total units, low-stock count, near-expiry count and sample sales revenue.
2. **Medicines:** displays the medicine catalogue and supports adding a medicine.
3. **Inventory:** shows batch-level quantities, prices, expiry dates and supplier names.
4. **Low Stock:** lists medicines whose total quantity is at or below their reorder level.
5. **Near Expiry:** shows batches expiring within 90 days from the current date.
6. **Suppliers and Customers:** lists records and supports adding records.
7. **Purchases and Sales:** displays sample transaction summaries.

## 8. Database Concepts Demonstrated
The SQL script demonstrates CREATE DATABASE, CREATE TABLE, primary keys, foreign keys, INSERT, SELECT, JOIN, GROUP BY, aggregate functions, WHERE, date filtering and views. The GUI demonstrates parameterized INSERT statements, database connectivity and refreshing query results.

## 9. Procedure to Run
1. Install Python and MySQL Server.
2. Open `database/medcare_pharmacy_desktop.sql` in MySQL Workbench and execute it in a clean practice database. The script drops and recreates the named project's tables; back up any data first.
3. Install the Python dependency with `pip install -r requirements.txt`.
4. Set the `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` and `MYSQL_DATABASE` environment variables.
5. Run `python medcare_desktop.py`.
6. Review the dashboard and each tab. Add a sample medicine/supplier/customer if needed.
7. Capture genuine screenshots and place them in the final report template.

## 10. Testing Plan
| Test | Action | Expected result |
|---|---|---|
| DB connection | Start GUI with valid MySQL settings | Dashboard and tables load |
| Medicine list | Open Medicines tab | Medicine rows display |
| Add medicine | Use Add medicine with valid values | New medicine is saved and visible |
| Supplier entry | Add a supplier | Supplier is saved and visible |
| Customer entry | Add a customer | Customer is saved and visible |
| Low stock | Open Low Stock | Stock at/below reorder level is listed |
| Near expiry | Open Near Expiry | Batches within 90 days are listed |
| Invalid connection | Use incorrect credentials | A connection error is shown |

**Testing status:** This report is a draft. Mark each test as Pass/Fail only after you run it. Add screenshots from the actual run; do not claim tests passed before verifying them.

## 11. Limitations and Future Enhancements
This student prototype uses synthetic data and does not implement a complete billing workflow or role-based authentication. Future improvements could include safe purchase and sales forms with transactions, stock updates, printable invoices, input validation, edit/delete controls, database backups and user roles. It must not be used as a production pharmacy or clinical system without substantial review and security work.

## 12. Conclusion
MedCare Pharmacy demonstrates how MySQL tables, relationships, views and report queries can support a desktop application. The Tkinter interface makes the data easier to inspect while keeping the database concepts visible for a DBMS course demonstration.

## References
1. Python documentation — https://docs.python.org/3/
2. Tkinter documentation — https://docs.python.org/3/library/tkinter.html
3. MySQL 8.0 Reference Manual — https://dev.mysql.com/doc/refman/8.0/en/
4. MySQL Connector/Python documentation — https://dev.mysql.com/doc/connector-python/en/
