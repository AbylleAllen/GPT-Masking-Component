from pathlib import Path
from urllib.parse import urlparse
from typing import Tuple


def identifyTypeAndParentDirectory(uri: str) -> Tuple[bool, str]:
    parsed = urlparse(uri)
    path = Path(parsed.path)

    pdf_flag = path.suffix.lower() == ".pdf"
    parent_dir = f"{parsed.scheme}://{path.parent.as_posix()}/"

    return pdf_flag, parent_dir
