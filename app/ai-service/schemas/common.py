from typing import Optional
from pydantic import BaseModel, Field


class AnchorMetadata(BaseModel):
    campaign_ref: Optional[str] = Field(None, description="Campaign reference ID", example="CAM-2024-001")
    claim_id: Optional[str] = Field(None, description="Claim ID", example="CLAIM-12345")
    package_id: Optional[str] = Field(None, description="Aid package ID", example="PKG-ABC-789")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_ref": "CAM-2024-001",
                    "claim_id": "CLAIM-12345",
                    "package_id": "PKG-ABC-789"
                }
            ]
        }
    }
