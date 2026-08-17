from __future__ import annotations

from datetime import date, timedelta
import json
import os
from pathlib import Path
import sys
from typing import Any

import pymssql


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation/local_smoke"
DATASETS = {
    "Capabilities": "00_capabilities.sql",
    "MachineCatalog": "01_machine_catalog.sql",
    "SiteSummary": "02_site_summary.sql",
    "MachineMonth": "03_machine_month.sql",
    "DeviceDay": "04_device_day.sql",
    "SlotSummary": "05_slot_summary.sql",
    "CaseMix": "06_case_mix.sql",
    "Imaging": "07_imaging.sql",
    "DataQuality": "08_data_quality.sql",
    "SessionDetails": "09_session_details.sql",
    "AppointmentDetails": "10_appointment_details.sql",
}
REQUIRED_ENV = ["ARIA_SQL_SERVER", "ARIA_SQL_DATABASE", "ARIA_SQL_USER", "ARIA_SQL_PASSWORD"]


def sql_string(value: str) -> str:
    return "N'" + value.replace("'", "''") + "'"


def compose(filename: str, values: dict[str, str]) -> str:
    sql = (ROOT / "sql/datasets" / filename).read_text(encoding="utf-8")
    session = (ROOT / "sql/fragments/session_base.sql").read_text(encoding="utf-8")
    resource = (ROOT / "sql/fragments/resource_base.sql").read_text(encoding="utf-8")
    sql = sql.replace("{{SESSION_BASE}}", session).replace("{{RESOURCE_BASE}}", resource)
    for name, value in sorted(values.items(), key=lambda item: -len(item[0])):
        sql = sql.replace(f"@{name}", value)
    if "{{" in sql:
        raise ValueError(f"Nicht aufgeloestes SQL-Token in {filename}")
    return sql


def execute_summary(cursor: Any, sql: str) -> dict[str, Any]:
    cursor.execute(sql)
    columns = [column[0] for column in (cursor.description or [])]
    rows = 0
    while True:
        batch = cursor.fetchmany(1000)
        if not batch:
            break
        rows += len(batch)
    return {"columns": columns, "row_count": rows}


def discover_machines(cursor: Any, common: dict[str, str]) -> list[str]:
    sql = compose(DATASETS["MachineCatalog"], common)
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    index = columns.index("machine_value")
    return [str(row[index]) for row in cursor.fetchall() if row[index]]


def main() -> int:
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        print("SQL_SMOKE_REFUSED: fehlende Umgebungsvariablen " + ", ".join(missing))
        return 2
    end_text = os.environ.get("ARIA_SMOKE_END")
    end = date.fromisoformat(end_text) if end_text else date.today().replace(day=1) - timedelta(days=1)
    start_text = os.environ.get("ARIA_SMOKE_START")
    start = date.fromisoformat(start_text) if start_text else end.replace(day=1)
    common = {
        "MethodVersion": sql_string("ARIA18-THROUGHPUT-1.0"),
        "RunId": sql_string("SQL-SMOKE"),
        "SiteLabel": sql_string(os.environ.get("ARIA_SMOKE_SITE", "Lokaler Smoke-Test")),
        "PeriodStart": sql_string(start.isoformat()),
        "PeriodEnd": sql_string(end.isoformat()),
        "MinimumGroupPatients": os.environ.get("ARIA_SMOKE_MIN_GROUP", "5"),
        "IncludePseudonymizedDetails": "0",
        "ExportSalt": sql_string("nicht-exportierter-smoke-salt"),
    }
    connection = pymssql.connect(
        server=os.environ["ARIA_SQL_SERVER"],
        database=os.environ["ARIA_SQL_DATABASE"],
        user=os.environ["ARIA_SQL_USER"],
        password=os.environ["ARIA_SQL_PASSWORD"],
        port=int(os.environ.get("ARIA_SQL_PORT", "1433")),
        login_timeout=15,
        timeout=int(os.environ.get("ARIA_SQL_TIMEOUT", "360")),
    )
    results: dict[str, Any] = {"period_start": start.isoformat(), "period_end": end.isoformat(), "datasets": {}}
    try:
        cursor = connection.cursor()
        configured = [item.strip() for item in os.environ.get("ARIA_SQL_MACHINES", "").split(",") if item.strip()]
        machines = configured or discover_machines(cursor, common)
        if not machines:
            raise RuntimeError("Keine Therapiegerate im Zeitraum gefunden")
        common["Machines"] = ", ".join(sql_string(machine) for machine in machines)
        common["MachineList"] = sql_string("|".join(machines))
        results["machine_count"] = len(machines)
        for dataset, filename in DATASETS.items():
            try:
                results["datasets"][dataset] = execute_summary(cursor, compose(filename, common))
            except Exception as exc:
                connection.rollback()
                results["datasets"][dataset] = {"error": f"{type(exc).__name__}: {exc}"}
        cursor.close()
    finally:
        connection.close()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / "sql_smoke_summary.json"
    target.write_text(json.dumps(results, indent=2, ensure_ascii=True), encoding="utf-8")
    failures = [name for name, result in results["datasets"].items() if "error" in result]
    if failures:
        print("SQL_SMOKE_FAILED: " + ", ".join(failures))
        return 1
    print(f"SQL_SMOKE_OK: {len(results['datasets'])} Datasets, {len(machines)} Geraete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
