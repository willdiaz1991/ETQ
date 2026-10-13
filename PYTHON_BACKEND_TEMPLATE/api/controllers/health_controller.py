from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api.response.api_response import ApiResponse
from infrastructure.logging.LoggerImplements import LoggerImplements

health_router = APIRouter(prefix="/health", tags=["Health"])
logger = LoggerImplements("HealthController")


def get_available_databases():
    from infrastructure.database.db_context import get_available_databases as load_available_databases

    return load_available_databases()


def get_db_session(db_name):
    from infrastructure.database.db_context import get_db_session as load_db_session

    return load_db_session(db_name)


@health_router.get("", summary="Full Health Check", description="Checks all database connections", response_model=ApiResponse)
async def health_check_all():
    method = "health_check_all"
    logger.log_information("Starting full health check...", method)

    try:
        database_names = get_available_databases()
    except Exception as exc:
        logger.log_error(f"Health check initialization failed: {exc}", method)
        error_response = ApiResponse.create_error("Could not initialize the database health check")
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=error_response.model_dump(by_alias=True))

    healthy_dbs = []
    failed_dbs = []

    for db_name in database_names:
        try:
            with get_db_session(db_name) as session:
                session.execute(text("SELECT 1 FROM DUAL"))
                healthy_dbs.append(db_name)
        except Exception as e:
            logger.log_error(f"Health check failed for {db_name}: {e}", method)
            failed_dbs.append(db_name)

    if failed_dbs:
        error_response = ApiResponse.create_error(f"Failed DBs: {', '.join(failed_dbs)}")
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=error_response.model_dump(by_alias=True))

    return ApiResponse.create_successful(result="All databases are healthy", meta=None, messages=None)
