-- Optional Oracle Database / SQL Developer examples for the DBMSL report.
-- The runnable Flask application uses SQLite; these examples illustrate equivalent
-- Oracle PL/SQL constructs requested in the course scope. Adapt table names/types
-- to the exact Oracle schema before executing in an Oracle environment.

-- 1) Function: calculate a line amount
CREATE OR REPLACE FUNCTION fn_line_amount(
    p_quantity IN NUMBER,
    p_unit_price IN NUMBER
) RETURN NUMBER IS
BEGIN
    IF p_quantity <= 0 OR p_unit_price < 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Invalid quantity or unit price');
    END IF;
    RETURN ROUND(p_quantity * p_unit_price, 2);
END;
/

-- 2) Procedure: record a simple stock adjustment.
-- Assumes a corresponding MEDICINE_BATCHES table with BATCH_ID and QUANTITY.
CREATE OR REPLACE PROCEDURE pr_adjust_stock(
    p_batch_id IN NUMBER,
    p_delta IN NUMBER
) IS
BEGIN
    IF p_delta = 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Stock adjustment cannot be zero');
    END IF;

    UPDATE medicine_batches
       SET quantity = quantity + p_delta
     WHERE batch_id = p_batch_id
       AND quantity + p_delta >= 0;

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'Batch not found or stock would become negative');
    END IF;
END;
/

-- 3) Explicit cursor: list batches and their remaining quantity.
DECLARE
    CURSOR c_batches IS
        SELECT batch_id, batch_number, quantity, expiry_date
          FROM medicine_batches
         ORDER BY expiry_date;
    v_batch_id medicine_batches.batch_id%TYPE;
    v_batch_no medicine_batches.batch_number%TYPE;
    v_quantity medicine_batches.quantity%TYPE;
    v_expiry medicine_batches.expiry_date%TYPE;
BEGIN
    OPEN c_batches;
    LOOP
        FETCH c_batches INTO v_batch_id, v_batch_no, v_quantity, v_expiry;
        EXIT WHEN c_batches%NOTFOUND;
        DBMS_OUTPUT.PUT_LINE('Batch ' || v_batch_no || ': quantity=' ||
                             v_quantity || ', expiry=' || TO_CHAR(v_expiry, 'YYYY-MM-DD'));
    END LOOP;
    CLOSE c_batches;
END;
/

-- 4) Trigger: reject invalid negative quantities.
-- Keep this only if the Oracle table does not already enforce the same rule.
CREATE OR REPLACE TRIGGER trg_batch_nonnegative
BEFORE INSERT OR UPDATE OF quantity ON medicine_batches
FOR EACH ROW
BEGIN
    IF :NEW.quantity < 0 THEN
        RAISE_APPLICATION_ERROR(-20004, 'Batch quantity cannot be negative');
    END IF;
END;
/

-- 5) Transaction demonstration (run with valid IDs in a test schema).
-- SAVEPOINT/ROLLBACK TO demonstrate rollback; COMMIT only after validation.
DECLARE
    v_old_qty NUMBER;
BEGIN
    SELECT quantity INTO v_old_qty
      FROM medicine_batches
     WHERE batch_id = 1
     FOR UPDATE;

    SAVEPOINT before_demo_adjustment;
    UPDATE medicine_batches SET quantity = quantity - 1 WHERE batch_id = 1;
    -- Inspect values here; if a validation fails, use:
    -- ROLLBACK TO before_demo_adjustment;
    ROLLBACK TO before_demo_adjustment;
    COMMIT;
END;
/
