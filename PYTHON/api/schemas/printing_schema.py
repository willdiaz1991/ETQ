from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PrintRequestIdentifier(BaseModel):
    lpn: str = Field(min_length=1)


class PrintValidationRequest(BaseModel):
    request: PrintRequestIdentifier
    zone: Optional[str] = None
    requested_by: Optional[str] = Field(default=None, alias="requestedBy")

    model_config = ConfigDict(populate_by_name=True)


class PrintEtqResponseData(BaseModel):
    id_etiqueta: str = Field(alias="idEtiqueta")
    purchase_order: str = Field(alias="purchaseOrder")
    tc_order_id: str = Field(alias="tcOrderId")
    sku: str
    unidades: int
    zpl: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class PrintEtqResponse(BaseModel):
    response: PrintEtqResponseData


class PrintAuditRecord(BaseModel):
    request_id: str = Field(alias="requestId")
    requested_at: str = Field(alias="requestedAt")
    lpn: str
    etq_id: Optional[str] = Field(alias="etqId")
    zone: Optional[str]
    requested_by: Optional[str] = Field(alias="requestedBy")
    approved: bool
    event_type: str = Field(alias="eventType")
    is_reprint: bool = Field(alias="isReprint")
    reasons: list[str]

    model_config = ConfigDict(populate_by_name=True)
