# MedCare Pharmacy — Complete DBMS Project Details

> Consolidated reference for the college DBMS Lab / Course-End Project. Details below are based on recorded project context and are not a fresh live verification.

## 1. Project identity
- Project: MedCare Pharmacy — Pharmacy Management System
- Academic context: B.Tech 2nd year, 1st semester; CSD branch; DBMS Lab / Course-End Project (project 13 in the user's coursework context).
- GitHub: https://github.com/marthanithinkumar-web/pharmacy-management-system
- Recorded live URL: https://medcare-pharmacy.onrender.com/
- Purpose: a GUI-based pharmacy system for medicine records, suppliers, customers, stock receiving, sales, and reports.

## 2. Problem and objectives
Pharmacies need a consistent way to maintain medicine details, supplier/customer records, quantities, batches, expiry dates, purchases, and sales. MedCare Pharmacy brings these workflows into one database-backed interface.

Objectives:
1. Maintain medicine catalogue information.
2. Maintain supplier and customer records.
3. Record purchases and incoming stock.
4. Track batch quantities and expiry information where implemented.
5. Record sales and sale line items.
6. Provide inventory, low-stock, expiry, and sales reports.
7. Demonstrate relational database design, keys, joins, views, and queries.

## 3. Technology and deployment context
- Backend: Python with Flask.
- UI: HTML, CSS, JavaScript.
- Recorded production database: SQLite-style application database; verify current source before claiming this is still the active configuration.
- Classroom SQL version: MySQL-compatible script, recorded as database/medcare_mysql.sql; verify the current path in the repository.
- Hosting: Render. Recorded install command: pip install -r requirements.txt. Recorded start command: gunicorn app:app.
- Repository: GitHub.

### Important database distinction
The deployed web app and the classroom MySQL script are separate contexts. Do not claim they share the same database unless current source confirms it. The recorded MySQL reset script includes DROP VIEW / DROP TABLE operations. Use only in a local test database after reviewing it; never run it against production data.

## 4. Recorded UI navigation
- Dashboard
- Medicine
- Suppliers
- Customers
- Receive stock
- New sale
- Reports

The product name is MedCare Pharmacy. The user requested that the app UI not include “DBMS” in the product name and that old learning/demo disclaimers and taglines be removed. Academic classification belongs in the report.

## 5. Feature overview
- Dashboard: landing view for key operations and summary information.
- Medicine catalogue: maintain medicine details used by inventory and sales.
- Supplier management: maintain supplier records associated with purchases.
- Customer management: maintain customer records where the app uses them.
- Receive stock: record incoming stock and purchase details.
- Batch and expiry tracking: maintain batch-level quantity/expiry information where implemented; a 90-day expiry window was discussed.
- New sale / billing: record sales and line items; verify totals and stock decrement in current code.
- Reports: intended scope includes inventory, low-stock, expiry-related items, and sales.

These are recorded/intended capabilities. Verify each one in the current repository and running app before claiming a successful test.

## 6. Recorded MySQL schema overview
Tables recorded in the classroom schema:
- suppliers — supplier details
- customers — customer details
- medicines — medicine catalogue
- medicine_batches — batch quantities and expiry details
- purchases — purchase/stock receipt header
- purchase_items — items included in a purchase
- sales — sale/billing header
- sale_items — items included in a sale
- stock_movements — inventory movement history

Recorded views: v_inventory and v_low_stock.

This list is a high-level overview, not a substitute for the exact DDL. For submission, use the actual column names, data types, primary/foreign keys, constraints, and view definitions from the current SQL file. Do not guess column names.

## 7. DBMS concepts to explain
- Primary keys uniquely identify records.
- Foreign keys connect related records.
- One-to-many relationships may connect purchase headers to purchase items and sale headers to sale items; confirm actual foreign keys.
- Joins combine related information for reports.
- Aggregate functions can summarize quantities and sales where implemented.
- Views provide reusable query definitions; explain v_inventory and v_low_stock using the actual SQL.
- Transactions should keep related sale and inventory updates consistent if supported by the implementation.
- Constraints and input validation help prevent invalid records where defined.

## 8. Illustrative SQL
These are teaching examples only. Confirm the tables/views and exact column names in the current script before running.

    SELECT * FROM medicines;
    SELECT * FROM v_inventory;
    SELECT * FROM v_low_stock;

Do not assume a primary key is named id. Always check the actual schema first.

## 9. Typical demo workflows
### Receive stock
1. Open Receive stock.
2. Select supplier and medicine/batch information supported by the UI.
3. Enter quantity and required purchase/expiry details.
4. Save and verify the inventory change in the UI/database.

### Create a sale
1. Open New sale.
2. Add medicine line items and quantities.
3. Check the displayed total.
4. Save and verify the sale records and stock behavior.

### Review reports
1. Open Reports.
2. Show inventory and low-stock data.
3. Show expiry-related data.
4. Show sales results and explain the supporting tables/views.

These are demonstration plans, not proof that the workflows have already passed testing.

## 10. Testing checklist
Record actual results and date; do not mark a test as passed before running it.
- App opens without an unhandled error.
- If /health exists, it returns the expected healthy response and database check.
- Medicine records can be saved and retrieved.
- Supplier records can be saved and retrieved.
- Customer records can be saved and retrieved.
- Receiving stock changes inventory as expected.
- Sales and line items save; totals and stock changes are correct.
- Low-stock report matches the implemented threshold.
- Expiry report matches the implemented window.
- Invalid inputs show understandable feedback.
- Database failures are handled safely.
- Live deployment and core workflows are checked.

Suggested report evidence: dashboard, medicine, receive-stock, new-sale and reports screenshots; verified ER diagram; local SQL output; dated test table. Do not fabricate screenshots, performance numbers, or test results.

## 11. ER diagram guidance
Build the final ER diagram from actual DDL. Relationships to check include Supplier → Purchases, Purchase → Purchase items, Medicine → Purchase items, Medicine → Medicine batches, Customer → Sales if implemented, Sale → Sale items, Medicine → Sale items, and stock movements to the relevant medicine/batch/transaction references. Use actual foreign-key columns and cardinalities; omit relationships not implemented.

## 12. Deployment notes
- Recorded app URL: https://medcare-pharmacy.onrender.com/
- Recorded Render dashboard: https://dashboard.render.com/web/srv-db5nse4s728c738f4a90
- Recorded health endpoint: /health, described as executing SELECT 1 and returning JSON health information.
- Recorded workflow: .github/workflows/keep-awake.yml, scheduled as best-effort every 10 minutes.

The keep-awake workflow does not guarantee uptime. Recheck the current Render deployment, commit, HTTP response, and database behavior before claiming current health.

## 13. Limitations and accuracy rules
- The classroom MySQL script and deployed application's database may differ.
- Verify current schema, UI fields, validation, and transaction behavior against source.
- A successful deployment does not prove every feature works.
- Test outcomes and screenshots must come from real execution.
- Avoid destructive SQL against production; back up data before any intentional reset.

## 14. Suggested college report structure
Preserve the supplied college template and its layout. Suggested sections:
1. Cover page
2. Certificate and acknowledgement
3. Index
4. Abstract
5. Introduction and problem statement
6. Objectives and scope
7. Requirements and technology stack
8. System architecture
9. Database design and ER diagram
10. Relational schema and constraints
11. SQL commands and queries
12. GUI modules and workflows
13. Testing and actual results
14. Screenshots
15. Limitations and future enhancements
16. Conclusion
17. References / appendix

Use the required “DBMS Lab” wording in the report while keeping the in-app brand as MedCare Pharmacy.

## 15. Viva questions
1. What problem does the project solve?
2. Why use a relational database?
3. What are the primary and foreign keys in the actual schema?
4. Why are purchase items and sale items separate from header records?
5. What is batch tracking used for?
6. What is a view? Explain v_inventory and v_low_stock.
7. Which joins support the reports?
8. How should sale and inventory changes remain consistent?
9. How are low-stock and near-expiry items identified?
10. What is the difference between the deployed database and the classroom MySQL script?
11. How do you test invalid input and database errors?
12. What are the current limitations and possible improvements?

Answer using the actual source and SQL rather than generic assumptions.

## 16. References
- Repository: https://github.com/marthanithinkumar-web/pharmacy-management-system
- Recorded live application: https://medcare-pharmacy.onrender.com/
- Recorded Render dashboard: https://dashboard.render.com/web/srv-db5nse4s728c738f4a90
- Recorded workflow: https://github.com/marthanithinkumar-web/pharmacy-management-system/blob/main/.github/workflows/keep-awake.yml

Last consolidated from recorded project context: 26 October 2026. This is not a live verification timestamp.