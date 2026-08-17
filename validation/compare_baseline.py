from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> int:
    legacy = load("expected_baseline.json")
    collector = load("current_collector_baseline.json")
    checks: list[tuple[str, bool]] = []

    checks.append(("identischer Beobachtungszeitraum", legacy["period_start"] == collector["period_start"] and legacy["period_end"] == collector["period_end"]))
    checks.append(("identische vier Geräte", legacy["machines"] == collector["machines"]))

    excluded = collector["legacy_excluded_device_days"]
    excluded_sessions = sum(int(row["sessions"]) for row in excluded)
    checks.append(("Sitzungsdifferenz vollständig durch drei alte Filtertage erklärt", collector["sessions"] - legacy["sessions"] == excluded_sessions == 8))
    checks.append(("Gerätetagdifferenz entspricht den drei Filtertagen", collector["active_device_days"] - legacy["active_device_days"] == len(excluded) == 3))
    checks.append(("Collector deckt mindestens den alten Zeitraum ab", collector["active_calendar_days"] >= legacy["active_calendar_days"]))
    checks.append(("Netto-Proxy bleibt innerhalb 0,1 Prozent", abs(collector["net_proxy_hours"] - legacy["net_proxy_hours"]) / legacy["net_proxy_hours"] < 0.001))

    failed = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(("PASS" if ok else "FAIL") + ": " + label)

    print(f"INFO: Alt={legacy['sessions']} Sitzungen, Collector={collector['sessions']} Sitzungen, Delta={collector['sessions'] - legacy['sessions']}")
    if failed:
        print("BASELINE_COMPARISON_FAILED: " + "; ".join(failed))
        return 1
    print("BASELINE_COMPARISON_OK: Methodenwechsel nachvollziehbar und vollständig erklärt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
