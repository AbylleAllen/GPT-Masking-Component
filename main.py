from fastapi import FastAPI, HTTPException
from urllib.parse import urlparse
from pathlib import Path
import uuid

from identification.doc_identifier import identifyTypeAndParentDirectory
from conversion.doc_converter import convertToImage
from masking.mask_engine import maskPartial, maskFull
from masking.mask_utils import bbox_to_list, compute_masked_value
from models.schemas import (
    MaskingRequest,
    MaskingResponse,
    MaskingMetadata,
    MaskingDetail
)

app = FastAPI(
    title="Document Masking Service",
    version="1.0.0"
)


def processMasking(request: MaskingRequest) -> MaskingResponse:
    pdf_flag, parent_dir = identifyTypeAndParentDirectory(request.inputFileUri)

    # Normalize input → image paths
    if pdf_flag:
        image_paths = convertToImage(
            request.inputFileUri,
            request.documentPassword
        )
    else:
        image_paths = [
            Path(urlparse(request.inputFileUri).path).as_posix()
        ]

    masked_fields = []
    masking_details = {}

    field_map = {f.field: f for f in request.extractedFields}

    for rule in request.maskingRules:
        extracted = field_map.get(rule.field)
        if not extracted:
            continue

        boxes = bbox_to_list(extracted.boundingBoxes)
        masked_fields.append(rule.field)

        masked_value = compute_masked_value(
            extracted.value,
            rule.maskingConfig,
            rule.type
        )

        # Apply visual masking
        for image_path in image_paths:
            if rule.type == "PARTIAL":
                maskPartial(
                    image_path,
                    boxes.copy(),
                    rule.maskingConfig,
                    extracted.value
                )
            else:
                maskFull(
                    image_path,
                    boxes.copy(),
                    rule.maskingConfig,
                    extracted.value
                )

        masking_details[rule.field] = MaskingDetail(
            originalValue=extracted.value,
            maskedValue=masked_value,
            maskType=rule.type,
            showFirst=rule.maskingConfig.maskFirst or None,
            showLast=rule.maskingConfig.maskLast or None,
            maskChar=rule.maskingConfig.maskChar
        )

    # Build masked file URI (logical output)
    masked_filename = (
        f"masked_{Path(image_paths[0]).stem}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )
    masked_file_uri = f"{parent_dir}{masked_filename}"

    return MaskingResponse(
        maskedFileUri=masked_file_uri,
        maskedFields=masked_fields,
        metadata=MaskingMetadata(
            maskingMethod="black_box",
            fieldsProcessed=len(masked_fields),
            documentType=request.documentType,
            maskingDetails=masking_details
        )
    )


@app.post("/mask", response_model=MaskingResponse)
async def mask_document(request: MaskingRequest):
    """
    Applies masking/redaction to the document
    based on extracted fields and masking rules.
    """
    try:
        return processMasking(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "masking-service"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
