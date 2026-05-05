# Liminal — Project Plan

> Monthly contractor invoice generator. Fetches a Clockify timesheet link, fills a Word template, converts to PDF, ready to email manually.

---

## Phase 1 — Local Foundation

- [x] **Project scaffolding** — `backend/` with pipenv, Python 3.12 venv
- [x] **Dependencies installed** — `docxtpl`, `clockify-api-client`, `requests`, `python-dotenv`
- [x] **Clockify credentials** — API key, workspace ID, user ID stored in `.env`
- [x] **Invoice DOCX template** — manually edited with `docxtpl` Jinja placeholders
- [x] **`.gitignore`** — covers `.env`, `output/`, `__pycache__/`, `.venv/`
- [x] **Initial git commit** — pushed to GitHub

---

## Phase 2 — Core Modules (each runs as a standalone smoke test)

- [x] **`src/clockify.py`** — creates Clockify shared report, returns public URL
- [x] **`src/dates.py`** — `MonthRange`, `last_month()`, ISO-format helpers
- [x] **`src/render.py`** — fills DOCX template with context dict, saves to `output/`
- [ ] **`src/pdf.py`** — converts DOCX to PDF via LibreOffice headless
- [ ] **Pipfile cleanup** — change `python_version = "3.9"` → `"3.12"`

---

## Phase 3 — Wire It Together

- [ ] **`src/config.py`** — load `invoice_config.json` (sender, client, items, totals)
- [ ] **`config/invoice_config.json`** — editable per-invoice data
- [ ] **`generate.py`** — single CLI entry point that orchestrates everything:
  - [ ] Resolve target month (default: last month, override with `--month YYYY-MM`)
  - [ ] Auto-increment invoice number (or override with `--invoice-number`)
  - [ ] Call Clockify, get shared link
  - [ ] Build context dict (sender, client, items, notes, total)
  - [ ] Render DOCX
  - [ ] Convert to PDF
  - [ ] Print output paths
- [ ] **CLI flags**: `--month`, `--invoice-number`, `--skip-clockify`, `--skip-pdf`
- [ ] **End-to-end smoke test** — generate a real invoice for a past month locally

---

## Phase 4 — GitHub Actions Automation

- [ ] **`.github/workflows/monthly.yml`** — scheduled monthly + `workflow_dispatch`
- [ ] **Repo secrets** — `CLOCKIFY_API_KEY`, `CLOCKIFY_WORKSPACE_ID`, `CLOCKIFY_USER_ID`
- [ ] **Install LibreOffice in runner** — `sudo apt install libreoffice`
- [ ] **Upload PDF as workflow artifact** (not committed to repo)
- [ ] **Notification** — email/Slack/issue when ready for review (since GitHub doesn't email on success by default)
- [ ] **First successful CI run** — verify the artifact downloads and looks right

---

## Phase 5 — Polish (optional, do later)

- [ ] **Tests** — unit tests for `dates.py`, mock Clockify in tests for `clockify.py`
- [ ] **Logging** — replace `print()` with `logging` module, log to file
- [ ] **Error reporting** — better failure messages when Clockify/template/PDF step breaks
- [ ] **Multi-client support** — config could support multiple clients, pick via flag
- [ ] **Track sent invoices** — small SQLite or JSON log of "Invoice 17 sent on 2026-04-10"

---

## Known Issues & Notes

- Pipfile still pins `python_version = "3.9"` — gives a harmless warning on every run
- Each monthly Clockify run creates a new shared link — they pile up in Clockify → Shared Reports tab. Consider pruning old ones manually, or add a cleanup step.
- LibreOffice headless conversion can be flaky on first run; second run usually works.
- GitHub Actions disables scheduled workflows after 60 days of repo inactivity (private repos especially).
