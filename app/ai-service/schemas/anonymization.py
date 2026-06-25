from typing import Dict, Optional

from pydantic import BaseModel, Field
from schemas.common import AnchorMetadata


class AnonymizeRequest(BaseModel):
    text: str = Field(min_length=1, description="Input text to anonymize before LLM processing", example="John Doe from New York submitted a claim on 2024-01-15")
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "John Doe from New York submitted a claim on 2024-01-15",
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345",
                        "package_id": "PKG-ABC-789"
                    }
                }
            ]
        }
    }


class PIISummary(BaseModel):
    names: int = Field(description="Number of names detected", example=1)
    locations: int = Field(description="Number of locations detected", example=1)
    dates: int = Field(description="Number of dates detected", example=1)
    total: int = Field(description="Total PII items detected", example=3)


class AnonymizeResponse(BaseModel):
    success: bool = Field(description="Whether anonymization was successful", example=True)
    anonymized_text: str = Field(description="Text with PII anonymized", example="[NAME] from [LOCATION] submitted a claim on [DATE]")
    original_length: int = Field(description="Length of original text", example=52)
    pii_summary: PIISummary
    token_counts: Dict[str, int] = Field(default_factory=dict, description="Token count statistics")
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "anonymized_text": "[NAME] from [LOCATION] submitted a claim on [DATE]",
                    "original_length": 52,
                    "pii_summary": {
                        "names": 1,
                        "locations": 1,
                        "dates": 1,
                        "total": 3
                    },
                    "token_counts": {},
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345",
                        "package_id": "PKG-ABC-789"
                    }
                }
            ]
        }
    }
