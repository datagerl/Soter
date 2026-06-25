from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from schemas.common import AnchorMetadata


class HumanitarianVerificationRequest(BaseModel):
    aid_claim: str = Field(min_length=10, description="Aid claim to verify", example="Family of 5 needs food assistance due to flooding in region X")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting evidence texts", example=["Photo of damaged home", "Local authority report"])
    context_factors: Dict[str, Any] = Field(default_factory=dict, description="Additional context factors", example={"disaster_type": "flood", "household_size": 5})
    provider_preference: Literal["auto", "test", "openai", "groq"] = Field("auto", description="Preferred AI provider", example="test")
    timeout: Optional[float] = Field(default=None, description="Request-level timeout in seconds for provider call", example=30.0)
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "aid_claim": "Family of 5 needs food assistance due to flooding in region X",
                    "supporting_evidence": ["Photo of damaged home", "Local authority report"],
                    "context_factors": {"disaster_type": "flood", "household_size": 5},
                    "provider_preference": "test",
                    "timeout": 30.0,
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345",
                        "package_id": "PKG-ABC-789"
                    }
                }
            ]
        }
    }


class HumanitarianVerificationResponse(BaseModel):
    success: bool = Field(description="Whether verification was successful", example=True)
    provider: Optional[str] = Field(None, description="AI provider used", example="test")
    model: Optional[str] = Field(None, description="Model used", example="test-model-v1")
    prompt_variant: Optional[str] = Field(None, description="Prompt variant", example="v1")
    verification: Optional[Dict[str, Any]] = Field(None, description="Verification details", example={"valid": True, "confidence": 0.9, "reasoning": "Claim matches standard humanitarian criteria"})
    error: Optional[str] = Field(None, description="Error message if failed")
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "provider": "test",
                    "model": "test-model-v1",
                    "prompt_variant": "v1",
                    "verification": {"valid": True, "confidence": 0.9, "reasoning": "Claim matches standard humanitarian criteria"},
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345",
                        "package_id": "PKG-ABC-789"
                    }
                }
            ]
        }
    }