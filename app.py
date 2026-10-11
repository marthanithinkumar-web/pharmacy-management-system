import os
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta
from uuid import uuid4
from flask import Flask, g, request, redirect, url_for, flash, render_template_string, jsonify

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", ROOT / "instance" / "pharmacy.db"))
SCHEMA = ROOT / "database" / "schema.sql"
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local-demo-change-me")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
        g.db.execute("PRAGMA busy_timeout=10000")
    return g.db

@app.teardown_appcontext
def close_db(_err=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()

def init_db(seed=True):
    """Create the schema and add clearly labelled demonstration records idempotently."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    if seed:
        # Suppliers and customers make every menu page useful on first launch.
        for name, phone, email, address in [
            ("Demo Medical Distributors", "9000000001", "supplier1@example.test", "Demo address — not a real supplier"),
            ("Sample Health Supplies", "9000000002", "supplier2@example.test", "Demo address — not a real supplier"),
            ("Training Pharma Wholesale", "9000000003", "supplier3@example.test", "Demo address — not a real supplier"),
        ]:
            if not conn.execute("SELECT 1 FROM suppliers WHERE name=?", (name,)).fetchone():
                conn.execute("INSERT INTO suppliers(name,phone,email,address) VALUES(?,?,?,?)", (name,phone,email,address))
        supplier_rows = {r[1]: r[0] for r in conn.execute("SELECT supplier_id,name FROM suppliers")}
        for name, phone in [
            ("Demo Walk-in Customer", "9000010001"),
            ("Sample Customer A", "9000010002"),
            ("Sample Customer B", "9000010003"),
            ("Training Customer C", "9000010004"),
        ]:
            if not conn.execute("SELECT 1 FROM customers WHERE full_name=?", (name,)).fetchone():
                conn.execute("INSERT INTO customers(full_name,phone) VALUES(?,?)", (name,phone))

        # Seed only named demo products/batches; never overwrite actual stock quantities.
        demo_medicines = [
            ("Paracetamol 500 mg","Analgesic","Demo Pharma","strip",20,100,10,15,"DEMO-PAR-001","2028-12-31"),
            ("Cetirizine 10 mg","Antihistamine","Demo Pharma","strip",12,45,8,12,"DEMO-CET-001","2028-11-30"),
            ("ORS Sachet","Rehydration","Demo Labs","piece",10,80,4,7,"DEMO-ORS-001","2028-10-31"),
            ("Vitamin C 500 mg","Supplement demo","Demo Labs","strip",15,8,12,18,"DEMO-VTC-001","2028-09-30"),
            ("Antacid Tablets","Antacid demo","Training Pharma","strip",12,6,9,14,"DEMO-ANT-001","2026-11-15"),
            ("Cough Syrup 100 ml","Cough relief demo","Demo Pharma","bottle",10,30,25,38,"DEMO-CSY-001","2026-12-05"),
            ("Bandage Roll","First-aid demo","Sample Health Supplies","roll",8,50,7,12,"DEMO-BAN-001","2028-06-30"),
            ("Saline Nasal Spray","Nasal care demo","Sample Health Supplies","bottle",8,24,18,28,"DEMO-SNS-001","2027-05-31"),
        ]
        # Extra dashboard training rows: several low-stock medicines plus batches
        # expiring soon. Relative dates keep the 90-day panel populated over time.
        demo_medicines.extend([
            ("Ibuprofen 200 mg", "Pain relief demo", "Demo Pharma", "strip", 18, 5, 11, 17, "DEMO-IBU-001", (date.today() + timedelta(days=18)).isoformat()),
            # Most demo products intentionally have healthy stock and expiry dates beyond 90 days.
            ("Loratadine 10 mg", "Allergy care demo", "Demo Labs", "strip", 15, 34, 9, 14, "DEMO-LOR-001", (date.today() + timedelta(days=145)).isoformat()),
            ("Zinc Tablets", "Supplement demo", "Training Pharma", "strip", 20, 47, 6, 10, "DEMO-ZNC-001", (date.today() + timedelta(days=210)).isoformat()),
            ("Antiseptic Solution 100 ml", "First-aid demo", "Sample Health Supplies", "bottle", 10, 32, 20, 30, "DEMO-ANTISEP-001", (date.today() + timedelta(days=260)).isoformat()),
            ("Eye Lubricant Drops", "Eye care demo", "Demo Labs", "bottle", 12, 6, 22, 32, "DEMO-EYE-001", (date.today() + timedelta(days=26)).isoformat()),
            ("Throat Lozenges", "Throat care demo", "Demo Pharma", "strip", 14, 39, 7, 11, "DEMO-THR-001", (date.today() + timedelta(days=180)).isoformat()),
            ("Digestive Enzyme Tablets", "Digestive care demo", "Training Pharma", "strip", 16, 44, 13, 20, "DEMO-DIG-001", (date.today() + timedelta(days=300)).isoformat()),
            ("Gauze Pads", "First-aid demo", "Sample Health Supplies", "pack", 12, 29, 8, 13, "DEMO-GAU-001", (date.today() + timedelta(days=240)).isoformat()),
            # Three additional low-stock examples with uneven quantities and later expiry dates.
            ("Cotton Roll", "First-aid demo", "Sample Health Supplies", "roll", 12, 3, 5, 9, "DEMO-COT-001", (date.today() + timedelta(days=180)).isoformat()),
            ("Thermometer Strips", "Health monitoring demo", "Demo Labs", "pack", 20, 9, 8, 14, "DEMO-THERM-001", (date.today() + timedelta(days=150)).isoformat()),
            ("Hand Sanitizer 100 ml", "Hygiene demo", "Demo Pharma", "bottle", 24, 13, 12, 20, "DEMO-SAN-001", (date.today() + timedelta(days=200)).isoformat()),
            # Two additional near-expiry batches that still have healthy stock levels.
            ("Calamine Lotion 100 ml", "Skin care demo", "Demo Labs", "bottle", 8, 27, 14, 22, "DEMO-CAL-001", (date.today() + timedelta(days=42)).isoformat()),
            ("Multivitamin Syrup 200 ml", "Supplement demo", "Training Pharma", "bottle", 10, 36, 18, 28, "DEMO-MVS-001", (date.today() + timedelta(days=70)).isoformat()),
        ])
        for name, category, maker, unit, reorder, qty, cost, price, batch, expiry in demo_medicines:
            row = conn.execute("SELECT medicine_id FROM medicines WHERE name=?", (name,)).fetchone()
            if row:
                mid = row[0]
            else:
                conn.execute("INSERT INTO medicines(name,category,manufacturer,unit,reorder_level) VALUES(?,?,?,?,?)",
                             (name,category,maker,unit,reorder))
                mid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            existing_batch = conn.execute("SELECT batch_id FROM medicine_batches WHERE medicine_id=? AND batch_number=?", (mid,batch)).fetchone()
            if not existing_batch:
                supplier_name = ("Training Pharma Wholesale" if name == "Antacid Tablets" else
                                 "Sample Health Supplies" if name in ("Bandage Roll","Saline Nasal Spray","Vitamin C 500 mg","Antiseptic Solution 100 ml","Gauze Pads") else
                                 "Demo Medical Distributors")
                sid = supplier_rows.get(supplier_name)
                conn.execute("""INSERT INTO medicine_batches(medicine_id,supplier_id,batch_number,expiry_date,quantity,purchase_price,selling_price)
                                 VALUES(?,?,?,?,?,?,?)""", (mid,sid,batch,expiry,qty,cost,price))
                bid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.execute("INSERT INTO stock_movements(batch_id,movement_type,quantity_change,reference_text) VALUES(?,?,?,?)",
                             (bid,"PURCHASE",qty,"DEMO-SEED — sample data"))
                purchase_invoice = "DEMO-PUR-" + batch
                conn.execute("INSERT OR IGNORE INTO purchases(supplier_id,invoice_number,total_amount) VALUES(?,?,?)",
                             (sid,purchase_invoice,qty*cost))
                purchase_id = conn.execute("SELECT purchase_id FROM purchases WHERE invoice_number=?", (purchase_invoice,)).fetchone()[0]
                if not conn.execute("SELECT 1 FROM purchase_items WHERE purchase_id=? AND batch_id=?", (purchase_id,bid)).fetchone():
                    conn.execute("INSERT INTO purchase_items(purchase_id,batch_id,quantity,unit_cost,line_total) VALUES(?,?,?,?,?)",
                                 (purchase_id,bid,qty,cost,qty*cost))
            else:
                # Refresh only untouched, explicitly seeded demo batches. Never overwrite batches
                # that have been sold from or manually adjusted by the user.
                bid = existing_batch[0]
                is_demo_seed = conn.execute(
                    "SELECT 1 FROM stock_movements WHERE batch_id=? AND reference_text LIKE 'DEMO-SEED%'",
                    (bid,)
                ).fetchone()
                has_sales = conn.execute("SELECT 1 FROM sale_items WHERE batch_id=? LIMIT 1", (bid,)).fetchone()
                has_adjustments = conn.execute(
                    "SELECT 1 FROM stock_movements WHERE batch_id=? AND movement_type='ADJUSTMENT' LIMIT 1",
                    (bid,)
                ).fetchone()
                if is_demo_seed and not has_sales and not has_adjustments:
                    conn.execute(
                        "UPDATE medicine_batches SET expiry_date=?, quantity=?, purchase_price=?, selling_price=? WHERE batch_id=?",
                        (expiry, qty, cost, price, bid)
                    )
                    conn.execute(
                        "UPDATE medicines SET reorder_level=? WHERE medicine_id=?",
                        (reorder, mid)
                    )
        # Clearly labelled sample invoice keeps reports populated on a fresh demo install.
        if conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0:
            batch = conn.execute("SELECT batch_id,quantity,selling_price FROM medicine_batches WHERE batch_number='DEMO-PAR-001' AND expiry_date>=date('now')").fetchone()
            customer = conn.execute("SELECT customer_id FROM customers WHERE full_name='Demo Walk-in Customer'").fetchone()
            if batch and batch[1] >= 2 and customer:
                invoice = "DEMO-SALE-001"
                total = round(float(batch[2]) * 2, 2)
                conn.execute("INSERT INTO sales(customer_id,invoice_number,total_amount) VALUES(?,?,?)", (customer[0],invoice,total))
                sale_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.execute("INSERT INTO sale_items(sale_id,batch_id,quantity,unit_price,line_total) VALUES(?,?,?,?,?)", (sale_id,batch[0],2,batch[2],total))
                conn.execute("UPDATE medicine_batches SET quantity=quantity-2 WHERE batch_id=?", (batch[0],))
                conn.execute("INSERT INTO stock_movements(batch_id,movement_type,quantity_change,reference_text) VALUES(?,?,?,?)", (batch[0],"SALE",-2,invoice+" — demo"))
        conn.commit()
    conn.close()

# Initialize schema and demo inventory when the web server imports this module.
init_db()

STYLE = """
body{margin:0;background:linear-gradient(135deg,#eaf6f2,#f5f8fb 55%,#edf3ff);color:#173b36;font:15px/1.55 system-ui,Segoe UI,sans-serif;min-height:100vh}
header{background:linear-gradient(110deg,#fff,#e2f6ef);border-bottom:1px solid #cce3dc;padding:16px max(16px,calc((100% - 1180px)/2));display:flex;gap:18px;flex-wrap:wrap;align-items:center;box-shadow:0 3px 16px #174b3b0b}
.brand{font-size:22px;font-weight:900;color:#056b58;text-decoration:none;margin-right:auto;letter-spacing:-.4px}
nav{display:flex;gap:6px;flex-wrap:wrap}nav a{color:#294b46;text-decoration:none;font-weight:700;padding:8px 10px;border-radius:8px}nav a:hover{background:#d5eee6;color:#075c4d}
main{max-width:1180px;margin:28px auto;padding:0 20px}h1{font-size:30px;letter-spacing:-.6px;margin:0 0 8px;color:#143f37}h2{font-size:20px;color:#174c41;margin:24px 0 12px}
.muted{color:#627b75}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px;margin:22px 0}
.card,.panel{background:rgba(255,255,255,.96);border:1px solid #d5e8e1;border-radius:16px;padding:18px;margin:14px 0;box-shadow:0 8px 22px #194d3b0b}
.metric{font-size:30px;font-weight:900;color:#08715d;letter-spacing:-.6px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}
button,.btn{background:linear-gradient(135deg,#08715d,#0a8b71);color:white;border:0;border-radius:10px;padding:11px 16px;font:inherit;font-weight:750;text-decoration:none;cursor:pointer;box-shadow:0 4px 10px #08715d20}
input,select{width:100%;padding:10px;border:1px solid #c7d4d1;border-radius:8px;background:white;font:inherit;box-sizing:border-box}
label{display:block;font-weight:650;margin:10px 0 5px}.form{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.tablewrap{overflow:auto;border:1px solid #dce5e3;border-radius:10px;background:white}table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:10px;border-bottom:1px solid #e6ecea}th{background:#eaf5f1;color:#28564d;font-size:13px}tr:last-child td{border-bottom:0}.stockbar{height:8px;background:#e1eee9;border-radius:99px;overflow:hidden;min-width:80px}.stockbar span{display:block;height:100%;background:linear-gradient(90deg,#0a8a70,#6ac6a4);border-radius:99px}.hero{background:linear-gradient(120deg,#075f50,#0a8b71 62%,#57b99a);color:white;border-radius:20px;padding:26px 28px;box-shadow:0 12px 28px #075f5026;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}.hero h1{color:white;font-size:32px;margin:0}.hero p{color:#d9f5eb;margin:6px 0 0}.hero-tag{background:#ffffff22;border:1px solid #ffffff45;border-radius:12px;padding:12px 16px;font-weight:750}.section-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.empty-note{padding:15px;color:#627b75;background:#f8fbfa}
.flash{padding:12px;background:#e5f5ee;color:#075b49;border-radius:8px;margin:12px 0}.error{background:#fff0ed;color:#9b2116}
footer{max-width:1100px;margin:30px auto;padding:12px 16px;color:#667772;font-size:13px}
@media(max-width:600px){header{padding:14px}main{padding:0 14px;margin:18px auto}h1{font-size:25px}.hero{padding:22px}.hero h1{font-size:27px}.metric{font-size:27px}nav{gap:3px}nav a{padding:7px 8px}}
"""
SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{title}} · MedCare Pharmacy</title><style>{{style}}</style></head><body>
<header><a class="brand" href="/">✚ MedCare Pharmacy</a><nav>
<a href="/">Dashboard</a><a href="/medicines">Medicines</a><a href="/suppliers">Suppliers</a><a href="/customers">Customers</a><a href="/receive">Receive stock</a><a href="/sale">New sale</a><a href="/reports">Reports</a><a href="/sql-lab">SQL Lab</a></nav></header>
<main>{% with msgs=get_flashed_messages(with_categories=true) %}{% for cat,msg in msgs %}<div class="flash {{'error' if cat=='error' else ''}}">{{msg}}</div>{% endfor %}{% endwith %}{{body|safe}}</main>
<footer></footer></body></html>"""

def page(title, body, **ctx):
    return render_template_string(SHELL, title=title, style=STYLE, body=render_template_string(body, **ctx))

@app.route("/")
def dashboard():
    c=db()
    metrics={
      "medicines":c.execute("SELECT COUNT(*) FROM medicines").fetchone()[0],
      "batches":c.execute("SELECT COUNT(*) FROM medicine_batches").fetchone()[0],
      "stock":c.execute("SELECT COALESCE(SUM(quantity),0) FROM medicine_batches WHERE expiry_date>=date('now')").fetchone()[0],
      "sales":c.execute("SELECT COALESCE(SUM(total_amount),0) FROM sales WHERE date(sale_date)=date('now')").fetchone()[0]}
    inventory=c.execute("SELECT * FROM v_inventory ORDER BY available_stock DESC,medicine_name").fetchall()
    low=c.execute("SELECT * FROM v_low_stock ORDER BY available_stock,medicine_name").fetchall()
    exp=c.execute("SELECT * FROM v_expiring_batches ORDER BY expiry_date").fetchall()
    return page("Dashboard","""<section class="hero"><div><h1>Dashboard</h1></div><div class="hero-tag">✚ MedCare Pharmacy <span style="display:block;font-size:12px;font-weight:500;opacity:.9">Pharmacy management</span></div></section>
    <div class="grid"><div class="card"><div class="muted">Medicine types</div><div class="metric">{{m.medicines}}</div><div class="muted">In your catalogue</div></div><div class="card"><div class="muted">Tracked batches</div><div class="metric">{{m.batches}}</div><div class="muted">Batch records</div></div>
    <div class="card"><div class="muted">Available stock</div><div class="metric">{{m.stock}}</div><div class="muted">Valid units ready to sell</div></div><div class="card"><div class="muted">Today's sales</div><div class="metric">₹{{'%.2f'|format(m.sales)}}</div><div class="muted">Revenue recorded today</div></div></div>
    <div class="section-head"><h2 style="margin:8px 0">Quick actions</h2><span class="muted">Common tasks</span></div><div class="actions"><a class="btn" href="/medicines">Manage medicines</a><a class="btn" href="/receive">＋ Receive stock</a><a class="btn" href="/sale">＋ Create bill</a><a class="btn" href="/reports">View reports</a></div>
    <div class="section-head"><h2>Available stock by medicine</h2><span class="muted">{{inventory|length}} products listed</span></div><div class="tablewrap"><table><tr><th>Medicine</th><th>Category</th><th>Available units</th><th>Stock level</th><th>Reorder level</th><th>Next expiry</th></tr>
    {% for r in inventory %}<tr><td><strong>{{r.medicine_name}}</strong></td><td>{{r.category or 'General'}}</td><td><strong>{{r.available_stock}}</strong></td><td><div class="stockbar"><span style="width:{{[100,((r.available_stock|int / (r.reorder_level|int if r.reorder_level|int > 0 else 1))*25)]|min}}%"></span></div></td><td>{{r.reorder_level}}</td><td>{{r.next_batch_expiry or '—'}}</td></tr>{% else %}<tr><td colspan="6" class="empty-note">No medicines in the catalogue yet. Add a medicine and receive stock to see inventory here.</td></tr>{% endfor %}</table></div>
    <div class="grid"><section><h2>Low stock alerts</h2><div class="tablewrap"><table><tr><th>Medicine</th><th>Available</th><th>Reorder level</th></tr>{% for r in low %}<tr><td>{{r.medicine_name}}</td><td>{{r.available_stock}}</td><td>{{r.reorder_level}}</td></tr>{% else %}<tr><td colspan="3" class="empty-note">All listed medicines are above their reorder levels.</td></tr>{% endfor %}</table></div></section>
    <section><h2>Expiring in 90 days</h2><div class="tablewrap"><table><tr><th>Medicine</th><th>Batch</th><th>Expiry</th><th>Qty</th></tr>{% for r in exp %}<tr><td>{{r.medicine_name}}</td><td>{{r.batch_number}}</td><td>{{r.expiry_date}}</td><td>{{r.quantity}}</td></tr>{% else %}<tr><td colspan="4" class="empty-note">No near-expiry batches.</td></tr>{% endfor %}</table></div></section></div>""",m=metrics,inventory=inventory,low=low,exp=exp)

@app.route("/medicines",methods=["GET","POST"])
def medicines():
    c=db()
    if request.method=="POST":
        try:
            name=request.form.get("name","").strip(); reorder=int(request.form.get("reorder_level","10"))
            if not name or reorder<0: raise ValueError
            c.execute("INSERT INTO medicines(name,category,manufacturer,unit,reorder_level) VALUES(?,?,?,?,?)",
              (name,request.form.get("category","General").strip() or "General",request.form.get("manufacturer","").strip(),request.form.get("unit","strip").strip() or "strip",reorder))
            c.commit(); flash("Medicine added."); return redirect(url_for("medicines"))
        except (ValueError,sqlite3.IntegrityError):
            c.rollback(); flash("Enter a name and a non-negative reorder level.","error")
    q=request.args.get("q","").strip()
    rows=c.execute("SELECT * FROM v_inventory WHERE medicine_name LIKE ? ORDER BY medicine_name",("%"+q+"%",)).fetchall()
    return page("Medicines","""<h1>Medicine catalogue</h1><div class="panel"><h2>Add medicine</h2><form method="post"><div class="form">
    <div><label>Name *</label><input name="name" required></div><div><label>Category</label><input name="category" value="General"></div><div><label>Manufacturer</label><input name="manufacturer"></div><div><label>Unit</label><input name="unit" value="strip"></div><div><label>Reorder level</label><input type="number" name="reorder_level" min="0" value="10"></div></div><p><button>Add medicine</button></p></form></div>
    <form method="get" class="actions"><input name="q" value="{{q}}" placeholder="Search medicine"><button>Search</button></form><div class="tablewrap"><table><tr><th>Medicine</th><th>Category</th><th>Stock</th><th>Reorder</th><th>Next expiry</th><th>Starting price</th></tr>
    {% for r in rows %}<tr><td>{{r.medicine_name}}</td><td>{{r.category}}</td><td>{{r.available_stock}}</td><td>{{r.reorder_level}}</td><td>{{r.next_batch_expiry or '—'}}</td><td>₹{{'%.2f'|format(r.starting_price or 0)}}</td></tr>{% else %}<tr><td colspan="6">No matches.</td></tr>{% endfor %}</table></div>""",q=q,rows=rows)

@app.route("/suppliers",methods=["GET","POST"])
def suppliers():
    c=db()
    if request.method=="POST":
        name=request.form.get("name","").strip()
        if not name: flash("Supplier name is required.","error")
        else:
            c.execute("INSERT INTO suppliers(name,phone,email,address) VALUES(?,?,?,?)",(name,request.form.get("phone","").strip(),request.form.get("email","").strip(),request.form.get("address","").strip()))
            c.commit(); flash("Supplier added."); return redirect(url_for("suppliers"))
    rows=c.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    return page("Suppliers","""<h1>Suppliers</h1><div class="panel"><form method="post"><div class="form"><div><label>Name *</label><input name="name" required></div><div><label>Phone</label><input name="phone"></div><div><label>Email</label><input type="email" name="email"></div><div><label>Address</label><input name="address"></div></div><p><button>Add supplier</button></p></form></div>
    <div class="tablewrap"><table><tr><th>Name</th><th>Phone</th><th>Email</th><th>Address</th></tr>{% for r in rows %}<tr><td>{{r.name}}</td><td>{{r.phone or '—'}}</td><td>{{r.email or '—'}}</td><td>{{r.address or '—'}}</td></tr>{% endfor %}</table></div>""",rows=rows)

@app.route("/customers",methods=["GET","POST"])
def customers():
    c=db()
    if request.method=="POST":
        name=request.form.get("full_name","").strip()
        if not name: flash("Customer name is required.","error")
        else:
            c.execute("INSERT INTO customers(full_name,phone) VALUES(?,?)",(name,request.form.get("phone","").strip()))
            c.commit(); flash("Customer added."); return redirect(url_for("customers"))
    rows=c.execute("SELECT * FROM customers ORDER BY full_name").fetchall()
    return page("Customers","""<h1>Customers</h1><div class="panel"><form method="post"><div class="form"><div><label>Full name *</label><input name="full_name" required></div><div><label>Phone</label><input name="phone"></div></div><p><button>Add customer</button></p></form></div>
    <div class="tablewrap"><table><tr><th>Name</th><th>Phone</th><th>Added</th></tr>{% for r in rows %}<tr><td>{{r.full_name}}</td><td>{{r.phone or '—'}}</td><td>{{r.created_at}}</td></tr>{% endfor %}</table></div>""",rows=rows)

@app.route("/receive",methods=["GET","POST"])
def receive():
    c=db(); meds=c.execute("SELECT medicine_id,name FROM medicines ORDER BY name").fetchall(); sups=c.execute("SELECT supplier_id,name FROM suppliers ORDER BY name").fetchall()
    if request.method=="POST":
        try:
            mid=int(request.form["medicine_id"]); sv=request.form.get("supplier_id",""); sid=int(sv) if sv else None
            batch=request.form.get("batch_number","").strip(); expiry=date.fromisoformat(request.form["expiry_date"])
            qty=int(request.form["quantity"]); cost=float(request.form["purchase_price"]); price=float(request.form["selling_price"])
            if not batch or qty<=0 or cost<0 or price<0 or expiry<date.today(): raise ValueError
            c.execute("BEGIN")
            found=c.execute("SELECT batch_id FROM medicine_batches WHERE medicine_id=? AND batch_number=?",(mid,batch)).fetchone()
            if found:
                bid=found["batch_id"]; c.execute("UPDATE medicine_batches SET quantity=quantity+?,expiry_date=?,supplier_id=?,purchase_price=?,selling_price=? WHERE batch_id=?",(qty,expiry.isoformat(),sid,cost,price,bid))
            else:
                c.execute("INSERT INTO medicine_batches(medicine_id,supplier_id,batch_number,expiry_date,quantity,purchase_price,selling_price) VALUES(?,?,?,?,?,?,?)",(mid,sid,batch,expiry.isoformat(),qty,cost,price)); bid=c.execute("SELECT last_insert_rowid()").fetchone()[0]
            invoice="PUR-"+uuid4().hex[:10].upper(); total=qty*cost
            c.execute("INSERT INTO purchases(supplier_id,invoice_number,total_amount) VALUES(?,?,?)",(sid,invoice,total)); pid=c.execute("SELECT last_insert_rowid()").fetchone()[0]
            c.execute("INSERT INTO purchase_items(purchase_id,batch_id,quantity,unit_cost,line_total) VALUES(?,?,?,?,?)",(pid,bid,qty,cost,total))
            c.execute("INSERT INTO stock_movements(batch_id,movement_type,quantity_change,reference_text) VALUES(?,?,?,?)",(bid,"PURCHASE",qty,invoice))
            c.commit(); flash("Stock received. Purchase invoice: "+invoice); return redirect(url_for("receive"))
        except (ValueError,KeyError,sqlite3.IntegrityError):
            c.rollback(); flash("Check inputs. Quantity must be positive, prices non-negative, expiry not past, and batch unique per medicine.","error")
    recent=c.execute("""SELECT p.purchase_date,p.invoice_number,p.total_amount,s.name supplier_name,
        GROUP_CONCAT(m.name || ' (' || pi.quantity || ')', ', ') items
        FROM purchases p LEFT JOIN suppliers s ON s.supplier_id=p.supplier_id
        LEFT JOIN purchase_items pi ON pi.purchase_id=p.purchase_id
        LEFT JOIN medicine_batches b ON b.batch_id=pi.batch_id
        LEFT JOIN medicines m ON m.medicine_id=b.medicine_id
        GROUP BY p.purchase_id ORDER BY p.purchase_id DESC LIMIT 15""").fetchall()
    return page("Receive stock","""<h1>Receive stock</h1><p class="muted">Each batch stores its own expiry and prices.</p>{% if not meds %}<div class="flash error">Add a medicine first.</div>{% else %}
    <div class="panel"><form method="post"><div class="form"><div><label>Medicine *</label><select name="medicine_id">{% for m in meds %}<option value="{{m.medicine_id}}">{{m.name}}</option>{% endfor %}</select></div>
    <div><label>Supplier</label><select name="supplier_id"><option value="">Unspecified</option>{% for s in sups %}<option value="{{s.supplier_id}}">{{s.name}}</option>{% endfor %}</select></div>
    <div><label>Batch number *</label><input name="batch_number" required></div><div><label>Expiry *</label><input type="date" name="expiry_date" min="{{today}}" required></div>
    <div><label>Quantity *</label><input type="number" name="quantity" min="1" required></div><div><label>Purchase price ₹ *</label><input type="number" name="purchase_price" min="0" step=".01" required></div>
    <div><label>Selling price ₹ *</label><input type="number" name="selling_price" min="0" step=".01" required></div></div><p><button>Record purchase</button></p></form></div>{% endif %}
    <h2>Recent stock receipts</h2><div class="tablewrap"><table><tr><th>Date</th><th>Invoice</th><th>Supplier</th><th>Items / quantity</th><th>Total</th></tr>{% for r in recent %}<tr><td>{{r.purchase_date}}</td><td>{{r.invoice_number}}</td><td>{{r.supplier_name or '—'}}</td><td>{{r.items or '—'}}</td><td>₹{{'%.2f'|format(r.total_amount)}}</td></tr>{% else %}<tr><td colspan="5">No receipts recorded yet. Record a purchase above.</td></tr>{% endfor %}</table></div>""",meds=meds,sups=sups,today=date.today().isoformat(),recent=recent)

@app.route("/sale",methods=["GET","POST"])
def sale():
    c=db()
    if request.method=="POST":
        try:
            cv=request.form.get("customer_id",""); cid=int(cv) if cv else None
            ids=request.form.getlist("batch_id"); qtys=request.form.getlist("quantity"); cart=[]
            for raw,qraw in zip(ids,qtys):
                if raw:
                    bid,q=int(raw),int(qraw)
                    if q<=0: raise ValueError
                    cart.append((bid,q))
            if not cart: raise ValueError
            c.execute("BEGIN"); lines=[]; total=0.0
            for bid,q in cart:
                row=c.execute("SELECT b.*,m.name medicine_name FROM medicine_batches b JOIN medicines m ON m.medicine_id=b.medicine_id WHERE b.batch_id=?",(bid,)).fetchone()
                if row is None or row["expiry_date"]<date.today().isoformat() or row["quantity"]<q: raise ValueError
                line=round(row["selling_price"]*q,2); total=round(total+line,2); lines.append((row,q,line))
            invoice="SAL-"+datetime.now().strftime("%Y%m%d")+"-"+uuid4().hex[:6].upper()
            c.execute("INSERT INTO sales(customer_id,invoice_number,total_amount) VALUES(?,?,?)",(cid,invoice,total)); sale_id=c.execute("SELECT last_insert_rowid()").fetchone()[0]
            for row,q,line in lines:
                changed=c.execute("UPDATE medicine_batches SET quantity=quantity-? WHERE batch_id=? AND quantity>=? AND expiry_date>=date('now')",(q,row["batch_id"],q)).rowcount
                if changed!=1: raise ValueError
                c.execute("INSERT INTO sale_items(sale_id,batch_id,quantity,unit_price,line_total) VALUES(?,?,?,?,?)",(sale_id,row["batch_id"],q,row["selling_price"],line))
                c.execute("INSERT INTO stock_movements(batch_id,movement_type,quantity_change,reference_text) VALUES(?,?,?,?)",(row["batch_id"],"SALE",-q,invoice))
            c.commit(); flash("Sale completed: "+invoice); return redirect(url_for("invoice",sale_id=sale_id))
        except (ValueError,TypeError,sqlite3.IntegrityError):
            c.rollback(); flash("Sale not completed. Select valid batches and quantities; expired or insufficient stock is rejected.","error")
    batches=c.execute("SELECT b.*,m.name medicine_name FROM medicine_batches b JOIN medicines m ON m.medicine_id=b.medicine_id WHERE b.quantity>0 AND b.expiry_date>=date('now') ORDER BY m.name,b.expiry_date").fetchall()
    customers=c.execute("SELECT * FROM customers ORDER BY full_name").fetchall()
    return page("New sale","""<h1>New sale / bill</h1><p class="muted">Choose up to five item lines. A sale and its stock deductions commit together.</p>{% if not batches %}<div class="flash error">No valid stock available; receive stock first.</div>{% else %}
    <div class="panel"><form method="post"><label>Customer (optional)</label><select name="customer_id"><option value="">Walk-in customer</option>{% for c in customers %}<option value="{{c.customer_id}}">{{c.full_name}}</option>{% endfor %}</select>
    {% for i in range(5) %}<div class="form"><div><label>Item {{i+1}}</label><select name="batch_id"><option value="">— none —</option>{% for b in batches %}<option value="{{b.batch_id}}">{{b.medicine_name}} · {{b.batch_number}} · stock {{b.quantity}} · exp {{b.expiry_date}} · ₹{{'%.2f'|format(b.selling_price)}}</option>{% endfor %}</select></div><div><label>Quantity</label><input type="number" name="quantity" min="1" value="1"></div></div>{% endfor %}<p><button>Complete sale</button></p></form></div>{% endif %}""",batches=batches,customers=customers)

@app.route("/invoice/<int:sale_id>")
def invoice(sale_id):
    c=db(); s=c.execute("SELECT s.*,COALESCE(c.full_name,'Walk-in customer') customer_name FROM sales s LEFT JOIN customers c ON c.customer_id=s.customer_id WHERE sale_id=?",(sale_id,)).fetchone()
    if not s: return page("Not found","<h1>Invoice not found</h1>"),404
    items=c.execute("SELECT m.name,b.batch_number,si.quantity,si.unit_price,si.line_total FROM sale_items si JOIN medicine_batches b ON b.batch_id=si.batch_id JOIN medicines m ON m.medicine_id=b.medicine_id WHERE si.sale_id=?",(sale_id,)).fetchall()
    return page("Invoice","""<h1>Sales invoice</h1><div class="panel"><p><b>Invoice:</b> {{s.invoice_number}}<br><b>Date:</b> {{s.sale_date}}<br><b>Customer:</b> {{s.customer_name}}</p>
    <div class="tablewrap"><table><tr><th>Medicine</th><th>Batch</th><th>Qty</th><th>Unit price</th><th>Total</th></tr>{% for i in items %}<tr><td>{{i.name}}</td><td>{{i.batch_number}}</td><td>{{i.quantity}}</td><td>₹{{'%.2f'|format(i.unit_price)}}</td><td>₹{{'%.2f'|format(i.line_total)}}</td></tr>{% endfor %}<tr><th colspan="4">Grand total</th><th>₹{{'%.2f'|format(s.total_amount)}}</th></tr></table></div><p class="actions"><button onclick="window.print()">Print invoice</button><a class="btn" href="/sale">New sale</a></p></div>""",s=s,items=items)

@app.route("/reports")
def reports():
    c=db(); inv=c.execute("SELECT * FROM v_inventory ORDER BY medicine_name").fetchall()
    exp=c.execute("SELECT * FROM v_expiring_batches ORDER BY expiry_date").fetchall()
    sales=c.execute("SELECT date(sale_date) day,COUNT(*) bills,SUM(total_amount) revenue FROM sales GROUP BY date(sale_date) ORDER BY day DESC LIMIT 30").fetchall()
    return page("Reports","""<h1>Reports</h1><h2>Inventory</h2><div class="tablewrap"><table><tr><th>Medicine</th><th>Category</th><th>Stock</th><th>Reorder</th></tr>{% for r in inv %}<tr><td>{{r.medicine_name}}</td><td>{{r.category}}</td><td>{{r.available_stock}}</td><td>{{r.reorder_level}}</td></tr>{% endfor %}</table></div>
    <h2>Expiry (next 90 days)</h2><div class="tablewrap"><table><tr><th>Medicine</th><th>Batch</th><th>Expiry</th><th>Qty</th><th>Supplier</th></tr>{% for r in exp %}<tr><td>{{r.medicine_name}}</td><td>{{r.batch_number}}</td><td>{{r.expiry_date}}</td><td>{{r.quantity}}</td><td>{{r.supplier_name or '—'}}</td></tr>{% else %}<tr><td colspan="5">No near-expiry batches.</td></tr>{% endfor %}</table></div>
    <h2>Daily sales</h2><div class="tablewrap"><table><tr><th>Date</th><th>Bills</th><th>Revenue</th></tr>{% for r in sales %}<tr><td>{{r.day}}</td><td>{{r.bills}}</td><td>₹{{'%.2f'|format(r.revenue)}}</td></tr>{% else %}<tr><td colspan="3">No sales recorded.</td></tr>{% endfor %}</table></div>""",inv=inv,exp=exp,sales=sales)

@app.route("/health")
def health():
    """Lightweight Render health check; does not mutate application data."""
    try:
        db().execute("SELECT 1").fetchone()
        return jsonify(status="ok", database="ok"), 200
    except sqlite3.Error:
        app.logger.exception("Database health check failed")
        return jsonify(status="error", database="unavailable"), 503

@app.errorhandler(404)
def not_found(_err):
    return page("Not found","<h1>Page not found</h1><a class='btn' href='/'>Dashboard</a>"),404

@app.route("/sql-lab")
def sql_lab():
    return page("DBMS SQL Lab", """
    <h1>DBMS SQL Lab</h1>
    <p class="muted">MedCare Pharmacy · DBMS Laboratory Project 13</p>
    <div class="panel"><h2>SELECT, WHERE and ORDER BY</h2><pre><code>SELECT name, category FROM medicines WHERE category = 'Pain Relief' ORDER BY name;</code></pre></div>
    <div class="panel"><h2>LIKE search</h2><pre><code>SELECT name FROM medicines WHERE name LIKE '%Syrup%';</code></pre></div>
    <div class="panel"><h2>Aggregate functions</h2><pre><code>SELECT COUNT(*) AS medicine_count, MIN(reorder_level), MAX(reorder_level), AVG(reorder_level) FROM medicines;</code></pre></div>
    <div class="panel"><h2>GROUP BY and HAVING</h2><pre><code>SELECT category, COUNT(*) AS medicine_count FROM medicines GROUP BY category HAVING COUNT(*) >= 1;</code></pre></div>
    <div class="panel"><h2>JOIN</h2><pre><code>SELECT m.name, b.batch_number, s.name AS supplier, b.quantity FROM medicine_batches b JOIN medicines m ON m.medicine_id=b.medicine_id LEFT JOIN suppliers s ON s.supplier_id=b.supplier_id;</code></pre></div>
    <div class="panel"><h2>Subquery</h2><pre><code>SELECT m.name, b.selling_price FROM medicines m JOIN medicine_batches b ON b.medicine_id=m.medicine_id WHERE b.selling_price > (SELECT AVG(selling_price) FROM medicine_batches);</code></pre></div>
    <div class="panel"><h2>Run the MySQL lab script</h2><p>The standalone MySQL script is for your local MySQL Command Line. This live website continues to use its existing SQLite database.</p><p><a href="https://github.com/marthanithinkumar-web/pharmacy-management-system/blob/main/database/medcare_mysql.sql">Open MySQL lab script</a></p></div>
    """)
    
if __name__=="__main__":
    init_db()
    app.run(host="127.0.0.1",port=int(os.environ.get("PORT","5000")),debug=os.environ.get("FLASK_DEBUG")=="1")
