from typing import List, Optional, TypeVar

from .api_response_base import ApiResponseBase
from .metadata import Metadata

T = TypeVar("T")


class ApiResponse(ApiResponseBase[T]):

    @classmethod
    def create_successful(cls, result: T, meta: Optional[Metadata] = None, messages: Optional[List[str]] = None) -> "ApiResponse[T]":
        return cls(is_successful=True, is_error=False, result=result, messages=messages, meta=meta)

    @classmethod
    def create_unsuccessful(cls, messages: List[str], meta: Optional[Metadata] = None) -> "ApiResponse[T]":
        return cls(is_successful=False, is_error=False, messages=messages, meta=meta)

    @classmethod
    def create_error(cls, error_message: str, meta: Optional[Metadata] = None) -> "ApiResponse[T]":
        return cls(is_successful=False, is_error=True, error_message=error_message, meta=meta)
