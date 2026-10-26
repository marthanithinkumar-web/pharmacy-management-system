# MedCare Pharmacy — ER Diagram

This ER diagram is based on the current `database/medcare_mysql.sql` file in this repository. It represents the **classroom MySQL schema**; confirm separately if the deployed app uses a different schema.

```mermaid
erDiagram
    SUPPLIERS {
        int supplier_id PK
        varchar name
        varchar phone
        varchar email
        varchar address
        timestamp created_at
    }
    CUSTOMERS {
        int customer_id PK
        varchar full_name
        varchar phone
        varchar email
        varchar address
        timestamp created_at
    }
    MEDICINES {
        int medicine_id PK
        varchar name
        varchar category
        varchar manufacturer
        varchar unit
        int reorder_level
        boolean prescription_required
    }
    MEDICINE_BATCHES {
        int batch_id PK
        int medicine_id FK
        int supplier_id FK
        varchar batch_number
        decimal purchase_price
        decimal selling_price
        int quantity
        date expiry_date
    }
    PURCHASES {
        int purchase_id PK
        int supplier_id FK
        date purchase_date
        decimal total_amount
    }
    PURCHASE_ITEMS {
        int purchase_item_id PK
        int purchase_id FK
        int batch_id FK
        int quantity
        decimal unit_cost
    }
    SALES {
        int sale_id PK
        int customer_id FK
        datetime sale_date
        decimal total_amount
    }
    SALE_ITEMS {
        int sale_item_id PK
        int sale_id FK
        int batch_id FK
        int quantity
        decimal unit_price
    }
    STOCK_MOVEMENTS {
        int movement_id PK
        int batch_id FK
        enum movement_type
        int quantity_change
        timestamp movement_date
        varchar notes
    }

    SUPPLIERS o|--o{ MEDICINE_BATCHES : supplies
    SUPPLIERS o|--o{ PURCHASES : receives
    MEDICINES ||--o{ MEDICINE_BATCHES : has
    PURCHASES ||--|{ PURCHASE_ITEMS : contains
    MEDICINE_BATCHES ||--o{ PURCHASE_ITEMS : received_as
    CUSTOMERS o|--o{ SALES : makes
    SALES ||--|{ SALE_ITEMS : contains
    MEDICINE_BATCHES ||--o{ SALE_ITEMS : sold_from
    MEDICINE_BATCHES ||--o{ STOCK_MOVEMENTS : tracks
```

## Relationship notes
- One medicine can have multiple batches; every batch references one medicine.
- A batch may reference a supplier; supplier is nullable in the SQL schema.
- A purchase may reference a supplier; the supplier reference is nullable.
- A purchase has one or more purchase-item rows; each purchase item references a purchase and a batch.
- A customer may have multiple sales; the customer reference on a sale is nullable.
- A sale has one or more sale-item rows; each sale item references a sale and a batch.
- Each stock movement references a batch.
- `v_inventory` and `v_low_stock` are **views**, not base tables, so they are not shown as entities here.

## Source
`database/medcare_mysql.sql` — repository schema file.