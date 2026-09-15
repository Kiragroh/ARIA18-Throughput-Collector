"""Read-only schema preflight for optional acquisition-side imaging adapters."""
from pathlib import Path
import xml.etree.ElementTree as ET
import build_rdl as layout
from build_collector_v2 import build, NS


def create():
    base=build()
    root=ET.parse(base).getroot()
    uri=NS["r"]
    tag=lambda name:"{"+uri+"}"+name
    root.find("r:DataSources/r:DataSource/r:DataSourceReference",NS).text="/VarianTemplate/Data Sources/VARIAN"
    for prop in root.findall("r:CustomProperties/r:CustomProperty",NS):
        if prop.findtext("r:Name",namespaces=NS)=="ReportName":
            prop.find("r:Value",NS).text="ARIA18_Imaging_Preflight_2.0"
    queries={
        "ImageSchema":("""SELECT s.name AS schema_name,t.name AS table_name,c.name AS column_name,ty.name AS data_type
FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
JOIN sys.columns c ON c.object_id=t.object_id JOIN sys.types ty ON ty.user_type_id=c.user_type_id
WHERE t.name IN ('Image','ImageSlice','Slice','SliceRT','Series','Study','Radiation','Resource','RTPlan','Patient')
OR t.name LIKE '%DICOM%' ORDER BY t.name,c.column_id""",["schema_name","table_name","column_name","data_type"]),
        "ImageRelations":("""SELECT OBJECT_NAME(f.parent_object_id) AS source_table,COL_NAME(f.parent_object_id,f.parent_column_id) AS source_column,
OBJECT_NAME(f.referenced_object_id) AS target_table,COL_NAME(f.referenced_object_id,f.referenced_column_id) AS target_column
FROM sys.foreign_key_columns f
WHERE OBJECT_NAME(f.parent_object_id) IN ('Image','ImageSlice','Slice','SliceRT','Series','Study','Radiation','RTPlan')
ORDER BY source_table,source_column""",["source_table","source_column","target_table","target_column"])
    }
    sets=root.find("r:DataSets",NS);sets.clear()
    items=root.find("r:ReportSections/r:ReportSection/r:Body/r:ReportItems",NS);items.clear()
    layout.FIELDS={name:fields for name,(_,fields) in queries.items()}
    layout.PAGE_NAMES={name:name for name in queries}
    layout.CAPTIONS={name:name for name in queries}
    top=0
    for name,(sql,fields) in queries.items():
        ds=ET.SubElement(sets,tag("DataSet"),Name=name);query=ET.SubElement(ds,tag("Query"))
        ET.SubElement(query,tag("DataSourceName")).text="DataSource1"
        ET.SubElement(query,tag("CommandText")).text=sql
        ET.SubElement(query,tag("Timeout")).text="60"
        fs=ET.SubElement(ds,tag("Fields"))
        for field in fields:
            node=ET.SubElement(fs,tag("Field"),Name=field)
            ET.SubElement(node,tag("DataField")).text=field
        table,top=layout._tablix(name,top)
        wrapper=ET.fromstring('<root xmlns="'+uri+'">'+table+'</root>')
        items.append(wrapper[0])
    target=base.with_name("ARIA18_Imaging_Preflight_2.0.rdl")
    ET.register_namespace("",uri)
    ET.register_namespace("rd","http://schemas.microsoft.com/SQLServer/reporting/reportdesigner")
    ET.register_namespace("df","http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition/defaultfontfamily")
    ET.ElementTree(root).write(target,encoding="utf-8",xml_declaration=True)
    return target


if __name__=="__main__":
    print(create())
