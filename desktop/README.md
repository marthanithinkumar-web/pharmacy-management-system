# MedCare Pharmacy — Desktop GUI DBMS Project

This folder contains a **local desktop GUI** built with Python Tkinter and MySQL Connector/Python. It is separate from the existing Flask/SQLite web demonstration in the repository; it does not change or deploy the hosted website.

## Files
- `medcare_desktop.py` — Tkinter desktop application.
- `requirements.txt` — Python package dependency.
- `database/medcare_pharmacy_desktop.sql` — MySQL 8 schema and synthetic sample data.
- `docs/DESKTOP_GUI_PROJECT_REPORT.md` — editable project report draft.

## Setup on Windows 11
1. Install MySQL Server 8.0+ and Python 3.10+.
2. Open MySQL Workbench and run `database/medcare_pharmacy_desktop.sql` in a query tab. **This script drops and recreates tables in the database named `medcare_pharmacy`; do not run it if that database contains data you need.**
3. Open PowerShell in this folder:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   $env:MYSQL_HOST="127.0.0.1"
   $env:MYSQL_PORT="3306"
   $env:MYSQL_USER="root"
   $env:MYSQL_PASSWORD="YOUR_MYSQL_PASSWORD"
   $env:MYSQL_DATABASE="medcare_pharmacy"
   py medcare_desktop.py
   ```
4. The GUI opens with Dashboard, Medicines, Inventory, Low Stock, Near Expiry, Suppliers, Customers, Purchases and Sales tabs. Medicines, suppliers and customers have simple Add forms. Use Refresh after changes.

## Notes
- Tkinter is included with most standard Windows Python installations.
- The demo has no real patient data or prescription processing.
- Do not commit your MySQL password. Use environment variables as shown.
- The SQL uses synthetic names and email addresses.
- Actual database execution should be verified in MySQL Workbench before submission. Add genuine screenshots to your college report after running the GUI.
