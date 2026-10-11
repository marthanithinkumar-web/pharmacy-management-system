PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
    phone TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(trim(name)) > 0),
    category TEXT NOT NULL DEFAULT 'General',
    manufacturer TEXT,
    unit TEXT NOT NULL DEFAULT 'strip',
    reorder_level INTEGER NOT NULL DEFAULT 10 CHECK(reorder_level >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicine_batches (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id INTEGER NOT NULL REFERENCES medicines(medicine_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    supplier_id INTEGER REFERENCES suppliers(supplier_id) ON UPDATE CASCADE ON DELETE SET NULL,
    batch_number TEXT NOT NULL CHECK(length(trim(batch_number)) > 0),
    expiry_date TEXT NOT NULL, -- ISO YYYY-MM-DD
    quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
    purchase_price REAL NOT NULL CHECK(purchase_price >= 0),
    selling_price REAL NOT NULL CHECK(selling_price >= 0),
    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(medicine_id, batch_number)
);

CREATE TABLE IF NOT EXISTS purchases (
    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER REFERENCES suppliers(supplier_id) ON UPDATE CASCADE ON DELETE SET NULL,
    invoice_number TEXT NOT NULL UNIQUE,
    purchase_date TEXT NOT NULL DEFAULT (date('now')),
    total_amount REAL NOT NULL DEFAULT 0 CHECK(total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS purchase_items (
    purchase_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id INTEGER NOT NULL REFERENCES purchases(purchase_id) ON DELETE CASCADE,
    batch_id INTEGER NOT NULL REFERENCES medicine_batches(batch_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_cost REAL NOT NULL CHECK(unit_cost >= 0),
    line_total REAL NOT NULL CHECK(line_total >= 0)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(customer_id) ON UPDATE CASCADE ON DELETE SET NULL,
    invoice_number TEXT NOT NULL UNIQUE,
    sale_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL CHECK(total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS sale_items (
    sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(sale_id) ON DELETE CASCADE,
    batch_id INTEGER NOT NULL REFERENCES medicine_batches(batch_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    line_total REAL NOT NULL CHECK(line_total >= 0)
);

CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL REFERENCES medicine_batches(batch_id) ON DELETE RESTRICT,
    movement_type TEXT NOT NULL CHECK(movement_type IN ('PURCHASE', 'SALE', 'ADJUSTMENT')),
    quantity_change INTEGER NOT NULL CHECK(quantity_change <> 0),
    reference_text TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_medicine_name ON medicines(name);
CREATE INDEX IF NOT EXISTS idx_batch_expiry ON medicine_batches(expiry_date);
CREATE INDEX IF NOT EXISTS idx_batch_medicine ON medicine_batches(medicine_id);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);

CREATE VIEW IF NOT EXISTS v_inventory AS
SELECT m.medicine_id, m.name AS medicine_name, m.category, m.manufacturer, m.unit,
       m.reorder_level,
       COALESCE(SUM(CASE WHEN b.expiry_date >= date('now') THEN b.quantity ELSE 0 END), 0) AS available_stock,
       MIN(CASE WHEN b.quantity > 0 THEN b.expiry_date END) AS next_batch_expiry,
       MIN(CASE WHEN b.quantity > 0 THEN b.selling_price END) AS starting_price
FROM medicines m
LEFT JOIN medicine_batches b ON b.medicine_id = m.medicine_id
GROUP BY m.medicine_id;

CREATE VIEW IF NOT EXISTS v_low_stock AS
SELECT * FROM v_inventory WHERE available_stock <= reorder_level;

CREATE VIEW IF NOT EXISTS v_expiring_batches AS
SELECT b.batch_id, m.name AS medicine_name, b.batch_number, b.expiry_date, b.quantity,
       b.selling_price, s.name AS supplier_name
FROM medicine_batches b
JOIN medicines m ON m.medicine_id = b.medicine_id
LEFT JOIN suppliers s ON s.supplier_id = b.supplier_id
WHERE b.quantity > 0
  AND b.expiry_date BETWEEN date('now') AND date('now', '+90 days');
