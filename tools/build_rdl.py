from __future__ import annotations

import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
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
    "Glossary": "11_glossary.sql",
    "SessionDetails": "09_session_details.sql",
    "AppointmentDetails": "10_appointment_details.sql",
}

FIELDS = {
    "Capabilities": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "source_name", "column_name", "is_available"],
    "MachineCatalog": ["machine_value", "machine_label", "neutral_machine_index", "delivered_sessions", "treated_patients", "active_device_days", "first_treatment_date", "last_treatment_date", "selected_by_default"],
    "SiteSummary": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "requested_period_start", "requested_period_end", "observed_first_treatment_date", "observed_last_treatment_date", "selected_machines", "active_machines", "delivered_sessions", "unique_patients", "active_calendar_days", "active_saturdays", "active_device_days", "gross_device_hours"],
    "MachineMonth": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "period_month", "machine", "delivered_sessions", "treated_patients", "active_device_days", "first_treatment_date", "last_treatment_date", "is_active", "active_machines_in_month"],
    "DeviceDay": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "service_date", "weekday_name", "machine", "delivered_sessions", "treated_patients", "first_fractions", "delivered_fields", "first_session", "last_session", "operating_span_minutes", "avg_actual_minutes", "median_actual_minutes", "p25_actual_minutes", "p75_actual_minutes", "p90_actual_minutes", "avg_cycle_minutes", "median_cycle_minutes", "p25_cycle_minutes", "p75_cycle_minutes", "p90_cycle_minutes", "gap_count_lt15", "gap_count_15_29", "gap_count_30_59", "gap_count_60_119", "gap_count_ge120", "gap_minutes_ge30", "max_gap_minutes", "gross_device_hours", "net_proxy_hours", "sessions_per_10_gross_hours", "sessions_per_10_net_proxy_hours", "first_fraction_share_pct", "adaptive_share_pct"],
    "SlotSummary": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "period_month", "machine", "activity_code", "activity_name", "mapping_source", "relevant_slots", "patients", "matched_slots", "match_coverage_pct", "avg_scheduled_minutes", "avg_actual_minutes", "avg_slot_utilization_pct", "utilization_status"],
    "CaseMix": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "dimension_name", "period_month", "machine", "group_code", "group_label", "delivered_sessions", "patients", "avg_actual_minutes"],
    "Imaging": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "period_month", "machine", "imaging_type", "image_count", "capability_status"],
    "DataQuality": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "raw_rows", "excluded_images", "excluded_brachy", "excluded_test_patients", "valid_sessions", "missing_machine", "missing_fraction"],
    "Glossary": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "field_name", "german_label", "definition", "unit", "source", "interpretation"],
    "SessionDetails": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "patient_key", "course_key", "plan_key", "session_key", "service_date", "machine", "fraction_number", "planned_fractions", "technique", "treatment_mode", "diagnosis_group", "session_start", "session_end", "actual_minutes", "first_imaging_timestamp", "first_beam_timestamp", "clinical_start_timestamp", "imaging_to_beam_minutes", "clinical_span_minutes", "image_record_count", "image_field_count", "imaging_after_beam_flag", "field_count"],
    "AppointmentDetails": ["MethodVersion", "RunId", "SiteLabel", "RecordType", "patient_key", "appointment_key", "matched_session_key", "service_date", "machine", "slot_start", "slot_end", "scheduled_minutes", "activity_start", "activity_end", "activity_minutes", "activity_code", "activity_name", "activity_category", "mapping_source", "patient_arrival_timestamp", "arrival_source", "appointment_status", "checked_in", "pending_or_in_progress_timestamp", "pending_or_in_progress_status", "completed_timestamp", "completed_status", "matched_first_imaging_timestamp", "matched_first_beam_timestamp", "matched_clinical_start_timestamp", "matched_session_start", "matched_session_end", "matched_actual_minutes", "matched_clinical_span_minutes", "imaging_after_beam_flag", "arrival_timing_quality", "arrival_to_clinical_start_minutes", "slot_to_clinical_start_minutes", "pending_to_clinical_start_minutes", "arrival_to_pending_minutes", "clinical_start_to_completed_minutes"],
}

