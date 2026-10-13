export interface PrintRequest {
  request: {
    lpn: string;
  };
  zone: string;
  requestedBy: string;
}

export interface PrintEtqResponseData {
  idEtiqueta: string;
  purchaseOrder: string;
  tcOrderId: string;
  sku: string;
  unidades: number;
  zpl: string | null;
}

export interface PrintEtqResponse {
  response: PrintEtqResponseData;
}

export interface PrintAuditRecord {
  requestId: string;
  requestedAt: string;
  approved: boolean;
  lpn: string;
  etqId: string | null;
  zone: string | null;
  requestedBy: string | null;
  eventType: 'PRINT' | 'REPRINT' | 'REJECTED';
  isReprint: boolean;
  reasons: string[];
}

export interface ApiResponse<T> {
  errorMessage: string | null;
  isError: boolean;
  isSuccessful: boolean;
  messages: string[] | null;
  result: T | null;
}
