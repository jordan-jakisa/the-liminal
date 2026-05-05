"""Create or fetch a Clockify shared report and return its public URL."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["CLOCKIFY_API_KEY"]
WORKSPACE_ID = os.environ["CLOCKIFY_WORKSPACE_ID"]
USER_ID = os.environ["CLOCKIFY_USER_ID"]

REPORTS_HOST = "https://reports.api.clockify.me/v1"


def _build_payload(start: str, end: str, name: str) -> dict:
    return {
        "name": name,
        "isPublic": True,
        "type": "SUMMARY",
        "filter": {
            "dateRangeStart": start,
            "dateRangeEnd": end,
            "users": {"contains": "CONTAINS", "ids": [USER_ID], "status": "ACTIVE"},
            "userGroups": {"contains": "CONTAINS", "ids": [], "status": "ACTIVE"},
            "clients": {"contains": "CONTAINS", "ids": [], "status": "ACTIVE"},
            "projects": {"contains": "CONTAINS", "ids": [], "status": "ACTIVE"},
            "tasks": {"contains": "CONTAINS", "ids": [], "status": "ACTIVE"},
            "tags": {
                "containedInTimeentry": "CONTAINS_ONLY",
                "contains": "CONTAINS",
                "ids": [],
                "status": "ACTIVE",
            },
            "summaryFilter": {"groups": ["PROJECT"], "sortColumn": "GROUP"},
            "exportType": "JSON",
            "amountShown": "HIDE_AMOUNT",
        },
    }


def _extract_url(data: dict) -> str:
    """Pull the public URL out of a shared-report response."""
    for key in ("sharedUrl", "url", "publicUrl"):
        if data.get(key):
            return data[key]
    if "id" in data:
        return f"https://app.clockify.me/shared/{data['id']}"
    raise RuntimeError(f"Unexpected Clockify response: {data}")


def _find_existing_report(name: str) -> str | None:
    """List shared reports and return the URL of the one matching `name`, if any."""
    url = f"{REPORTS_HOST}/workspaces/{WORKSPACE_ID}/shared-reports"
    headers = {"X-Api-Key": API_KEY}
    response = requests.get(url, headers=headers, timeout=30)
    if not response.ok:
        return None
    reports = response.json()
    items = reports if isinstance(reports, list) else reports.get("reports", [])
    for r in items:
        if r.get("name") == name:
            return _extract_url(r)
    return None


def create_shared_report(start: str, end: str, name: str) -> str:
    """Create a shared report or, if one with this name already exists, return that one."""
    url = f"{REPORTS_HOST}/workspaces/{WORKSPACE_ID}/shared-reports"
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}
    payload = _build_payload(start, end, name)

    response = requests.post(url, json=payload, headers=headers, timeout=90)

    if response.ok:
        return _extract_url(response.json())

    body = response.text
    if "already exists" in body.lower():
        existing = _find_existing_report(name)
        if existing:
            print(f"Reusing existing shared report: {name}")
            return existing
        raise RuntimeError(f"Report '{name}' exists but could not be retrieved.")

    print("STATUS:", response.status_code)
    print("BODY:", body)
    response.raise_for_status()
    raise RuntimeError("Unreachable")


if __name__ == "__main__":
    url = create_shared_report(
        start="2026-03-01T00:00:00.000Z",
        end="2026-03-31T23:59:59.000Z",
        name="Test - delete me",
    )
    print("Shared URL:", url)
