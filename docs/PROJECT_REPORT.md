# Pharmacy Management System — Project Report Draft

**Project No.:** 13  
**Course:** DBMS Laboratory (DBMSL)  
**Academic year:** 2026–2027

> Fill only your real student name, roll number, team number, faculty name and required institution fields in the official college template. Add genuine screenshots after running the app. Keep the original template's pages, layout, headings, and submission guidelines unchanged; replace subject-specific text only.

## Abstract
The Pharmacy Management System maintains medicine details, batch-wise inventory, suppliers, customers, purchase entries and sales invoices in a relational database. It helps users view current stock, identify low-stock medicines and locate batches approaching expiry. A sale is recorded as a transaction so bill rows and stock deductions succeed or fail together.

## Problem statement
Manual stock and billing records can lead to duplicate entries, incorrect totals and poor visibility into batch expiry. This project models pharmacy operations using normalized relational tables, integrity constraints, joins, aggregate queries and transactional updates.

## Objectives
1. Design a relational database for medicines, batches, suppliers, customers, purchases and sales.
2. Demonstrate primary/foreign keys and data validation constraints.
3. Implement stock receiving, billing and inventory reports.
4. Apply transactions to prevent partial sales and negative stock.
5. Test common and invalid workflows.

## Software requirements
- Python 3.10+
- Flask
- SQLite 3
- Web browser
- Code editor

## Modules
1. Dashboard
2. Medicine and batch inventory
3. Supplier management
4. Customer management
5. Stock receiving
6. Sales and billing
7. Low-stock and expiry reports

## Testing
Run `python -m unittest discover -s tests -v`. Record the actual output and insert genuine screenshots in the college template. Do not claim screenshots or test runs that were not performed.

## Limitations
This is a student demonstration, not a production pharmacy platform. Authentication, real payment processing, prescription workflows, regulated medicine checks and clinical decision support are outside the current scope.

## Conclusion
The project demonstrates relational design and a usable application around stock and billing. Database constraints and transactions help maintain consistency while reports provide basic inventory visibility.

## References
- Python documentation: https://docs.python.org/3/
- Flask documentation: https://flask.palletsprojects.com/
- SQLite documentation: https://www.sqlite.org/docs.html
