from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .metadata import Metadata

T = TypeVar("T")


class ApiResponseBase(BaseModel, Generic[T]):
    error_message: Optional[str] = Field(None, alias="errorMessage")
    is_error: bool = Field(..., alias="isError")
    is_successful: bool = Field(..., alias="isSuccessful")
    messages: Optional[List[str]] = None
    meta: Optional[Metadata] = None
    result: Optional[T] = None

    model_config = ConfigDict(populate_by_name=True)