PAGE_NAMES = {
    "Capabilities": "00_Coverage",
    "SiteSummary": "01_SiteSummary",
    "MachineMonth": "02_MachineMonth",
    "DeviceDay": "03_DeviceDay",
    "SlotSummary": "04_SlotSummary",
    "CaseMix": "05_CaseMix",
    "Imaging": "06_Imaging",
    "DataQuality": "07_DataQuality",
    "Glossary": "08_Glossary",
    "SessionDetails": "90_Sessions",
    "AppointmentDetails": "91_Appointments",
}

CAPTIONS = {
    "Capabilities": "Schemafaehigkeiten und Abdeckungsrahmen",
    "SiteSummary": "Standortzusammenfassung",
    "MachineMonth": "Monatliche Geraeteabdeckung und Durchsatz",
    "DeviceDay": "Geraetetage, Takt und Luecken",
    "SlotSummary": "Terminplanung und 1:1-Slot-Matching",
    "CaseMix": "Klinischer Mix",
    "Imaging": "Bildgebung",
    "DataQuality": "Datenqualitaet und Filterfunnel",
    "Glossary": "Glossar und Methodenbegriffe",
    "SessionDetails": "Kontrollierter pseudonymisierter Sitzungsexport",
    "AppointmentDetails": "Kontrollierter pseudonymisierter Terminexport",
}

REPORT_PARAMETERS = [
    "SiteLabel", "PeriodStart", "PeriodEnd", "Machines", "MachineList",
    "MinimumGroupPatients", "IncludePseudonymizedDetails", "MethodVersion",
    "RunId", "ExportSalt",
]


def _type_name(field: str) -> str:
    lower = field.lower()
    if lower.endswith("_date") or lower.endswith("_start") or lower.endswith("_end") or lower.endswith("_timestamp") or lower == "period_month":
        return "System.DateTime"
    if lower.startswith("is_") or lower.endswith("_count") or lower.endswith("_patients") or lower in {
        "delivered_sessions", "treated_patients", "active_device_days", "selected_machines",
        "active_machines", "unique_patients", "active_calendar_days", "active_saturdays",
        "first_fractions", "delivered_fields", "relevant_slots", "patients", "matched_slots",
        "image_count", "raw_rows", "excluded_images", "excluded_brachy",
        "excluded_test_patients", "valid_sessions", "missing_machine", "missing_fraction",
        "fraction_number", "planned_fractions", "field_count", "active_machines_in_month",
        "image_record_count", "image_field_count", "imaging_after_beam_flag",
    }:
        return "System.Int64"
    if any(token in lower for token in ("minutes", "hours", "pct", "share")):
        return "System.Decimal"
    return "System.String"


def _compose_sql(filename: str) -> str:
    sql = (ROOT / "sql/datasets" / filename).read_text(encoding="utf-8")
    session = (ROOT / "sql/fragments/session_base.sql").read_text(encoding="utf-8")
    resource = (ROOT / "sql/fragments/resource_base.sql").read_text(encoding="utf-8")
    return sql.replace("{{SESSION_BASE}}", session).replace("{{RESOURCE_BASE}}", resource)


def _query_parameters(sql: str) -> str:
    parts = []
    for name in REPORT_PARAMETERS:
        if f"@{name}" not in sql:
            continue
        value = f"=Parameters!{name}.Value"
        parts.append(
            f'          <QueryParameter Name="@{name}"><Value>{escape(value)}</Value></QueryParameter>'
        )
    return "\n".join(parts)


def _dataset_xml(name: str, filename: str) -> str:
    sql = _compose_sql(filename)
    fields = "\n".join(
        "\n".join(
            [
                f'        <Field Name="{field}">',
                f"          <DataField>{field}</DataField>",
                f"          <rd:TypeName>{_type_name(field)}</rd:TypeName>",
                "        </Field>",
            ]
        )
        for field in FIELDS[name]
    )
    params = _query_parameters(sql)
    qp = f"\n        <QueryParameters>\n{params}\n        </QueryParameters>" if params else ""
    return f'''    <DataSet Name="{name}">
      <Query>
        <DataSourceName>DataSource1</DataSourceName>{qp}
        <CommandText>{escape(sql)}</CommandText>
        <rd:UseGenericDesigner>true</rd:UseGenericDesigner>
      </Query>
      <Fields>
{fields}
      </Fields>
    </DataSet>'''


