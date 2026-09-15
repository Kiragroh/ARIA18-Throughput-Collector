"""Flat CSV RDL, sharing the exact guarded source query with the Excel collector."""
from pathlib import Path
import xml.etree.ElementTree as ET
import build_rdl as layout
from build_collector_v2 import build,NS,FIELDS,event_sql

META=["period_start","period_end","context_start","data_through","data_through_confirmed"]


def create():
    base=build()
    root=ET.parse(base).getroot()
    uri=NS["r"];tag=lambda n:"{"+uri+"}"+n
    sets=root.find("r:DataSets",NS)
    for ds in list(sets):
        if ds.get("Name")!="EventDetails":
            sets.remove(ds)
    ds=sets[0]
    sql=event_sql()
    before,select=sql.rsplit("\nSELECT N'2.0' AS contract_version",1)
    select="\nSELECT N'2.0' AS contract_version"+select
    select=select.replace("machine,event_start,event_end,fraction",
                          "machine,CONVERT(nvarchar(33),event_start,126) AS event_start,CONVERT(nvarchar(33),event_end,126) AS event_end,fraction")
    select=select.replace("is_brachy,activity_start,activity_end,\n completed,",
                          "is_brachy,CONVERT(nvarchar(33),activity_start,126) AS activity_start,CONVERT(nvarchar(33),activity_end,126) AS activity_end,\n CONVERT(nvarchar(33),completed,126) AS completed,")
    metadata=(",CONVERT(nvarchar(10),@PeriodStart,23) AS period_start,CONVERT(nvarchar(10),@PeriodEnd,23) AS period_end,"
              "CONVERT(nvarchar(10),@ContextStart,23) AS context_start,CONVERT(nvarchar(10),@DataThrough,23) AS data_through,"
              "@DataThroughConfirmed AS data_through_confirmed")
    select=select.replace("\nFROM grouped_events",metadata+"\nFROM grouped_events")
    # Keep the empty-result schema identical to the enabled detail export.
    before=before.replace(" WHERE 1=0;",","+",".join(f"CAST(NULL AS nvarchar(255)) AS [{f}]" for f in META)+" WHERE 1=0;")
    ds.find("r:Query/r:CommandText",NS).text=before+select
    qp=ds.find("r:Query/r:QueryParameters",NS)
    if not any(p.get("Name")=="@DataThroughConfirmed" for p in qp):
        p=ET.SubElement(qp,tag("QueryParameter"),Name="@DataThroughConfirmed")
        ET.SubElement(p,tag("Value")).text="=Parameters!DataThroughConfirmed.Value"
    fields=ds.find("r:Fields",NS)
    for name in META:
        field=ET.SubElement(fields,tag("Field"),Name=name)
        ET.SubElement(field,tag("DataField")).text=name
    body=root.find("r:ReportSections/r:ReportSection/r:Body/r:ReportItems",NS)
    body.clear()
    name="FlatEvents"
    layout.FIELDS={name:FIELDS+META};layout.PAGE_NAMES={name:"Events"};layout.CAPTIONS={name:"Lokaler CSV-Ereignisexport"}
    table,_=layout._tablix(name,0)
    wrapper=ET.fromstring('<root xmlns="'+uri+'">'+table+'</root>')
    table=wrapper[0];table.find("r:DataSetName",NS).text="EventDetails"
    for box in table.findall(".//r:Textbox",NS):
        box_name=box.get("Name")
        if "_D_" in box_name:
            index=int(box_name.rsplit("_",1)[1])
            ET.SubElement(box,tag("DataElementName")).text=(FIELDS+META)[index]
            ET.SubElement(box,tag("DataElementOutput")).text="Output"
        else:
            ET.SubElement(box,tag("DataElementOutput")).text="NoOutput"
    body.append(table)
    for page in root.findall(".//r:PageHeader",NS)+root.findall(".//r:PageFooter",NS):
        for box in page.findall(".//r:Textbox",NS):
            ET.SubElement(box,tag("DataElementOutput")).text="NoOutput"
    ET.register_namespace("",uri)
    ET.register_namespace("rd","http://schemas.microsoft.com/SQLServer/reporting/reportdesigner")
    ET.register_namespace("df","http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition/defaultfontfamily")
    target=base.with_name("ARIA18_Throughput_Collector_Fast_2.0.rdl")
    for prop in root.findall("r:CustomProperties/r:CustomProperty",NS):
        if prop.findtext("r:Name",namespaces=NS)=="ReportName":
            prop.find("r:Value",NS).text="ARIA18_Throughput_Collector_Fast_2.0"
    ET.ElementTree(root).write(target,encoding="utf-8",xml_declaration=True)
    return target


if __name__=="__main__":
    print(create())
