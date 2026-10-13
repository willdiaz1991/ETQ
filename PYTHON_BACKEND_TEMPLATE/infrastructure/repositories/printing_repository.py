import json
from pathlib import Path
from typing import Any, Dict, List

from domain.models.printing import InventoryAvailability, PrintLabel, PrintOrder, PrintProduct

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent


def load_order() -> PrintOrder:
    order_path = PROJECT_ROOT / "tableOrders.json"
    if not order_path.exists():
        order_path = BACKEND_ROOT / "tableOrders.json"
    data = _read_json(order_path)
    labels = tuple(
        PrintLabel(
            etq_id=label["etqId"],
            lpn_id=label["lpnId"],
            is_pre_generated=label["isPreGenerated"],
            zpl=label.get("zpl"),
        )
        for label in data["labels"]
    )
    products = tuple(
        PrintProduct(
            product_code=product["productCode"],
            requested_qty=product["requestedQty"],
        )
        for product in data["products"]
    )
    return PrintOrder(
        requested_by=data["requestedBy"],
        zone=data["zone"],
        document_status=data["document"]["status"],
        labels=labels,
        products=products,
        purchase_order=data["purchaseOrder"],
        tc_order_id=data["tcOrderId"],
    )


def load_inventory() -> List[InventoryAvailability]:
    inventory_path = BACKEND_ROOT / "data" / "inventory.json"
    data = _read_json(inventory_path)
    return [
        InventoryAvailability(
            product_code=item["productCode"],
            zone=item["zone"],
            available_qty=item["availableQty"],
            stocked=item["stocked"],
        )
        for item in data["inventory"]
    ]


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)