def _textbox(name: str, value: str, top: float, left: float, width: float, height: float, *, size: int = 9, bold: bool = False, color: str = "#10243E", background: str | None = None) -> str:
    background_xml = f"<BackgroundColor>{background}</BackgroundColor>" if background else ""
    return f'''          <Textbox Name="{name}">
            <CanGrow>true</CanGrow><KeepTogether>true</KeepTogether>
            <Paragraphs><Paragraph><TextRuns><TextRun><Value>{escape(value)}</Value><Style><FontFamily>Segoe UI</FontFamily><FontSize>{size}pt</FontSize><FontWeight>{'Bold' if bold else 'Normal'}</FontWeight><Color>{color}</Color></Style></TextRun></TextRuns><Style /></Paragraph></Paragraphs>
            <Top>{top:.2f}mm</Top><Left>{left:.2f}mm</Left><Height>{height:.2f}mm</Height><Width>{width:.2f}mm</Width>
            <Style><Border><Color>#C9D4E0</Color><Style>None</Style></Border>{background_xml}<PaddingLeft>2pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>2pt</PaddingTop><PaddingBottom>2pt</PaddingBottom></Style>
          </Textbox>'''


def _cell_textbox(name: str, value: str, header: bool = False) -> str:
    background = "#123A63" if header else "#FFFFFF"
    color = "#FFFFFF" if header else "#172A3A"
    weight = "Bold" if header else "Normal"
    return f'''<Textbox Name="{name}"><CanGrow>true</CanGrow><KeepTogether>true</KeepTogether><Paragraphs><Paragraph><TextRuns><TextRun><Value>{escape(value)}</Value><Style><FontFamily>Segoe UI</FontFamily><FontSize>{'6.5' if header else '6'}pt</FontSize><FontWeight>{weight}</FontWeight><Color>{color}</Color></Style></TextRun></TextRuns><Style /></Paragraph></Paragraphs><Style><Border><Color>#D7E0E8</Color><Style>Solid</Style></Border><BackgroundColor>{background}</BackgroundColor><PaddingLeft>2pt</PaddingLeft><PaddingRight>2pt</PaddingRight><PaddingTop>1pt</PaddingTop><PaddingBottom>1pt</PaddingBottom></Style></Textbox>'''


def _tablix(name: str, top: float) -> tuple[str, float]:
    fields = FIELDS[name]
    page_name = PAGE_NAMES[name]
    col_width = min(32.0, 396.0 / len(fields))
    width = col_width * len(fields)
    columns = "".join(f"<TablixColumn><Width>{col_width:.3f}mm</Width></TablixColumn>" for _ in fields)
    caption_cells = (
        f'<TablixCell><CellContents>{_cell_textbox(f"{name}_Caption", CAPTIONS[name], True)}'
        f'<ColSpan>{len(fields)}</ColSpan></CellContents></TablixCell>'
        + "".join("<TablixCell />" for _ in fields[1:])
    )
    header_cells = "".join(
        f"<TablixCell><CellContents>{_cell_textbox(f'{name}_H_{i}', field, True)}</CellContents></TablixCell>"
        for i, field in enumerate(fields)
    )
    detail_cells = "".join(
        f"<TablixCell><CellContents>{_cell_textbox(f'{name}_D_{i}', f'=Fields!{field}.Value')}</CellContents></TablixCell>"
        for i, field in enumerate(fields)
    )
    col_members = "".join("<TablixMember />" for _ in fields)
    hidden = ""
    if name in {"SessionDetails", "AppointmentDetails"}:
        hidden = "<Visibility><Hidden>=Not(Parameters!IncludePseudonymizedDetails.Value)</Hidden></Visibility>"
    if name in {"SessionDetails", "AppointmentDetails"}:
        year_group = f'''<TablixMember><Group Name="{name}_Year"><GroupExpressions><GroupExpression>=Year(Fields!service_date.Value)</GroupExpression></GroupExpressions><PageBreak><BreakLocation>Between</BreakLocation></PageBreak><PageName>="{page_name}_" &amp; Year(Fields!service_date.Value)</PageName></Group><TablixMembers><TablixMember><Group Name="{name}_Details" /></TablixMember></TablixMembers></TablixMember>'''
        row_members = f"<TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember><TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember>{year_group}"
        outer_page_name = ""
    else:
        row_members = f'<TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember><TablixMember><KeepWithGroup>After</KeepWithGroup><RepeatOnNewPage>true</RepeatOnNewPage></TablixMember><TablixMember><Group Name="{name}_Details" /></TablixMember>'
        outer_page_name = page_name
    height = 22.0
    page_name_xml = f"<PageName>{outer_page_name}</PageName>" if outer_page_name else ""
    xml = f'''          <Tablix Name="Tablix_{name}">
            <TablixBody><TablixColumns>{columns}</TablixColumns><TablixRows>
              <TablixRow><Height>8mm</Height><TablixCells>{caption_cells}</TablixCells></TablixRow>
              <TablixRow><Height>6mm</Height><TablixCells>{header_cells}</TablixCells></TablixRow>
              <TablixRow><Height>6mm</Height><TablixCells>{detail_cells}</TablixCells></TablixRow>
            </TablixRows></TablixBody>
            <TablixColumnHierarchy><TablixMembers>{col_members}</TablixMembers></TablixColumnHierarchy>
            <TablixRowHierarchy><TablixMembers>{row_members}</TablixMembers></TablixRowHierarchy>
            <DataSetName>{name}</DataSetName>
            <PageBreak><BreakLocation>Start</BreakLocation></PageBreak>{page_name_xml}
            <Top>{top:.2f}mm</Top><Left>2mm</Left><Height>{height:.2f}mm</Height><Width>{width:.2f}mm</Width>
            {hidden}<Style><Border><Style>None</Style></Border></Style>
          </Tablix>'''
    return xml, top + height + 18.0


