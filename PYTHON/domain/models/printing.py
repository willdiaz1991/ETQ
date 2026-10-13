from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class PrintRequest:
    lpn: str
    zone: Optional[str] = None
    requested_by: Optional[str] = None


@dataclass(frozen=True)
class PrintLabel:
    etq_id: str
    lpn_id: str
    is_pre_generated: bool
    zpl: Optional[str] = None


@dataclass(frozen=True)
class PrintProduct:
    product_code: str
    requested_qty: int


@dataclass(frozen=True)
class PrintOrder:
    requested_by: str
    zone: str
    document_status: str
    labels: Tuple[PrintLabel, ...]
    products: Tuple[PrintProduct, ...]
    purchase_order: str = ""
    tc_order_id: str = ""


@dataclass(frozen=True)
class InventoryAvailability:
    product_code: str
    zone: str
    available_qty: int
    stocked: bool


@dataclass(frozen=True)
class PrintDecision:
    approved: bool
    lpn: str
    etq_id: Optional[str]
    zone: Optional[str]
    requested_by: Optional[str]
    is_reprint: bool
    reasons: Tuple[str, ...]
    zpl: Optional[str] = None


@dataclass(frozen=True)
class PrintAuditEntry:
    request_id: str
    requested_at: str
    lpn: str
    etq_id: Optional[str]
    zone: Optional[str]
    requested_by: Optional[str]
    approved: bool
    event_type: str
    is_reprint: bool
    reasons: Tuple[str, ...]
