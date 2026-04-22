from datetime import date
from pathlib import Path
from tempfile import template
from docxtpl import DocxTemplate

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = BACKEND_DIR / "template" / "invoice_template.docx"
OUTPUT_DIR = BACKEND_DIR / "output"

def render_invoice(context: dict, output_path: Path):
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE}")
    template = DocxTemplate(str(TEMPLATE))
    template.render(context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.save(str(output_path))
    return output_path
        
if __name__ == "__main__":
    # Smoke test with dummy data matching your Invoice 16
    dummy_context = {
    }

    output = OUTPUT_DIR / "Invoice_017_SMOKE_TEST.docx"
    render_invoice(dummy_context, output)
    print(f"Rendered: {output}")