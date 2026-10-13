# API de Impresión de Etiquetas ETQ/LPN

Backend FastAPI de la prueba técnica de impresión de etiquetas. Valida LPN contra una orden e
inventario mock, devuelve el contrato ETQ definido por `responseEtq.json` y registra cada
solicitud aprobada o rechazada en SQLite. La impresión se simula: no se conecta a una impresora
física ni necesita Oracle para este flujo.

## Arquitectura

- `api/`: endpoints HTTP, esquemas Pydantic y configuración de FastAPI.
- `application/services/printing.py`: reglas de validación del caso de uso.
- `domain/models/printing.py`: modelos del dominio para solicitudes, orden, inventario y auditoría.
- `infrastructure/repositories/printing_repository.py`: lectura de orden e inventario mock.
- `infrastructure/repositories/print_audit_repository.py`: persistencia SQLite e historial.
- `data/inventory.json`: disponibilidad mock por producto y zona.
- `../tableOrders.json`: orden y etiqueta mock del LPN `olpn12345`.

## Ejecutar localmente en Windows

Desde esta carpeta:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8080
```

La documentación interactiva estará disponible en:

- Swagger UI: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- ReDoc: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)

## Ejecutar con Docker Compose

Desde la raíz del repositorio, con Docker Desktop iniciado:

```powershell
docker compose up --build
```

La interfaz Angular estará en [http://localhost:4200](http://localhost:4200) y Swagger en
[http://localhost:8080/docs](http://localhost:8080/docs). Nginx también reenvía las peticiones
`/printing/` de la interfaz al backend.

Para detener los servicios sin borrar el historial:

```powershell
docker compose down
```

## Endpoints

### `POST /printing/validate`

Valida e intenta imprimir una etiqueta. El LPN es obligatorio; `zone` y `requestedBy` son
opcionales y se completan con los valores de la orden mock cuando se omiten.

Request:

```json
{
  "request": {
    "lpn": "olpn12345"
  },
  "zone": "ZONA-PICKING-A",
  "requestedBy": "usuario.operacion"
}
```

Una aprobación devuelve el contrato de `responseEtq.json`:

```json
{
  "response": {
    "idEtiqueta": "12345",
    "purchaseOrder": "PO123456",
    "tcOrderId": "TC78910",
    "sku": "SKU001",
    "unidades": 25,
    "zpl": "..."
  }
}
```

Un rechazo de negocio responde HTTP `422` con los motivos en `detail`. Todos los intentos quedan
auditados antes de responder.

### `GET /printing/history`

Lista los intentos más recientes. Acepta `lpn` opcional y `limit` entre 1 y 500 (predeterminado
100):

```text
GET /printing/history?lpn=olpn12345&limit=50
```

Los eventos son `PRINT` para la primera aprobación, `REPRINT` para aprobaciones posteriores del
mismo LPN y `REJECTED` para solicitudes que no pasan las reglas. Solo una aprobación previa
cuenta al clasificar una reimpresión.

## Reglas de negocio

- El LPN debe corresponder a exactamente una etiqueta.
- El documento no puede tener estado `ANULADA` ni `DEVUELTA`.
- La etiqueta debe estar pre-generada.
- La cantidad solicitada debe ser positiva.
- Para cada producto debe existir inventario en la zona; debe estar abastecido y cubrir la cantidad
  solicitada.

## Auditoría SQLite

En una ejecución local, SQLite crea `data/printing_audit.sqlite3` al primer intento o consulta del
historial. La tabla `print_audit` se crea automáticamente si no existe; no requiere un servidor
SQLite aparte ni un script de inicialización.

Se puede cambiar la ruta local mediante `PRINT_AUDIT_DB_PATH`. Docker Compose establece esa
variable a `/var/lib/etq/printing_audit.sqlite3` y monta un volumen nombrado `print-audit` para
conservar los registros al reiniciar o recrear los contenedores. `docker compose down -v` elimina
ese volumen y, por tanto, el historial.

## Pruebas

Desde esta carpeta, con las dependencias de desarrollo instaladas:

```powershell
python -m pytest -q
```

Las pruebas cubren aprobaciones, rechazos, validación de inventario, documentos anulados/devueltos,
pre-generación de etiquetas, reimpresiones, contrato API e historial.
