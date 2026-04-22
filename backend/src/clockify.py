import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["CLOCKIFY_API_KEY"]
WORKSPACE_ID = os.environ["CLOCKIFY_WORKSPACE_ID"]
USER_ID = os.environ["CLOCKIFY_USER_ID"]

REPORTS_HOST = "https://reports.api.clockify.me/v1"


def create_shared_report(start: str, end: str, name: str) -> str:
    url = f"{REPORTS_HOST}/workspaces/{WORKSPACE_ID}/shared-reports"
    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "name": "Test - delete me",
        "isPublic": True,
        "type": "SUMMARY",
        "filter": {
            "dateRangeStart": "2026-03-01T00:00:00.000Z",
            "dateRangeEnd": "2026-03-31T23:59:59.000Z",
            "users": {
                "contains": "CONTAINS",
                "ids": [USER_ID],
                "status": "ACTIVE",
            },
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
            "summaryFilter": {
                "groups": ["PROJECT"],
                "sortColumn": "GROUP",
            },
            "exportType": "JSON",
            "amountShown": "HIDE_AMOUNT",
        },
    }
    print("Sending payload:", json.dumps(payload, indent=2))
    response = requests.post(url, json=payload, headers=headers, timeout=90)

    if not response.ok:
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        response.raise_for_status()

    data = response.json()
    for key in ("sharedUrl", "url", "publicUrl"):
        if data.get(key):
            return data[key]
    if "id" in data:
        return f"https://app.clockify.me/shared/{data['id']}"
    raise RuntimeError(f"Unexpected Clockify response: {data}")


if __name__ == "__main__":
    # Smoke test: create a shared link for March 2026
    url = create_shared_report(
        start="2026-03-01T00:00:00.000Z",
        end="2026-03-31T23:59:59.000Z",
        name="Test - delete me",
    )
    print("Shared URL:", url)
