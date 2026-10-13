from pydantic import BaseModel, ConfigDict, Field


class Metadata(BaseModel):
    total_items: int = Field(..., alias="totalItems")
    status: str

    model_config = ConfigDict(populate_by_name=True)
