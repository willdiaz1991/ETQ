import unittest

from application.services.printing import evaluate_print_request
from domain.models.printing import (
    InventoryAvailability,
    PrintLabel,
    PrintOrder,
    PrintProduct,
    PrintRequest,
)


class PrintingValidationTests(unittest.TestCase):
    def setUp(self):
        self.order = PrintOrder(
            requested_by="usuario.operacion",
            zone="ZONA-PICKING-A",
            document_status="LIBERADA",
            labels=(PrintLabel("ETQ-10001", "olpn12345", True, "^XA^XZ"),),
            products=(PrintProduct("SKU001", 25),),
        )
        self.inventory = (
            InventoryAvailability("SKU001", "ZONA-PICKING-A", 25, True),
        )

    def test_approves_when_all_rules_are_satisfied(self):
        result = evaluate_print_request(PrintRequest("olpn12345"), [self.order], self.inventory)

        self.assertTrue(result.approved)
        self.assertEqual(result.etq_id, "ETQ-10001")
        self.assertEqual(result.zone, "ZONA-PICKING-A")
        self.assertEqual(result.requested_by, "usuario.operacion")
        self.assertEqual(result.zpl, "^XA^XZ")

    def test_rejects_unknown_lpn(self):
        result = evaluate_print_request(PrintRequest("unknown"), [self.order], self.inventory)

        self.assertFalse(result.approved)
        self.assertIn("No existe una etiqueta", result.reasons[0])

    def test_rejects_cancelled_and_returned_documents(self):
        for state in ("ANULADA", "DEVUELTA"):
            with self.subTest(state=state):
                order = PrintOrder(
                    self.order.requested_by,
                    self.order.zone,
                    state,
                    self.order.labels,
                    self.order.products,
                )
                result = evaluate_print_request(PrintRequest("olpn12345"), [order], self.inventory)

                self.assertFalse(result.approved)
                self.assertIn("anulado o devuelto", result.reasons[0])

    def test_rejects_label_that_is_not_pre_generated(self):
        order = PrintOrder(
            self.order.requested_by,
            self.order.zone,
            self.order.document_status,
            (PrintLabel("ETQ-10001", "olpn12345", False, "^XA^XZ"),),
            self.order.products,
        )
        result = evaluate_print_request(PrintRequest("olpn12345"), [order], self.inventory)

        self.assertFalse(result.approved)
        self.assertIn("La etiqueta no está pre-generada.", result.reasons)

    def test_rejects_unstocked_product(self):
        inventory = (
            InventoryAvailability("SKU001", "ZONA-PICKING-A", 25, False),
        )
        result = evaluate_print_request(PrintRequest("olpn12345"), [self.order], inventory)

        self.assertFalse(result.approved)
        self.assertIn("no está abastecido", result.reasons[0])

    def test_rejects_insufficient_inventory(self):
        inventory = (
            InventoryAvailability("SKU001", "ZONA-PICKING-A", 1, True),
        )
        result = evaluate_print_request(PrintRequest("olpn12345"), [self.order], inventory)

        self.assertFalse(result.approved)
        self.assertIn("Disponibilidad insuficiente", result.reasons[0])

    def test_uses_requested_zone_and_user_when_provided(self):
        inventory = (
            InventoryAvailability("SKU001", "ZONA-B", 25, True),
        )
        result = evaluate_print_request(
            PrintRequest("olpn12345", zone="ZONA-B", requested_by="operador-2"),
            [self.order],
            inventory,
        )

        self.assertTrue(result.approved)
        self.assertEqual(result.zone, "ZONA-B")
        self.assertEqual(result.requested_by, "operador-2")

    def test_marks_previously_printed_request_as_reprint(self):
        result = evaluate_print_request(
            PrintRequest("olpn12345"),
            [self.order],
            self.inventory,
            previously_printed=True,
        )

        self.assertTrue(result.approved)
        self.assertTrue(result.is_reprint)


if __name__ == "__main__":
    unittest.main()
