import tempfile
import unittest
from pathlib import Path
import app as pharmacy

class PharmacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        pharmacy.DB_PATH = Path(self.temp.name) / "test.db"
        pharmacy.app.config.update(TESTING=True, SECRET_KEY="test")
        pharmacy.init_db()
        self.client = pharmacy.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def test_dashboard(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Pharmacy dashboard", r.data)

    def test_add_medicine(self):
        r = self.client.post("/medicines", data={"name":"Test Tablet","category":"Test","manufacturer":"Lab","unit":"strip","reorder_level":"5"}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Test Tablet", r.data)

    def test_sale_decrements_stock(self):
        with pharmacy.app.app_context():
            c = pharmacy.db()
            row = c.execute("SELECT batch_id,quantity FROM medicine_batches ORDER BY batch_id LIMIT 1").fetchone()
            bid, before = row["batch_id"], row["quantity"]
        r = self.client.post("/sale", data={"customer_id":"","batch_id":[str(bid),"","","",""],"quantity":["2","1","1","1","1"]}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Sales invoice", r.data)
        with pharmacy.app.app_context():
            after = pharmacy.db().execute("SELECT quantity FROM medicine_batches WHERE batch_id=?",(bid,)).fetchone()["quantity"]
        self.assertEqual(after, before-2)

    def test_failed_sale_rolls_back(self):
        with pharmacy.app.app_context():
            c = pharmacy.db()
            row = c.execute("SELECT batch_id,quantity FROM medicine_batches LIMIT 1").fetchone()
            bid, before = row["batch_id"], row["quantity"]
        r = self.client.post("/sale", data={"customer_id":"","batch_id":[str(bid),"","","",""],"quantity":[str(before+50),"1","1","1","1"]}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Sale not completed", r.data)
        with pharmacy.app.app_context():
            c = pharmacy.db()
            after = c.execute("SELECT quantity FROM medicine_batches WHERE batch_id=?",(bid,)).fetchone()["quantity"]
            count = c.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        self.assertEqual(after, before)
        self.assertEqual(count, 0)

if __name__ == "__main__":
    unittest.main()
