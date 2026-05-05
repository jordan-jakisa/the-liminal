import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from datetime import datetime

from clockify import create_shared_report
from config import load_invoice_config
from dates import MonthRange, last_month
from pdf import docx_to_pdf
from render import OUTPUT_DIR, render_invoice


def parse_month(s: str) -> MonthRange:
    """Parse 'YYYY-MM' into a MonthRange."""
    try:
        dt = datetime.strptime(s, "%Y-%m")
    except ValueError:
        raise SystemExit(f"--month must be YYYY-MM, got: {s!r}")
    return MonthRange(dt.year, dt.month)


def next_invoice_number(explicit: str | None) -> str:
    """Auto-increment from existing files in output/. Returns zero-padded 3-digit string."""
    if explicit:
        return explicit.zfill(3)
    if not OUTPUT_DIR.exists():
        return "001"
    highest = 0
    for p in OUTPUT_DIR.glob("Invoice_*"):
        parts = p.stem.split("_")
        if len(parts) >= 2 and parts[1].isdigit():
            highest = max(highest, int(parts[1]))
    return f"{highest + 1:03d}"


def build_context(
    cfg: dict, month: MonthRange, invoice_number: str, timesheet_url: str | None
) -> dict:
    preamble = cfg.get("notes_preamble", "").strip()
    if timesheet_url:
        notes = (
            f"{preamble} Here is the link to the timesheet for the associated "
            f"month of {month.human} - {timesheet_url}"
        )
    else:
        notes = f"{preamble} Timesheet for {month.human} (link unavailable)."

    total_line = cfg["total"]
    if cfg.get("payment_suffix"):
        total_line = f"{total_line} {cfg['payment_suffix']}"

    return {
        "sender_name": cfg["sender"]["name"],
        "sender_address": cfg["sender"]["address"],
        "client_name": cfg["client"]["name"],
        "client_address_line1": cfg["client"].get("address_line1", ""),
        "client_address_line2": cfg["client"].get("address_line2", ""),
        "client_address_line3": cfg["client"].get("address_line3", ""),
        "client_email": cfg["client"].get("email", ""),
        "invoice_number": invoice_number,
        "invoice_date": date.today().strftime("%d/%m/%Y"),
        "items": cfg["items"],
        "notes_preamble": cfg.get("notes_preamble", "").strip(),
        "month_human": month.human,
        "timesheet_url": timesheet_url or "(unavailable)",
        "total": cfg["total"],
        "payment_suffix": cfg.get("payment_suffix", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate monthly contractor invoice.")
    parser.add_argument("--month", help="Target month YYYY-MM (default: last month).")
    parser.add_argument(
        "--invoice-number", help="Override invoice number (default: auto-increment)."
    )
    parser.add_argument(
        "--skip-clockify", action="store_true", help="Don't call Clockify."
    )
    parser.add_argument("--skip-pdf", action="store_true", help="Only produce DOCX.")
    args = parser.parse_args()

    month = parse_month(args.month) if args.month else last_month()
    invoice_number = next_invoice_number(args.invoice_number)
    cfg = load_invoice_config()

    print(f"Month:           {month.human}")
    print(f"Invoice number:  {invoice_number}")

    # Clockify
    timesheet_url = None
    if not args.skip_clockify:
        try:
            print("Creating Clockify shared report...")
            timesheet_url = create_shared_report(
                month.iso_start,
                month.iso_end,
                name=f"Invoice timesheet - {month.human}",
            )
            print(f"Timesheet:       {timesheet_url}")
        except Exception as e:
            print(f"[warn] Clockify failed: {e}", file=sys.stderr)
            print("[warn] Continuing without timesheet URL.", file=sys.stderr)

    # Render DOCX
    context = build_context(cfg, month, invoice_number, timesheet_url)
    client_slug = cfg["client"]["name"].split()[0]
    docx_path = OUTPUT_DIR / f"Invoice_{invoice_number}_-_{client_slug}.docx"
    render_invoice(context, docx_path)
    print(f"DOCX:            {docx_path}")

    # PDF
    if not args.skip_pdf:
        pdf_path = docx_to_pdf(docx_path)
        print(f"PDF:             {pdf_path}")

    print("\nDone. Review before sending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
