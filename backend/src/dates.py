from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass(frozen=True)
class MonthRange:
    year: int
    month: int

    @property
    def human(self) -> str:
        """e.g. 'March 2026' — for invoice notes."""
        return date(self.year, self.month, 1).strftime("%B %Y")

    @property
    def iso_start(self) -> str:
        """Start of month, ISO-8601 UTC — for Clockify API."""
        return datetime(self.year, self.month, 1, tzinfo=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )

    @property
    def iso_end(self) -> str:
        """End of month, ISO-8601 UTC — for Clockify API."""
        last_day = monthrange(self.year, self.month)[1]
        return datetime(
            self.year, self.month, last_day, 23, 59, 59, tzinfo=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def last_month(today: date | None = None) -> MonthRange:
    """Return the month before `today` (defaults to today)."""
    today = today or date.today()
    if today.month == 1:
        return MonthRange(today.year - 1, 12)
    return MonthRange(today.year, today.month - 1)


if __name__ == "__main__":
    # Smoke test
    m = last_month()
    print(f"Human:     {m.human}")
    print(f"ISO start: {m.iso_start}")
    print(f"ISO end:   {m.iso_end}")

    # Edge case: January rolls back to December of previous year
    jan = last_month(date(2026, 1, 15))
    print(f"\nJanuary edge case → {jan.human}")
