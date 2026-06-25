"""
v1 OCR endpoint.

Extracted from the legacy flat router so the route logic lives in a
single place and is referenced by both the /v1 and the legacy /ai mounts.
"""

import base64
import io
import time
from typing import Annotated, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

import tasks
from schemas.ocr import OCRResponse
from schemas.errors import ErrorEnvelope
from services.ocr_job import run_ocr_from_bytes
from config import settings

router = APIRouter(tags=["ocr"])
limiter = Limiter(key_func=get_remote_address)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
    "image/bmp",
    "image/tiff",
    "image/webp",
}

class QueuedOCRResponse(BaseModel):
    success: bool = Field(description="Whether job was queued successfully", example=True)
    task_id: str = Field(description="Unique task identifier", example="task-12345")
    status: str = Field(description="Current task status", example="pending")
    message: str = Field(description="Status message", example="OCR job queued for processing")
    status_url: str = Field(description="URL to poll for task status", example="/v1/ai/jobs/task-12345")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "task_id": "task-12345",
                    "status": "pending",
                    "message": "OCR job queued for processing",
                    "status_url": "/v1/ai/jobs/task-12345"
                }
            ]
        }
    }


@router.post(
    "/ai/ocr",
    response_model=OCRResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successful OCR processing",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successfully extracted text from image",
                            "value": {
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
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid image or content type",
            "model": ErrorEnvelope,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_content_type": {
                            "summary": "Invalid image content type",
                            "value": {
                                "error": {
                                    "code": "invalid_content_type",
                                    "message": "Invalid content type: text/plain. Allowed: image/jpeg, image/png, image/jpg, image/bmp, image/tiff, image/webp",
                                    "details": None
                                }
                            }
                        },
                        "empty_image": {
                            "summary": "Empty uploaded image",
                            "value": {
                                "error": {
                                    "code": "empty_image",
                                    "message": "Uploaded image is empty",
                                    "details": None
                                }
                            }
                        },
                        "invalid_image": {
                            "summary": "Could not decode image",
                            "value": {
                                "error": {
                                    "code": "invalid_image",
                                    "message": "Could not decode image: cannot identify image file <_io.BytesIO object at 0x...>",
                                    "details": None
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
@limiter.limit(settings.request_rate_limit)
async def process_ocr(
    request: Request,
    image: Annotated[UploadFile, File(description="Image file to process")],
    anchor_metadata: Annotated[Optional[str], Form(description="JSON encoded AnchorMetadata")] = None,
) -> OCRResponse:
    """Extract text fields from an uploaded document image."""
    start_time = time.time()

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_content_type",
                "message": (
                    f"Invalid content type: {image.content_type}. "
                    f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
                ),
            },
        )

    try:
        contents = await image.read()

        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "empty_image",
                    "message": "Uploaded image is empty",
                },
            )

        _validate_image_bytes(contents)
        result = run_ocr_from_bytes(contents, anchor_metadata)

        return OCRResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        return OCRResponse(
            success=False,
            error={
                "code": "processing_error",
                "message": str(e),
            },
            processing_time_ms=processing_time_ms,
            anchor_metadata=None, # Cannot easily re-parse here without duplicating, so omit or ignore
        )


@router.post(
    "/ai/ocr/jobs",
    response_model=QueuedOCRResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: {
            "description": "OCR job successfully queued",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successfully queued OCR job",
                            "value": {
                                "success": True,
                                "task_id": "task-12345",
                                "status": "pending",
                                "message": "OCR job queued for processing",
                                "status_url": "/v1/ai/jobs/task-12345"
                            }
                        }
                    }
                }
            }
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid image or content type",
            "model": ErrorEnvelope,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_content_type": {
                            "summary": "Invalid image content type",
                            "value": {
                                "error": {
                                    "code": "invalid_content_type",
                                    "message": "Invalid content type: text/plain. Allowed: image/jpeg, image/png, image/jpg, image/bmp, image/tiff, image/webp",
                                    "details": None
                                }
                            }
                        },
                        "empty_image": {
                            "summary": "Empty uploaded image",
                            "value": {
                                "error": {
                                    "code": "empty_image",
                                    "message": "Uploaded image is empty",
                                    "details": None
                                }
                            }
                        },
                        "invalid_image": {
                            "summary": "Could not decode image",
                            "value": {
                                "error": {
                                    "code": "invalid_image",
                                    "message": "Could not decode image: cannot identify image file <_io.BytesIO object at 0x...>",
                                    "details": None
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
@limiter.limit(settings.request_rate_limit)
async def queue_ocr_job(
    request: Request,
    image: Annotated[UploadFile, File(description="Image file to process")],
    anchor_metadata: Annotated[Optional[str], Form(description="JSON encoded AnchorMetadata")] = None,
) -> QueuedOCRResponse:
    """Queue OCR processing and return immediately with a pollable job URL."""
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_content_type",
                "message": (
                    f"Invalid content type: {image.content_type}. "
                    f"Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}"
                ),
            },
        )

    contents = await image.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "empty_image",
                "message": "Uploaded image is empty",
            },
        )

    _validate_image_bytes(contents)

    task_id = tasks.create_task(
        task_type="ocr",
        payload={
            "image_base64": base64.b64encode(contents).decode("ascii"),
            "content_type": image.content_type,
            "filename": image.filename,
            "anchor_metadata": anchor_metadata,
        },
    )

    return QueuedOCRResponse(
        success=True,
        task_id=task_id,
        status="pending",
        message="OCR job queued for processing",
        status_url=f"/v1/ai/jobs/{task_id}",
    )


def _validate_image_bytes(contents: bytes) -> None:
    from PIL import Image

    try:
        Image.open(io.BytesIO(contents)).verify()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_image",
                "message": f"Could not decode image: {str(e)}",
            },
        )
