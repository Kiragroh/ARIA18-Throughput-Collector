"""Reproducibility metadata, without paths, original labels or record identifiers."""
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import pandas as pd

CALCULATION_SETTINGS = ('minimum_patients','timezone','require_numeric_patient_id',
    'max_interval_minutes','imaging_before_beam_minutes','visit_merge_minutes')


def file_digest(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def analysis_digest():
    digest = hashlib.sha256()
    for source in sorted(Path(__file__).parent.glob('*.py')):
        if source.name in {'compare.py','report.py','provenance.py'}:
            continue
        digest.update(source.name.encode('utf-8'))
        digest.update(source.read_text(encoding='utf-8').replace('\r\n','\n').encode('utf-8'))
    return digest.hexdigest()


def create_provenance(path, metadata, profile, fields, coverage):
    def flag(value):
        return str(value).lower() in {'true','1','1.0'}
    def date(value):
        return str(pd.Timestamp(value).date()) if value else None
    profile_json = json.dumps(profile.as_dict(),sort_keys=True,ensure_ascii=True)
    return dict(schema=1,export_sha256=file_digest(path),synthetic=metadata.get('run_id')=='SYNTHETIC',
        run_sha256=hashlib.sha256(str(metadata['run_id']).encode('utf-8')).hexdigest()
            if metadata.get('run_id') else None,
        profile_sha256=hashlib.sha256(profile_json.encode('utf-8')).hexdigest(),
        analysis_sha256=analysis_digest(),collector_release=str(metadata.get('collector_release','unknown')),
        contract_version=str(metadata.get('contract_version','unknown')),
        context_start=date(metadata.get('context_start')),
        settings={name:getattr(profile,name) for name in CALCULATION_SETTINGS},
        fields=sorted(set(fields)),
        capabilities=sorted([dict(source=str(c.get('source_name','')),
            column=str(c.get('column_name','')),required=flag(c.get('is_required')),
            available=flag(c.get('available'))) for c in coverage],key=lambda c:(c['source'],c['column'])),
        dependencies={name:version(name) for name in ('pandas','numpy','openpyxl')},
        activity_kinds=sorted(set(profile.activity_codes.values()) | set(profile.activity_names.values())),
        comparison_population_complete=flag(metadata.get('comparison_population_complete')))
