"""Create a layout-only diagnostic definition; does not execute or publish reports."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

NS = {"r": "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"}


def monthly_copy(source, target):
    tree = ET.parse(source)
    original_queries = [q.text for q in tree.findall(".//r:CommandText", NS)]
    group = next(g for g in tree.findall(".//r:Group", NS) if g.get("Name") in {"EventDetails_Year", "EventDetails_Month"})
    group.set("Name", "EventDetails_Month")
    group.find("r:GroupExpressions/r:GroupExpression", NS).text = '=Format(Fields!event_start.Value, "yyyy_MM")'
    group.find("r:PageName", NS).text = '="90_Events_" & Format(Fields!event_start.Value, "yyyy_MM")'
    assert original_queries == [q.text for q in tree.findall(".//r:CommandText", NS)]
    ET.register_namespace("", NS["r"])
    ET.register_namespace("rd", "http://schemas.microsoft.com/SQLServer/reporting/reportdesigner")
    ET.register_namespace("df", "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition/defaultfontfamily")
    target.parent.mkdir(parents=True, exist_ok=True)
    tree.write(target, encoding="utf-8", xml_declaration=True)
    print("MONTH_PARTITION_ONLY_SQL_UNCHANGED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    monthly_copy(args.source, args.target)
