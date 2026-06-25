from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from schemas.common import AnchorMetadata


class ClaimMetadata(BaseModel):
    claim_id: str = Field(description="Unique claim identifier", example="CLAIM-12345")
    ip_address: Optional[str] = Field(None, description="IP address of claimant", example="192.168.1.1")
    evidence_hash: Optional[str] = Field(None, description="Hash of evidence file", example="sha256:abc123def456")
    amount: Optional[float] = Field(None, description="Requested aid amount", example=1000.0)
    location: Optional[str] = Field(None, description="Claim location", example="Region X")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata", example={"priority": "high"})


class FraudDetectionRequest(BaseModel):
    claims: List[ClaimMetadata] = Field(min_length=1, description="List of claims to analyze")
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "claims": [
                        {
                            "claim_id": "CLAIM-12345",
                            "ip_address": "192.168.1.1",
                            "evidence_hash": "sha256:abc123def456",
                            "amount": 1000.0,
                            "location": "Region X",
                            "extra": {"priority": "high"}
                        },
                        {
                            "claim_id": "CLAIM-67890",
                            "ip_address": "192.168.1.2",
                            "amount": 900.0,
                            "location": "Region Y"
                        }
                    ],
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001"
                    }
                }
            ]
        }
    }


class ClaimFraudResult(BaseModel):
    claim_id: str = Field(description="Claim identifier", example="CLAIM-12345")
    fraud_risk_score: float = Field(ge=0.0, le=1.0, description="Risk score 0-1", example=0.15)
    is_flagged: bool = Field(description="Whether claim is flagged", example=False)
    reason: Optional[str] = Field(None, description="Flag reason if applicable", example="No issues detected")


class FraudDetectionResponse(BaseModel):
    results: List[ClaimFraudResult] = Field(description="Fraud results for each claim")
    flagged_count: int = Field(description="Number of flagged claims", example=0)
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "results": [
                        {
                            "claim_id": "CLAIM-12345",
                            "fraud_risk_score": 0.15,
                            "is_flagged": False,
                            "reason": "No issues detected"
                        },
                        {
                            "claim_id": "CLAIM-67890",
                            "fraud_risk_score": 0.05,
                            "is_flagged": False
                        }
                    ],
                    "flagged_count": 0,
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001"
                    }
                }
            ]
        }
    }