def _parameters(method_version: str) -> tuple[str, str]:
    xml = [
        '''    <ReportParameter Name="SiteLabel"><DataType>String</DataType><DefaultValue><Values><Value>Standort</Value></Values></DefaultValue><Prompt>Standortbezeichnung</Prompt></ReportParameter>''',
        '''    <ReportParameter Name="PeriodStart"><DataType>DateTime</DataType><DefaultValue><Values><Value>=DateAdd("m", -12, DateSerial(Year(Today()), Month(Today()), 1))</Value></Values></DefaultValue><Prompt>Zeitraum von</Prompt></ReportParameter>''',
        '''    <ReportParameter Name="PeriodEnd"><DataType>DateTime</DataType><DefaultValue><Values><Value>=DateAdd("d", -1, DateSerial(Year(Today()), Month(Today()), 1))</Value></Values></DefaultValue><Prompt>Zeitraum bis</Prompt></ReportParameter>''',
        '''    <ReportParameter Name="Machines"><DataType>String</DataType><DefaultValue><DataSetReference><DataSetName>MachineCatalog</DataSetName><ValueField>machine_value</ValueField></DataSetReference></DefaultValue><Prompt>Therapiegeraete</Prompt><ValidValues><DataSetReference><DataSetName>MachineCatalog</DataSetName><ValueField>machine_value</ValueField><LabelField>machine_label</LabelField></DataSetReference></ValidValues><MultiValue>true</MultiValue></ReportParameter>''',
        '''    <ReportParameter Name="MachineList"><DataType>String</DataType><DefaultValue><Values><Value>=Join(Parameters!Machines.Value, "|")</Value></Values></DefaultValue><Hidden>true</Hidden></ReportParameter>''',
        '''    <ReportParameter Name="MinimumGroupPatients"><DataType>Integer</DataType><DefaultValue><Values><Value>5</Value></Values></DefaultValue><Prompt>Mindestzahl Patienten je Gruppe</Prompt></ReportParameter>''',
        '''    <ReportParameter Name="IncludePseudonymizedDetails"><DataType>Boolean</DataType><DefaultValue><Values><Value>true</Value></Values></DefaultValue><Prompt>Pseudonymisierte Detailblaetter exportieren</Prompt></ReportParameter>''',
        f'''    <ReportParameter Name="MethodVersion"><DataType>String</DataType><DefaultValue><Values><Value>{method_version}</Value></Values></DefaultValue><Hidden>true</Hidden></ReportParameter>''',
        '''    <ReportParameter Name="RunId"><DataType>String</DataType><DefaultValue><Values><Value>=System.Guid.NewGuid().ToString("N")</Value></Values></DefaultValue><Hidden>true</Hidden></ReportParameter>''',
        '''    <ReportParameter Name="ExportSalt"><DataType>String</DataType><DefaultValue><Values><Value>=System.Guid.NewGuid().ToString("N")</Value></Values></DefaultValue><Hidden>true</Hidden></ReportParameter>''',
    ]
    layout = []
    for index, name in enumerate(REPORT_PARAMETERS):
        layout.append(f"        <CellDefinition><ColumnIndex>{index % 4}</ColumnIndex><RowIndex>{index // 4}</RowIndex><ParameterName>{name}</ParameterName></CellDefinition>")
    return "\n".join(xml), "\n".join(layout)


