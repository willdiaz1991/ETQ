from typing import Optional, Sequence

from domain.models.printing import (
    InventoryAvailability,
    PrintDecision,
    PrintLabel,
    PrintOrder,
    PrintRequest,
)


def evaluate_print_request(
    request: PrintRequest,
    orders: Sequence[PrintOrder],
    inventory: Sequence[InventoryAvailability],
    previously_printed: bool = False,
) -> PrintDecision:
    lpn = request.lpn.strip()
    if not lpn:
        return _reject(request, "El LPN es obligatorio.", previously_printed)

    matches = [
        (order, label)
        for order in orders
        for label in order.labels
        if label.lpn_id.strip().casefold() == lpn.casefold()
    ]
    if not matches:
        return _reject(request, "No existe una etiqueta para el LPN indicado.", previously_printed)
    if len(matches) > 1:
        return _reject(request, "El LPN está asociado a más de una etiqueta.", previously_printed)

    order, label = matches[0]
    zone = _value_or_default(request.zone, order.zone)
    requested_by = _value_or_default(request.requested_by, order.requested_by)
    reasons = []

    if not zone:
        reasons.append("No se pudo determinar la zona solicitada.")
    if not requested_by:
        reasons.append("No se pudo determinar el usuario solicitante.")
    if order.document_status.strip().upper() in {"ANULADA", "DEVUELTA"}:
        reasons.append("El documento origen está anulado o devuelto.")
    if not label.is_pre_generated:
        reasons.append("La etiqueta no está pre-generada.")

    for product in order.products:
        if product.requested_qty <= 0:
            reasons.append(f"La cantidad solicitada para {product.product_code} no es válida.")
            continue

        stock = next(
            (
                item
                for item in inventory
                if item.product_code == product.product_code and item.zone.casefold() == (zone or "").casefold()
            ),
            None,
        )
        if stock is None:
            reasons.append(f"No hay disponibilidad registrada para {product.product_code} en la zona {zone or 'sin definir'}.")
        elif not stock.stocked:
            reasons.append(f"El producto {product.product_code} no está abastecido en la zona {zone}.")
        elif stock.available_qty < product.requested_qty:
            reasons.append(
                f"Disponibilidad insuficiente para {product.product_code} en la zona {zone}: "
                f"solicitado {product.requested_qty}, disponible {stock.available_qty}."
            )

    if reasons:
        return PrintDecision(
            approved=False,
            lpn=lpn,
            etq_id=label.etq_id,
            zone=zone,
            requested_by=requested_by,
            is_reprint=previously_printed,
            reasons=tuple(reasons),
        )

    return PrintDecision(
        approved=True,
        lpn=lpn,
        etq_id=label.etq_id,
        zone=zone,
        requested_by=requested_by,
        is_reprint=previously_printed,
        reasons=(),
        zpl=label.zpl,
    )


def _reject(request: PrintRequest, reason: str, previously_printed: bool) -> PrintDecision:
    return PrintDecision(
        approved=False,
        lpn=request.lpn.strip(),
        etq_id=None,
        zone=request.zone,
        requested_by=request.requested_by,
        is_reprint=previously_printed,
        reasons=(reason,),
    )


def _value_or_default(value: Optional[str], default: Optional[str]) -> str:
    if value and value.strip():
        return value.strip()
    return default.strip() if default else ""
