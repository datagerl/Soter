"""
v1 anonymization endpoint.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from schemas.errors import ErrorEnvelope

from schemas.anonymization import AnonymizeRequest, AnonymizeResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["anonymization"])


@router.post(
    "/ai/anonymize",
    response_model=AnonymizeResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful anonymization",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful anonymization",
                            "value": {
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
                        "missing_text": {
                            "summary": "Missing required text field",
                            "value": {
                                "error": {
                                    "code": "VALIDATION_ERROR",
                                    "message": "Request validation failed",
                                    "details": [{"type": "missing", "loc": ["body", "text"], "msg": "Field required", "input": {}}]
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
async def anonymize_text(request: AnonymizeRequest):
    """Anonymize names, locations, and dates before text is sent to external LLMs."""
    import main as _main

    logger.info("Processing privacy-preserving anonymization request")

    try:
        result = _main.pii_scrubber_service.anonymize(request.text)
        return AnonymizeResponse(
            success=True,
            anchor_metadata=request.anchor_metadata,
            **result
        )
    except Exception as e:
        logger.error(f"Anonymization failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to anonymize text")
