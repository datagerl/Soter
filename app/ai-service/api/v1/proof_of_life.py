"""
v1 proof-of-life endpoint.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from schemas.common import AnchorMetadata
from schemas.errors import ErrorEnvelope

logger = logging.getLogger(__name__)

router = APIRouter(tags=["proof-of-life"])


class ProofOfLifeRequest(BaseModel):
    """Request model for proof-of-life selfie and optional burst frames."""

    selfie_image_base64: str = Field(description="Base64 encoded selfie image", example="base64encodedimage==")
    burst_images_base64: Optional[List[str]] = Field(None, description="Optional burst frames as base64 encoded images", example=["base64encodedburst1==", "base64encodedburst2=="])
    confidence_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Custom confidence threshold", example=0.7)
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "selfie_image_base64": "base64encodedimage==",
                    "burst_images_base64": ["base64encodedburst1==", "base64encodedburst2=="],
                    "confidence_threshold": 0.7,
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345"
                    }
                }
            ]
        }
    }


class ProofOfLifeResponse(BaseModel):
    """Response model for proof-of-life analysis."""

    is_real_person: bool = Field(description="Whether person is real", example=True)
    confidence: float = Field(description="Confidence score", example=0.95)
    threshold: float = Field(description="Threshold used", example=0.7)
    checks: Dict[str, Any] = Field(description="Detailed checks", example={"face_detected": True, "liveness_signals": ["blink_detected"]})
    reason: str = Field(description="Analysis reason", example="Live person detected with high confidence")
    anchor_metadata: Optional[AnchorMetadata] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_real_person": True,
                    "confidence": 0.95,
                    "threshold": 0.7,
                    "checks": {"face_detected": True, "liveness_signals": ["blink_detected"]},
                    "reason": "Live person detected with high confidence",
                    "anchor_metadata": {
                        "campaign_ref": "CAM-2024-001",
                        "claim_id": "CLAIM-12345"
                    }
                }
            ]
        }
    }


@router.post(
    "/ai/proof-of-life",
    response_model=ProofOfLifeResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful proof-of-life analysis",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successfully verified live person",
                            "value": {
                                "is_real_person": True,
                                "confidence": 0.95,
                                "threshold": 0.7,
                                "checks": {"face_detected": True, "liveness_signals": ["blink_detected"]},
                                "reason": "Live person detected with high confidence",
                                "anchor_metadata": {
                                    "campaign_ref": "CAM-2024-001",
                                    "claim_id": "CLAIM-12345"
                                }
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error",
            "model": ErrorEnvelope,
            "content": {
                "application/json": {
                    "examples": {
                        "missing_selfie": {
                            "summary": "Missing required selfie_image_base64",
                            "value": {
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "message": "Request validation failed",
                                    "details": [{"type": "missing", "loc": ["body", "selfie_image_base64"], "msg": "Field required", "input": {}}]
                                }
                            }
                        },
                        "invalid_threshold": {
                            "summary": "Confidence threshold out of range",
                            "value": {
                                "error": {
                                    "code": "HTTP_422",
                                    "message": "Confidence threshold must be between 0 and 1",
                                    "details": None
                                }
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "model": ErrorEnvelope
        }
    }
)
async def analyze_proof_of_life(request: ProofOfLifeRequest):
    """
    Analyse a selfie image (with optional burst frames) for proof-of-life.

    Returns ``is_real_person`` and a confidence score.  When burst frames
    are provided, the service additionally checks for liveness signals
    such as blink detection and head movement.
    """
    import main as _main

    logger.info("Processing proof-of-life verification request")

    try:
        result = _main.proof_of_life_analyzer.analyze(
            selfie_image_base64=request.selfie_image_base64,
            burst_images_base64=request.burst_images_base64,
            confidence_threshold=request.confidence_threshold,
        )
        # Ensure we return a ProofOfLifeResponse object with anchor_metadata
        if isinstance(result, dict):
            return ProofOfLifeResponse(
                **result,
                anchor_metadata=request.anchor_metadata
            )
        else:
            # If result is already a BaseModel instance
            result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()
            return ProofOfLifeResponse(
                **result_dict,
                anchor_metadata=request.anchor_metadata
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Proof-of-life processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to process proof-of-life request"
        )
