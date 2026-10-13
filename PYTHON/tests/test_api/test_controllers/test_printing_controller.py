import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI
from fastapi.testclient import TestClient

import api.controllers.printing_controller as printing_controller
from api.controllers.printing_controller import printing_router
from infrastructure.repositories.print_audit_repository import PrintAuditRepository


class PrintingControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(printing_router)
        cls.client = TestClient(app)

    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "audit.sqlite3"
        printing_controller.audit_repository = PrintAuditRepository(database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validates_request_using_order_defaults(self):
        response = self.client.post("/printing/validate", json={"request": {"lpn": "olpn12345"}})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        expected_path = Path(__file__).resolve().parents[4] / "responseEtq.json"
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        self.assertEqual(body, expected)

    def test_returns_business_rejection_for_zone_without_inventory(self):
        response = self.client.post(
            "/printing/validate",
            json={"request": {"lpn": "olpn12345"}, "zone": "ZONA-NO-DISPONIBLE"},
        )

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertIn("No hay disponibilidad registrada", body["detail"][0])

        history = self.client.get("/printing/history", params={"lpn": "olpn12345"})
        self.assertEqual(history.json()["result"][0]["eventType"], "REJECTED")

    def test_returns_validation_error_when_lpn_is_missing(self):
        response = self.client.post("/printing/validate", json={"request": {}})

        self.assertEqual(response.status_code, 422)

    def test_main_app_starts_and_routes_printing_without_database_initialization(self):
        from api.main import app

        client = TestClient(app)
        response = client.post("/printing/validate", json={"request": {"lpn": "olpn12345"}})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"]["idEtiqueta"], "12345")

    def test_second_successful_print_is_a_reprint(self):
        request = {"request": {"lpn": "olpn12345"}}

        first = self.client.post("/printing/validate", json=request)
        second = self.client.post("/printing/validate", json=request)

        self.assertEqual(first.json()["response"]["idEtiqueta"], "12345")
        self.assertEqual(second.json()["response"]["idEtiqueta"], "12345")
        history = self.client.get("/printing/history", params={"lpn": "olpn12345"})
        self.assertEqual(
            [entry["eventType"] for entry in history.json()["result"]],
            ["REPRINT", "PRINT"],
        )

    def test_history_persists_attempts_and_can_filter_by_lpn(self):
        self.client.post("/printing/validate", json={"request": {"lpn": "olpn12345"}})
        self.client.post(
            "/printing/validate",
            json={"request": {"lpn": "olpn12345"}, "zone": "ZONA-NO-DISPONIBLE"},
        )

        response = self.client.get("/printing/history", params={"lpn": "OLPN12345"})

        self.assertEqual(response.status_code, 200)
        entries = response.json()["result"]
        self.assertEqual(len(entries), 2)
        self.assertEqual([entry["eventType"] for entry in entries], ["REJECTED", "PRINT"])
        self.assertTrue(all(entry["lpn"] == "olpn12345" for entry in entries))

    def test_history_remains_available_after_repository_is_recreated(self):
        self.client.post("/printing/validate", json={"request": {"lpn": "olpn12345"}})
        database_path = Path(self.temp_dir.name) / "audit.sqlite3"
        reopened_repository = PrintAuditRepository(database_path)

        entries = reopened_repository.list_history()

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].event_type, "PRINT")
        self.assertTrue(entries[0].request_id)


if __name__ == "__main__":
    unittest.main()
