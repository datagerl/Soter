"""
v1 humanitarian verification endpoint.
"""

import logging

from fastapi import APIRouter, status
from schemas.errors import ErrorEnvelope

from schemas.humanitarian import (
    HumanitarianVerificationRequest,
    HumanitarianVerificationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["humanitarian"])


@router.post(
    "/ai/humanitarian/verify",
    response_model=HumanitarianVerificationResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful verification",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful verification",
                            "value": {
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
                        "missing_aid_claim": {
                            "summary": "Missing required aid_claim field",
                            "value": {
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "message": "Request validation failed",
                                    "details": [{"type": "missing", "loc": ["body", "aid_claim"], "msg": "Field required", "input": {}}]
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def verify_humanitarian_claim(request: HumanitarianVerificationRequest):
    """Verify an aid claim against standardised humanitarian criteria."""
    # Delegate to the singleton owned by main.py so that monkeypatching in
    # tests (and any future dependency-injection wiring) works transparently.
    import main as _main

    logger.info("Processing humanitarian verification request")

    try:
        try:
            result = _main.humanitarian_verification_service.verify_claim(
                aid_claim=request.aid_claim,
                supporting_evidence=request.supporting_evidence,
                context_factors=request.context_factors,
                provider_preference=request.provider_preference,
                timeout=request.timeout,
            )
        except TypeError as exc:
            if "timeout" in str(exc):
                result = _main.humanitarian_verification_service.verify_claim(
                    aid_claim=request.aid_claim,
                    supporting_evidence=request.supporting_evidence,
                    context_factors=request.context_factors,
                    provider_preference=request.provider_preference,
                )
            else:
                raise exc
        return HumanitarianVerificationResponse(
            success=True,
            anchor_metadata=request.anchor_metadata,
            **result
        )
    except Exception as e:
        logger.error("Humanitarian verification failed: %s", str(e), exc_info=True)
        return HumanitarianVerificationResponse(
            success=False,
            error=str(e),
            anchor_metadata=request.anchor_metadata
        )
