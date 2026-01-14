from typing import List, Literal, Dict, Optional
from pydantic import BaseModel


class BoundingBox(BaseModel):
    p0: List[int]
    p1: List[int]
    p2: List[int]
    p3: List[int]


class ExtractedField(BaseModel):
    field: str
    value: str
    confidence: float
    boundingBoxes: BoundingBox


class MaskingConfig(BaseModel):
    maskFirst: int
    maskLast: int
    maskChar: str

class MaskingRule(BaseModel):
    field: str
    type: Literal["PARTIAL", "FULL"]
    maskingConfig: MaskingConfig


class MaskingRequest(BaseModel):
    documentId: str
    inputFileUri: str
    documentPassword: str | None
    documentType: Literal["AADHAR", "PANCARD"]
    extractedFields: List[ExtractedField]
    maskingRules: List[MaskingRule]

class MaskingDetail(BaseModel):
    originalValue: str
    maskedValue: str
    maskType: str
    showFirst: Optional[int] = None
    showLast: Optional[int] = None
    maskChar: str


class MaskingMetadata(BaseModel):
    maskingMethod: str
    fieldsProcessed: int
    documentType: str
    maskingDetails: Dict[str, MaskingDetail]


class MaskingResponse(BaseModel):
    maskedFileUri: str
    maskedFields: List[str]
    metadata: MaskingMetadata
