import fitz
from pathlib import Path
from typing import List


def convertToImage(pdf_path: str, password: str | None) -> List[str]:
    dpi = 300
    pdf_path = Path(pdf_path)
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    doc = fitz.open(pdf_path)

    if doc.needs_pass:
        if not password or not doc.authenticate(password):
            raise ValueError("Invalid or missing PDF password")

    image_paths = []

    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=dpi)
        image_path = temp_dir / f"{pdf_path.stem}_page_{i+1}.png"
        pix.save(image_path)
        image_paths.append(str(image_path))

    doc.close()
    return image_paths
