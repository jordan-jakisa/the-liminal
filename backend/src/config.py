import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BACKEND_DIR / "config" / "invoice_config.json"

def load_invoice_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_FILE}")
    with CONFIG_FILE.open() as f:
        return json.load(f)

if __name__ == "__main__":
    cfg = load_invoice_config()
    print(f"Sender:  {cfg['sender']['name']}")
    print(f"Client:  {cfg['client']['name']}")
    print(f"Items:   {len(cfg['items'])}")
    print(f"Total:   {cfg['total']} {cfg.get('payment_suffix', '')}")