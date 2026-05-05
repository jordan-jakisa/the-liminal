from pathlib import Path
from docxtpl import DocxTemplate, RichText

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = BACKEND_DIR / "template" / "invoice_template.docx"
OUTPUT_DIR = BACKEND_DIR / "output"


def _build_timesheet_link(tpl: DocxTemplate, url: str | None) -> RichText:
    rt = RichText()
    if url:
        rt.add(
            "Timesheet",
            url_id=tpl.build_url_id(url),
            color="0563C1",
            underline=True,
        )
    else:
        rt.add("(unavailable)")
    return rt


def render_invoice(context: dict, output_path: Path) -> Path:
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE}")
    tpl = DocxTemplate(str(TEMPLATE))
    context["timesheet_url"] = _build_timesheet_link(tpl, context.get("timesheet_url"))
    tpl.render(context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tpl.save(str(output_path))
    return output_path


if __name__ == "__main__":
    dummy_context = {}
    output = OUTPUT_DIR / "Invoice_017_SMOKE_TEST.docx"
    render_invoice(dummy_context, output)
    print(f"Rendered: {output}")
