"""MedCare Pharmacy desktop GUI (Tkinter + MySQL Connector/Python).

Configure MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
as environment variables, or edit the defaults below for a local student setup.
This app is a learning demo; use synthetic data only.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "medcare_pharmacy"),
}


class MedCareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MedCare Pharmacy — Desktop DBMS Project")
        self.geometry("1120x700")
        self.minsize(850, 520)
        self.configure(padx=12, pady=12)
        ttk.Label(self, text="MedCare Pharmacy", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="Desktop GUI • MySQL database • College demonstration").pack(anchor="w", pady=(0, 10))
        self.status = tk.StringVar(value="Connecting to MySQL…")
        ttk.Label(self, textvariable=self.status).pack(side="bottom", anchor="w", pady=(8, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        self.make_dashboard()
        self.make_table_tab("Medicines", "SELECT medicine_id,name,category,manufacturer,unit,reorder_level,prescription_required FROM medicines", refreshable=True)
        self.make_table_tab("Inventory", "SELECT medicine_name,batch_number,quantity,reorder_level,expiry_date,supplier_name FROM v_inventory LEFT JOIN medicines USING (medicine_id) ORDER BY medicine_name")
        self.make_table_tab("Low Stock", "SELECT medicine_name,total_stock,reorder_level FROM v_low_stock ORDER BY total_stock")
        self.make_table_tab("Near Expiry", "SELECT medicine_name,batch_number,quantity,expiry_date,supplier_name FROM v_inventory WHERE expiry_date BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE, INTERVAL 90 DAY) ORDER BY expiry_date")
        self.make_table_tab("Suppliers", "SELECT supplier_id,name,phone,email,address FROM suppliers", refreshable=True)
        self.make_table_tab("Customers", "SELECT customer_id,full_name,phone,email,address FROM customers", refreshable=True)
        self.make_table_tab("Purchases", "SELECT purchase_id,supplier_id,purchase_date,total_amount FROM purchases ORDER BY purchase_date DESC")
        self.make_table_tab("Sales", "SELECT s.sale_id,c.full_name AS customer,s.sale_date,s.total_amount FROM sales s LEFT JOIN customers c ON c.customer_id=s.customer_id ORDER BY s.sale_date DESC")
        self.after(100, self.refresh_all)

    def connect(self):
        return mysql.connector.connect(**DB_CONFIG)

    def query(self, sql, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description] if cur.description else []
            return columns, rows
        finally:
            conn.close()

    def make_dashboard(self):
        frame = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(frame, text="Dashboard")
        ttk.Label(frame, text="Inventory overview", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        self.dashboard_text = tk.Text(frame, height=12, wrap="word", state="disabled", font=("Consolas", 11))
        self.dashboard_text.pack(fill="both", expand=True, pady=10)
        ttk.Button(frame, text="Refresh dashboard", command=self.refresh_dashboard).pack(anchor="w")

    def make_table_tab(self, title, sql, refreshable=False):
        frame = ttk.Frame(self.tabs, padding=8)
        self.tabs.add(frame, text=title)
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Label(toolbar, text=title, font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=lambda: self.load_table(tree, sql)).pack(side="right")
        if title == "Medicines":
            ttk.Button(toolbar, text="Add medicine", command=self.add_medicine).pack(side="right", padx=5)
        if title == "Suppliers":
            ttk.Button(toolbar, text="Add supplier", command=self.add_supplier).pack(side="right", padx=5)
        if title == "Customers":
            ttk.Button(toolbar, text="Add customer", command=self.add_customer).pack(side="right", padx=5)
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(tree_frame, show="headings")
        ybar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        setattr(self, "tree_" + title.lower().replace(" ", "_"), tree)
        setattr(self, "sql_" + title.lower().replace(" ", "_"), sql)

    def load_table(self, tree, sql):
        try:
            columns, rows = self.query(sql)
            tree.delete(*tree.get_children())
            tree["columns"] = columns
            for col in columns:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=max(110, min(220, len(col) * 10)), anchor="w")
            for row in rows:
                tree.insert("", "end", values=[("" if v is None else str(v)) for v in row])
            self.status.set(f"Connected • {len(rows)} rows loaded")
        except Error as exc:
            self.status.set("Database connection/query failed")
            messagebox.showerror("MySQL error", f"{exc}\n\nCheck MySQL is running and run database/medcare_pharmacy_desktop.sql first.")

    def refresh_dashboard(self):
        try:
            _, medicines = self.query("SELECT COUNT(*) FROM medicines")
            _, stock = self.query("SELECT COALESCE(SUM(quantity),0) FROM medicine_batches")
            _, low = self.query("SELECT COUNT(*) FROM v_low_stock")
            _, expiry = self.query("SELECT COUNT(*) FROM medicine_batches WHERE expiry_date BETWEEN CURRENT_DATE AND DATE_ADD(CURRENT_DATE, INTERVAL 90 DAY)")
            _, revenue = self.query("SELECT COALESCE(SUM(total_amount),0) FROM sales")
            text = (
                f"Medicine types       : {medicines[0][0]}\n"
                f"Total units in stock : {stock[0][0]}\n"
                f"Low-stock medicines  : {low[0][0]}\n"
                f"Batches expiring in 90 days: {expiry[0][0]}\n"
                f"Demo sales revenue   : ₹{float(revenue[0][0]):,.2f}\n\n"
                "Use the tabs to inspect medicines, suppliers, customers, purchases, sales,\n"
                "low-stock items and near-expiry batches. Demo records are synthetic."
            )
            self.dashboard_text.configure(state="normal")
            self.dashboard_text.delete("1.0", "end")
            self.dashboard_text.insert("1.0", text)
            self.dashboard_text.configure(state="disabled")
            self.status.set("Dashboard refreshed")
        except Error as exc:
            self.status.set("MySQL connection failed")
            messagebox.showerror("Connection error", f"{exc}\n\nSee README.md for setup.")

    def refresh_all(self):
        self.refresh_dashboard()
        for name in ("medicines", "inventory", "low_stock", "near_expiry", "suppliers", "customers", "purchases", "sales"):
            tree = getattr(self, "tree_" + name)
            sql = getattr(self, "sql_" + name)
            self.load_table(tree, sql)

    def add_medicine(self):
        name = simpledialog.askstring("Add medicine", "Medicine name:")
        if not name or not name.strip():
            return
        category = simpledialog.askstring("Add medicine", "Category:", initialvalue="General") or "General"
        manufacturer = simpledialog.askstring("Add medicine", "Manufacturer:", initialvalue="Not specified") or "Not specified"
        unit = simpledialog.askstring("Add medicine", "Unit:", initialvalue="tablet") or "tablet"
        reorder = simpledialog.askinteger("Add medicine", "Reorder level:", minvalue=0, initialvalue=10)
        if reorder is None:
            return
        prescription = messagebox.askyesno("Prescription", "Is a prescription required?")
        try:
            conn = self.connect()
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO medicines (name,category,manufacturer,unit,reorder_level,prescription_required) VALUES (%s,%s,%s,%s,%s,%s)",
                            (name.strip(), category, manufacturer, unit, reorder, prescription))
                conn.commit()
            finally:
                conn.close()
            self.refresh_all()
        except Error as exc:
            messagebox.showerror("Could not add medicine", str(exc))

    def add_supplier(self):
        name = simpledialog.askstring("Add supplier", "Supplier name:")
        if not name or not name.strip():
            return
        phone = simpledialog.askstring("Add supplier", "Phone (optional):") or None
        email = simpledialog.askstring("Add supplier", "Email (optional):") or None
        address = simpledialog.askstring("Add supplier", "Address (optional):") or None
        try:
            conn = self.connect()
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO suppliers (name,phone,email,address) VALUES (%s,%s,%s,%s)", (name.strip(), phone, email, address))
                conn.commit()
            finally:
                conn.close()
            self.refresh_all()
        except Error as exc:
            messagebox.showerror("Could not add supplier", str(exc))

    def add_customer(self):
        name = simpledialog.askstring("Add customer", "Customer full name:")
        if not name or not name.strip():
            return
        phone = simpledialog.askstring("Add customer", "Phone (optional):") or None
        email = simpledialog.askstring("Add customer", "Email (optional):") or None
        address = simpledialog.askstring("Add customer", "Address (optional):") or None
        try:
            conn = self.connect()
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO customers (full_name,phone,email,address) VALUES (%s,%s,%s,%s)", (name.strip(), phone, email, address))
                conn.commit()
            finally:
                conn.close()
            self.refresh_all()
        except Error as exc:
            messagebox.showerror("Could not add customer", str(exc))


if __name__ == "__main__":
    try:
        app = MedCareApp()
        app.mainloop()
    except Error as exc:
        messagebox.showerror("MedCare Pharmacy", f"Unable to connect to MySQL: {exc}")
