from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(description="Error code", example="VALIDATION_ERROR")
    message: str = Field(description="Error message", example="Request validation failed")
    details: Optional[Any] = Field(None, description="Additional error details", example=[{"type": "missing", "loc": ["body", "text"], "msg": "Field required"}])


class ErrorEnvelope(BaseModel):
    error: ErrorDetail

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Request validation failed",
                        "details": [{"type": "missing", "loc": ["body", "text"], "msg": "Field required"}]
                    }
                },
                {
                    "error": {
                        "code": "HTTP_422",
                        "message": "Validation error",
                        "details": None
                    }
                }
            ]
        }
    }
