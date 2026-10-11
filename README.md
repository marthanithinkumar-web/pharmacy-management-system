# Pharmacy Management System — DBMS Lab Project

A student-focused Pharmacy Management System demonstrating relational database design and CRUD workflows with **Python, Flask, and SQLite**. It is a learning/demo application, not a certified pharmacy or clinical system.

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

## DBMS coverage
See [database/schema.sql](database/schema.sql) and [docs/DBMS_NOTES.md](docs/DBMS_NOTES.md) for entities, relationships, normalization notes, SQL examples, transactions, indexes, and viva points.

## Project scope and safety
- Demo data is synthetic.
- No real prescriptions, patient medical records, payment gateway, or drug-interaction validation are implemented.
- This is not a substitute for pharmacist review, regulatory compliance, or production security.
- Before production use, add authentication/roles, CSRF protection, migrations, backups, stronger validation, audit controls and a production database.

## Project information
- Project title: **Pharmacy Management System**
- Project number: **13**
- Course: **DBMS Laboratory (DBMSL)**
- Student/faculty/roll-number details are intentionally not fabricated; enter them in the college report where required.
