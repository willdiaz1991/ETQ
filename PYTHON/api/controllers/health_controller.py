from fastapi import APIRouter

from api.response.api_response import ApiResponse

health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get("", summary="Health Check", description="Confirms that the API is available", response_model=ApiResponse[str])
def health_check() -> ApiResponse[str]:
    return ApiResponse.create_successful(result="API disponible", meta=None, messages=None)
