from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.controllers.health_controller import health_router
from api.controllers.printing_controller import printing_router
from api.response.api_response import ApiResponse
from api.routes.docs_routes import router as docs_router
from application.constants import constants
from application.constants.constants import APP_TITLE, APP_VERSION
from config.config import Config


def create_app() -> FastAPI:
    Config()

    app = FastAPI(
        title=APP_TITLE,
        description=(
            "API de demostración para validar solicitudes de impresión de etiquetas ETQ/LPN, "
            "consultar la orden e inventario mock y mantener la auditoría de cada intento."
        ),
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(docs_router)
    app.include_router(health_router)
    app.include_router(printing_router)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            api_response = ApiResponse.create_error(constants.ERR_NOT_FOUND, meta=None)
            return JSONResponse(
                status_code=404,
                content=api_response.model_dump(by_alias=True),
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


app = create_app()
