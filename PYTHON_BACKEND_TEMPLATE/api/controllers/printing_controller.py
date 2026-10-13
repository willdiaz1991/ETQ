from fastapi import APIRouter, HTTPException, Query

from api.response.api_response import ApiResponse
from api.schemas.printing_schema import (
    PrintAuditRecord,
    PrintEtqResponse,
    PrintEtqResponseData,
    PrintValidationRequest,
)
from application.services.printing import evaluate_print_request
from domain.models.printing import PrintRequest
from infrastructure.repositories.print_audit_repository import PrintAuditRepository
from infrastructure.repositories.printing_repository import load_inventory, load_order

printing_router = APIRouter(prefix="/printing", tags=["Printing"])
audit_repository = PrintAuditRepository()


@printing_router.post(
    "/validate",
    summary="Validate a pre-generated label print request",
    response_model=PrintEtqResponse,
)
def validate_print(payload: PrintValidationRequest) -> PrintEtqResponse:
    order = load_order()
    inventory = load_inventory()
    decision = evaluate_print_request(
        PrintRequest(
            lpn=payload.request.lpn,
            zone=payload.zone,
            requested_by=payload.requested_by,
        ),
        orders=[order],
        inventory=inventory,
    )
    audit_entry = audit_repository.record_attempt(decision)
    if not decision.approved:
        raise HTTPException(status_code=422, detail=list(audit_entry.reasons))
    if decision.etq_id is None:
        raise RuntimeError("La validación aprobada no contiene un identificador de etiqueta.")

    product = order.products[0]
    return PrintEtqResponse(
        response=PrintEtqResponseData(
            id_etiqueta=decision.etq_id,
            purchase_order=order.purchase_order,
            tc_order_id=order.tc_order_id,
            sku=product.product_code,
            unidades=product.requested_qty,
            zpl=decision.zpl,
        )
    )


@printing_router.get(
    "/history",
    summary="List print and reprint audit history",
    response_model=ApiResponse[list[PrintAuditRecord]],
)
def list_print_history(
    lpn: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> ApiResponse[list[PrintAuditRecord]]:
    entries = audit_repository.list_history(lpn=lpn, limit=limit)
    result = [
        PrintAuditRecord(
            request_id=entry.request_id,
            requested_at=entry.requested_at,
            lpn=entry.lpn,
            etq_id=entry.etq_id,
            zone=entry.zone,
            requested_by=entry.requested_by,
            approved=entry.approved,
            event_type=entry.event_type,
            is_reprint=entry.is_reprint,
            reasons=list(entry.reasons),
        )
        for entry in entries
    ]
    return ApiResponse.create_successful(result=result)