def _report_items() -> tuple[str, float]:
    items = []
    top = 0.0
    items.append(_textbox("Title", "ARIA 18: Durchsatz- und Klinikvergleich", top, 2, 396, 13, size=20, bold=True, color="#FFFFFF", background="#123A63")); top += 16
    items.append(_textbox("Subtitle", '=Parameters!SiteLabel.Value & " | " & Format(Parameters!PeriodStart.Value, "dd.MM.yyyy") & " bis " & Format(Parameters!PeriodEnd.Value, "dd.MM.yyyy")', top, 2, 396, 9, size=11, bold=True)); top += 11
    method = "Der Bericht zaehlt applizierte externe Therapiesitzungen je Patient, Kurs, Plan, Geraet, Tag und Fraktion. Bildgebung und Brachytherapie werden separat ausgewiesen. Netto-Proxy bedeutet Brutto-Geraetefenster abzuglich aller Luecken ab 30 Minuten; es ist weder Beam-on-Zeit noch technische Verfuegbarkeit. Slotkennzahlen werden nur ab 50 Prozent 1:1-Matchquote als auswertbar markiert."
    items.append(_textbox("MethodNote", method, top, 2, 396, 22, size=9, background="#EAF1F7")); top += 26
    items.append(_textbox("PrivacyNote", "Pseudonymisierte Detailblaetter enthalten keine Namen, Geburtsdaten, Original-IDs, Freitexte oder DICOM-UIDs. Die Hashschluessel sind nur innerhalb dieser Ausfuehrung stabil. Der Export bleibt ein kontrollierter Forschungsdatensatz.", top, 2, 396, 18, size=9, color="#6E3B00", background="#FFF4DC")); top += 24
    for dataset in PAGE_NAMES:
        table, top = _tablix(dataset, top)
        items.append(table)
    return "\n".join(items), top


def build() -> Path:
    method = json.loads((ROOT / "method.json").read_text(encoding="utf-8"))
    template = (ROOT / "templates/ARIA18_Collector.template.rdl").read_text(encoding="utf-8")
    datasets = "\n".join(_dataset_xml(name, filename) for name, filename in DATASETS.items())
    report_items, body_height = _report_items()
    parameters, layout = _parameters(method["method_version"])
    header = _textbox("PageHeaderText", '=Parameters!SiteLabel.Value & " | " & Parameters!MethodVersion.Value', 0, 2, 330, 7, size=8, bold=True)
    footer = _textbox("PageFooterText", '="Run " & Parameters!RunId.Value & " | Seite " & Globals!PageNumber & " / " & Globals!TotalPages', 0, 2, 396, 7, size=7, color="#526575")
    replacements = {
        "{{DATASETS}}": datasets,
        "{{REPORT_ITEMS}}": report_items,
        "{{BODY_HEIGHT}}": f"{body_height:.2f}",
        "{{PAGE_HEADER}}": header,
        "{{PAGE_FOOTER}}": footer,
        "{{REPORT_PARAMETERS}}": parameters,
        "{{PARAMETER_LAYOUT}}": layout,
    }
    text = template
    for token, value in replacements.items():
        text = text.replace(token, value)
    unresolved = re.findall(r"\{\{[^}]+\}\}", text)
    if unresolved:
        raise ValueError(f"Unresolved template tokens: {unresolved}")
    ET.fromstring(text)
    output = ROOT / "dist/ARIA18_Durchsatz_Klinikvergleich_Collector.rdl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return output


if __name__ == "__main__":
    print(build())
