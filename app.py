import os
import sqlite3
from pathlib import Path
from datetime import date, datetime
from uuid import uuid4
from flask import Flask, g, request, redirect, url_for, flash, render_template_string

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
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    if seed and conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0] == 0:
        conn.execute("INSERT INTO suppliers(name,phone,email) VALUES(?,?,?)",
                     ("Demo Medical Distributors","9000000001","supplier@example.test"))
        sid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        demo = [
            ("Paracetamol 500 mg","Analgesic","Demo Pharma","strip",20,100,10,15),
            ("Cetirizine 10 mg","Antihistamine","Demo Pharma","strip",10,100,8,12),
            ("ORS Sachet","Rehydration","Demo Labs","piece",15,100,4,7),
        ]
        for name,cat,maker,unit,reorder,qty,cost,price in demo:
            conn.execute("INSERT INTO medicines(name,category,manufacturer,unit,reorder_level) VALUES(?,?,?,?,?)",
                         (name,cat,maker,unit,reorder))
            mid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.execute("""INSERT INTO medicine_batches(medicine_id,supplier_id,batch_number,expiry_date,quantity,purchase_price,selling_price)
                            VALUES(?,?,?,?,?,?,?)""",
                         (mid,sid,"DEMO-%03d" % mid,"2028-12-31",qty,cost,price))
    conn.commit()
    conn.close()

STYLE = """
body{margin:0;background:#f5f7f8;color:#172b2a;font:15px/1.5 system-ui,Segoe UI,sans-serif}
header{background:white;border-bottom:1px solid #dce5e3;padding:16px max(16px,calc((100% - 1100px)/2));display:flex;gap:18px;flex-wrap:wrap;align-items:center}
.brand{font-size:20px;font-weight:800;color:#08715d;text-decoration:none;margin-right:auto}
nav{display:flex;gap:12px;flex-wrap:wrap}nav a{color:#344e49;text-decoration:none;font-weight:650}
main{max-width:1100px;margin:24px auto;padding:0 16px}h1{font-size:28px;margin:0 0 8px}h2{font-size:19px}
.muted{color:#667772}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:18px 0}
.card,.panel{background:white;border:1px solid #dce5e3;border-radius:12px;padding:16px;margin:12px 0}
.metric{font-size:28px;font-weight:800}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}
button,.btn{background:#08715d;color:white;border:0;border-radius:8px;padding:10px 14px;font:inherit;font-weight:700;text-decoration:none;cursor:pointer}
input,select{width:100%;padding:10px;border:1px solid #c7d4d1;border-radius:8px;background:white;font:inherit;box-sizing:border-box}
label{display:block;font-weight:650;margin:10px 0 5px}.form{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.tablewrap{overflow:auto;border:1px solid #dce5e3;border-radius:10px;background:white}table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:10px;border-bottom:1px solid #e6ecea}th{background:#f2f6f5;font-size:13px}
.flash{padding:12px;background:#e5f5ee;color:#075b49;border-radius:8px;margin:12px 0}.error{background:#fff0ed;color:#9b2116}
footer{max-width:1100px;margin:30px auto;padding:12px 16px;color:#667772;font-size:13px}
@media(max-width:600px){header{padding:14px}h1{font-size:24px}}
"""
SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{title}} · MedCare Pharmacy</title><style>{{style}}</style></head><body>
<header><a class="brand" href="/">✚ MedCare Pharmacy</a><nav>
<a href="/">Dashboard</a><a href="/medicines">Medicines</a><a href="/suppliers">Suppliers</a><a href="/customers">Customers</a><a href="/receive">Receive stock</a><a href="/sale">New sale</a><a href="/reports">Reports</a></nav></header>
<main>{% with msgs=get_flashed_messages(with_categories=true) %}{% for cat,msg in msgs %}<div class="flash {{'error' if cat=='error' else ''}}">{{msg}}</div>{% endfor %}{% endwith %}{{body|safe}}</main>
<footer>Pharmacy management demo · For learning and demonstration only; not for clinical or production use.</footer></body></html>"""

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
    low=c.execute("SELECT * FROM v_low_stock ORDER BY available_stock,medicine_name").fetchall()
    exp=c.execute("SELECT * FROM v_expiring_batches ORDER BY expiry_date").fetchall()
    return page("Dashboard","""<h1>MedCare Pharmacy dashboard</h1><p class="muted">Inventory, sales and expiry overview.</p>
    <div class="grid"><div class="card">Medicine types<div class="metric">{{m.medicines}}</div></div><div class="card">Tracked batches<div class="metric">{{m.batches}}</div></div>
    <div class="card">Valid units in stock<div class="metric">{{m.stock}}</div></div><div class="card">Today's sales<div class="metric">₹{{'%.2f'|format(m.sales)}}</div></div></div>
    <div class="actions"><a class="btn" href="/medicines">Manage medicines</a><a class="btn" href="/receive">Receive stock</a><a class="btn" href="/sale">Create bill</a></div>
    <h2>Low stock</h2><div class="tablewrap"><table><tr><th>Medicine</th><th>Available</th><th>Reorder level</th></tr>{% for r in low %}<tr><td>{{r.medicine_name}}</td><td>{{r.available_stock}}</td><td>{{r.reorder_level}}</td></tr>{% else %}<tr><td colspan="3">No low-stock medicines.</td></tr>{% endfor %}</table></div>
    <h2>Expiring in 90 days</h2><div class="tablewrap"><table><tr><th>Medicine</th><th>Batch</th><th>Expiry</th><th>Qty</th></tr>{% for r in exp %}<tr><td>{{r.medicine_name}}</td><td>{{r.batch_number}}</td><td>{{r.expiry_date}}</td><td>{{r.quantity}}</td></tr>{% else %}<tr><td colspan="4">No near-expiry batches.</td></tr>{% endfor %}</table></div>""",m=metrics,low=low,exp=exp)

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
    return page("Receive stock","""<h1>Receive stock</h1><p class="muted">Each batch stores its own expiry and prices.</p>{% if not meds %}<div class="flash error">Add a medicine first.</div>{% else %}
    <div class="panel"><form method="post"><div class="form"><div><label>Medicine *</label><select name="medicine_id">{% for m in meds %}<option value="{{m.medicine_id}}">{{m.name}}</option>{% endfor %}</select></div>
    <div><label>Supplier</label><select name="supplier_id"><option value="">Unspecified</option>{% for s in sups %}<option value="{{s.supplier_id}}">{{s.name}}</option>{% endfor %}</select></div>
    <div><label>Batch number *</label><input name="batch_number" required></div><div><label>Expiry *</label><input type="date" name="expiry_date" min="{{today}}" required></div>
    <div><label>Quantity *</label><input type="number" name="quantity" min="1" required></div><div><label>Purchase price ₹ *</label><input type="number" name="purchase_price" min="0" step=".01" required></div>
    <div><label>Selling price ₹ *</label><input type="number" name="selling_price" min="0" step=".01" required></div></div><p><button>Record purchase</button></p></form></div>{% endif %}""",meds=meds,sups=sups,today=date.today().isoformat())

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

@app.errorhandler(404)
def not_found(_err):
    return page("Not found","<h1>Page not found</h1><a class='btn' href='/'>Dashboard</a>"),404

if __name__=="__main__":
    init_db()
    app.run(host="127.0.0.1",port=int(os.environ.get("PORT","5000")),debug=os.environ.get("FLASK_DEBUG")=="1")
