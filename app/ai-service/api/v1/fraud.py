"""
Fraud detection endpoint.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from schemas.errors import ErrorEnvelope

from schemas.fraud import FraudDetectionRequest, FraudDetectionResponse
from services.fraud_detection import detect_fraud

logger = logging.getLogger(__name__)

router = APIRouter(tags=["fraud"])


@router.post(
    "/fraud/detect",
    response_model=FraudDetectionResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful fraud detection",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successfully analyzed claims",
                            "value": {
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
                        "empty_claims_list": {
                            "summary": "Empty claims list",
                            "value": {
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "message": "Request validation failed",
                                    "details": [{"type": "too_short", "loc": ["body", "claims"], "msg": "List should have at least 1 item after validation, not 0", "input": []}]
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
async def detect_fraud_endpoint(request: FraudDetectionRequest) -> FraudDetectionResponse:
    """
    Analyse a batch of claims for suspicious patterns.

    Returns a ``fraud_risk_score`` (0-1) for each claim.  Claims that are
    statistical outliers relative to the batch are flagged with
    ``is_flagged=true``.
    """
    try:
        results = detect_fraud(request.claims)
        return FraudDetectionResponse(
            results=results,
            flagged_count=sum(r.is_flagged for r in results),
            anchor_metadata=request.anchor_metadata
        )
    except Exception as exc:
        logger.error("Fraud detection failed: %s", exc)
        raise HTTPException(status_code=500, detail="Fraud detection failed") from exc
