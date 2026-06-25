from typing import Optional
from pydantic import BaseModel, Field
from schemas.common import AnchorMetadata


class OCRFieldResult(BaseModel):
    value: str = Field(description="Extracted field value", example="John Doe")
    confidence: float = Field(0.0, description="Confidence score", example=0.95)


class OCRData(BaseModel):
    fields: dict[str, OCRFieldResult] = Field(description="Extracted fields", example={"name": {"value": "John Doe", "confidence": 0.95}})
    raw_text: str = Field(description="Raw extracted text", example="John Doe\nID: 12345")
    processing_time_ms: int = Field(description="Processing time in milliseconds", example=450)


class OCRResponse(BaseModel):
    success: bool = Field(description="Whether OCR was successful", example=True)
    data: OCRData | None = Field(None, description="OCR data if successful")
    error: dict[str, str] | None = Field(None, description="Error details if failed", example={"code": "processing_error", "message": "Failed to process image"})
    processing_time_ms: int = Field(description="Total processing time in milliseconds", example=500)
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {
                        "fields": {"name": {"value": "John Doe", "confidence": 0.95}},
                        "raw_text": "John Doe\nID: 12345",
                        "processing_time_ms": 450
                    },
                    "processing_time_ms": 500,
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345"
                    }
                },
                {
                    "success": False,
                    "error": {"code": "processing_error", "message": "Failed to process image"},
                    "processing_time_ms": 100,
                    "anchor_metadata": None
                }
            ]
        }
    }
