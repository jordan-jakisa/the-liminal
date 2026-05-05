import shutil
import subprocess
from pathlib import Path


def _try_docx2pdf(docx_path: Path) -> Path | None:
    """Return PDF path on success, None if docx2pdf isn't available or fails."""
    try:
        from docx2pdf import convert
    except ImportError:
        return None
    try:
        pdf_path = docx_path.with_suffix(".pdf")
        convert(str(docx_path), str(pdf_path))
        return pdf_path if pdf_path.exists() else None
    except Exception:
        return None


def _try_libreoffice(docx_path: Path) -> Path | None:
    """Return PDF path on success, None if LibreOffice isn't available."""
    soffice = (
        shutil.which("soffice")
        or shutil.which("libreoffice")
        or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    )
    if not Path(soffice).exists() and not shutil.which(soffice):
        return None
    outdir = docx_path.parent
    result = subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(docx_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return None
    pdf_path = outdir / (docx_path.stem + ".pdf")
    return pdf_path if pdf_path.exists() else None


def docx_to_pdf(docx_path: Path) -> Path:
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    # Try docx2pdf first (preferred locally on macOS)
    pdf = _try_docx2pdf(docx_path)
    if pdf:
        return pdf

    # Fall back to LibreOffice (works in CI)
    pdf = _try_libreoffice(docx_path)
    if pdf:
        return pdf

    raise RuntimeError(
        "PDF conversion failed: neither docx2pdf nor LibreOffice produced output."
    )


if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent.parent
    docx = backend_dir / "output" / "Invoice_017_SMOKE_TEST.docx"
    print(f"Converted: {docx_to_pdf(docx)}")
