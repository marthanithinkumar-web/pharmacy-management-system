# MedCare Pharmacy — DBMS Lab Project

A student-focused MedCare Pharmacy Management System demonstrating relational database design and CRUD workflows with **Python, Flask, and SQLite**. It is a learning/demo application, not a certified pharmacy or clinical system.

## Features
- Dashboard with inventory, low-stock and near-expiry summaries
- Medicine catalogue with batch number, expiry date, quantity, reorder level, purchase price and selling price
- Supplier and customer records
- Stock receiving / purchase entries
- Sales and itemized bills, with stock updated in a single database transaction
- Search medicines, view recent sales, and low-stock / expiry reports
- Database constraints, foreign keys, indexes, views, and a stock-movement audit table
- Automated tests for core routes and sale/stock behaviour

## Requirements
- Python 3.10+
- pip

## Run locally
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. The SQLite database is created automatically at `instance/pharmacy.db` and seeded with clearly labelled demo records on first run.

Optional environment variables:
- `SECRET_KEY`: Flask session secret (set a private value outside local demos)
- `DATABASE_PATH`: path to the SQLite database file

## Run tests
```bash
python -m unittest discover -s tests -v
```

## DBMS lab SQL files

The Flask web application still uses SQLite automatically. For the college lab terminal, use the separate **MySQL 8.0+ compatible** script:
- [database/medcare_mysql.sql](database/medcare_mysql.sql) — creates the practice database and tables, inserts sample data, creates simple views, and includes beginner/intermediate SQL practice queries.
- [database/schema.sql](database/schema.sql) — SQLite schema used by the Flask application.
- [docs/DBMS_NOTES.md](docs/DBMS_NOTES.md) — concepts and viva notes.

### Run the MySQL script on Windows
1. Open MySQL Command Line Client and log in.
2. Save/download `database/medcare_mysql.sql` to your computer.
3. At the `mysql>` prompt, run `SOURCE C:/full/path/to/medcare_mysql.sql;` and replace the example path with the actual file path.
4. When setup finishes, run the practice SELECT statements near the bottom of the file one at a time. They are commented out so they do not all execute during setup.
5. Check the output with `USE medcare_pharmacy;`, then `SHOW TABLES;`, then `SELECT * FROM medicines;`.

**Warning:** the MySQL setup script drops and recreates its named tables in `medcare_pharmacy`. Use it only for this practice project, because existing data in those tables will be deleted.

## DBMS coverage
The MySQL lab script covers CREATE TABLE, primary and foreign keys, CHECK and UNIQUE constraints, INSERT, SELECT, WHERE, LIKE, ORDER BY, aggregate functions, GROUP BY, HAVING, INNER JOIN, LEFT JOIN, subqueries, UNION, and views at a B.Tech 2nd-year introductory DBMS level.

## Project scope and safety
- Demo data is synthetic.
- No real prescriptions, patient medical records, payment gateway, or drug-interaction validation are implemented.
- This is not a substitute for pharmacist review, regulatory compliance, or production security.
- Before production use, add authentication/roles, CSRF protection, migrations, backups, stronger validation, audit controls and a production database.

## Project information
- Project title: **MedCare Pharmacy**
- Project number: **13**
- Course: **DBMS Laboratory (DBMSL)**
- Student/faculty/roll-number details are intentionally not fabricated; enter them in the college report where required.
