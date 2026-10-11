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

    def test_core_pages_load(self):
        for path in ("/", "/medicines", "/suppliers", "/customers",
                     "/receive", "/sale", "/reports", "/sql-lab", "/health"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, response.get_data(as_text=True)[:300])

    def test_dashboard_shows_inventory(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard", response.data)
        self.assertIn(b"Available stock by medicine", response.data)

    def test_add_medicine(self):
        response = self.client.post(
            "/medicines",
            data={"name": "Test Tablet", "category": "Test",
                  "manufacturer": "Lab", "unit": "strip", "reorder_level": "5"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Tablet", response.data)

    def test_sale_decrements_stock(self):
        with pharmacy.app.app_context():
            c = pharmacy.db()
            row = c.execute(
                """SELECT batch_id, quantity FROM medicine_batches
                   WHERE quantity >= 2 AND expiry_date >= date('now')
                   ORDER BY expiry_date LIMIT 1"""
            ).fetchone()
            self.assertIsNotNone(row, "Seed data should include a valid batch")
            bid, before = row["batch_id"], row["quantity"]

        response = self.client.post(
            "/sale",
            data={"customer_id": "", "batch_id": [str(bid), "", "", "", ""],
                  "quantity": ["2", "1", "1", "1", "1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sales invoice", response.data)
        with pharmacy.app.app_context():
            after = pharmacy.db().execute(
                "SELECT quantity FROM medicine_batches WHERE batch_id=?", (bid,)
            ).fetchone()["quantity"]
        self.assertEqual(after, before - 2)

    def test_failed_sale_rolls_back(self):
        with pharmacy.app.app_context():
            c = pharmacy.db()
            row = c.execute(
                """SELECT batch_id, quantity FROM medicine_batches
                   WHERE quantity > 0 AND expiry_date >= date('now')
                   ORDER BY batch_id LIMIT 1"""
            ).fetchone()
            self.assertIsNotNone(row, "Seed data should include a valid batch")
            bid, before = row["batch_id"], row["quantity"]
            sales_before = c.execute("SELECT COUNT(*) FROM sales").fetchone()[0]

        response = self.client.post(
            "/sale",
            data={"customer_id": "", "batch_id": [str(bid), "", "", "", ""],
                  "quantity": [str(before + 50), "1", "1", "1", "1"]},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sale not completed", response.data)
        with pharmacy.app.app_context():
            c = pharmacy.db()
            after = c.execute(
                "SELECT quantity FROM medicine_batches WHERE batch_id=?", (bid,)
            ).fetchone()["quantity"]
            sales_after = c.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        self.assertEqual(after, before)
        self.assertEqual(sales_after, sales_before)

    def test_health_endpoint_reports_database(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        self.assertEqual(response.get_json()["database"], "ok")


if __name__ == "__main__":
    unittest.main()
