# 📄 Document Masking Service

A FastAPI-based service to **mask sensitive information** in documents (images or PDFs) using
OCR-extracted bounding boxes and configurable masking rules.

The system supports **PARTIAL** and **FULL** masking and works transparently for both
image files and multi-page PDFs.

---

## 🧱 Project Structure

```
app/
├── app.py # FastAPI entry point
├── main.py # Orchestration & response construction
│
├── models/
│   └── schemas.py # Pydantic request/response models
│
├── identification/
│   └── doc_identifier.py # Detects PDF vs Image & parent directory
│
├── conversion/
│   └── doc_converter.py # Converts PDF pages to images (PyMuPDF)
│
├── masking/
│   ├── mask_engine.py # OpenCV-based visual masking
│   └── mask_utils.py # Mask text computation & bbox helpers
│
├── temp/ # Temporary images from PDF conversion
└── README.md
```

---

## 🔁 High-Level Flow

API Request
↓
Document Identification (PDF / Image)
↓
PDF → Image Conversion (if needed)
↓
Masking Rules mapped to Extracted Fields
↓
OpenCV Masking on Images
↓
Masked Metadata Construction
↓
API Response

---

## 🧩 Component Breakdown

### 1️⃣ `app.py` — API Layer

- Exposes `/mask` endpoint using **FastAPI**
- Accepts `MaskingRequest`
- Returns `MaskingResponse`
- Handles validation & error responses

**No business logic lives here**

---

### 2️⃣ `main.py` — Orchestrator

Responsible for:
- Deciding PDF vs image handling
- Converting PDFs into images
- Mapping masking rules to extracted fields
- Calling visual masking functions
- Building the final response JSON

This is the **core pipeline controller**.

---

### 3️⃣ `models/schemas.py` — Data Contracts

Defines all request & response schemas using **Pydantic**:

- `MaskingRequest`
- `ExtractedField`
- `MaskingRule`
- `MaskingConfig`
- `MaskingResponse`
- `MaskingMetadata`
- `MaskingDetail`

Ensures:
- Input validation
- Typed, predictable responses
- Swagger/OpenAPI documentation

---

### 4️⃣ `identification/doc_identifier.py`

Purpose:
- Detects whether input is a **PDF or Image**
- Extracts the parent directory for output storage

Output:

```python
(pdf_flag: bool, parent_dir: str)
```

---

### 5️⃣ `conversion/doc_converter.py`

Purpose:

Converts PDFs to images using PyMuPDF

Handles password-protected PDFs

Stores output images in `temp/`

Output:

```python
List[str]  # Image paths
```

---

### 6️⃣ `masking/mask_engine.py` — Visual Masking

Uses OpenCV to:

- Draw white rectangles over sensitive regions
- Overlay masked text dynamically
- Scale font size to bounding box width

Contains:

- `maskPartial()` → First / last character masking
- `maskFull()` → Full redaction

This module only handles pixels, not business logic.

---

### 7️⃣ `masking/mask_utils.py` — Mask Logic Helpers

Contains utilities for:

- Converting bounding boxes to lists
- Computing masked values (text-only)
- Maintaining separation between logic & rendering

This ensures:

- Accurate metadata
- Audit-friendly masked values
- Consistent masking behavior


### 🧪 Supported Masking Types

**PARTIAL**
- Mask first N characters
- Mask last N characters
- Preserves formatting (spaces, slashes, hyphens)

**FULL**
- Masks all alphanumeric characters
- Keeps separators intact

---

### 📦 Example API Response

```json
{
  "maskedFileUri": "file:///app/storage/aadhaar/masked_doc_abc123.png",
  "maskedFields": ["aadhaar_number", "name", "dob"],
  "metadata": {
    "maskingMethod": "black_box",
    "fieldsProcessed": 3,
    "documentType": "AADHAAR",
    "maskingDetails": {
      "aadhaar_number": {
        "originalValue": "1234 5678 9012",
        "maskedValue": "1234 5X XX XXXX",
        "maskType": "PARTIAL",
        "showFirst": 6,
        "maskChar": "X"
      }
    }
  }
}
```

---

## 🚀 Running the Service

```bash
# Run the FastAPI app (uses `main:app`)
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

Access Swagger UI:

```bash
http://localhost:8004/docs
```

---

### Example: API Usage & Sample Request

#### POST /mask (application/json)

Upload the JSON payload:

```bash
curl -s -X POST "http://localhost:8004/mask" \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

Sample JSON payload (save as `sample_request.json`):

```json
{
  "documentId": "doc-123",
  "inputFileUri": "file:///C:/Users/Allen/Desktop/test123/back.png",
  "documentPassword": null,
  "documentType": "AADHAR",
  "extractedFields": [
    {
      "field": "aadhaar_number",
      "value": "1234 5678 9012",
      "confidence": 0.98,
      "boundingBoxes": {
        "p0": [100, 150],
        "p1": [400, 150],
        "p2": [400, 200],
        "p3": [100, 200]
      }
    }
  ],
  "maskingRules": [
    {
      "field": "aadhaar_number",
      "type": "PARTIAL",
      "maskingConfig": {
        "maskFirst": 6,
        "maskLast": 0,
        "maskChar": "X"
      }
    }
  ]
}
```

#### POST /test (upload request JSON file)

```bash
curl -s -X POST "http://localhost:8004/test" -F "file=@sample_request.json"
```

## 🔮 Extensibility

This architecture easily supports:

- Multiple output formats (PDF re-merge)
- Confidence-based masking
- Field-level masking strategies
- Async processing
- Cloud storage (S3, GCS)

---

## ✅ Design Principles Followed

- Single Responsibility per module
- Clear separation of concerns
- PDF & Image unified pipeline
- Audit-safe metadata generation
- Production-ready FastAPI setup


> Authoritative, modular, and scalable masking pipeline.
