import pytest


@pytest.fixture
def connected_rows():
    """Add real R&V evidence outside the measured year to calendar test fixtures."""
    def add(rows):
        return list(rows) + [dict(source='delivery', event_key='prior-'+machine,
            patient_key='prior', machine=machine, plan_key='prior-plan', fraction=1,
            activity_code='', status='delivered', event_start='2024-12-01 08:00',
            event_end='2024-12-01 08:15') for machine in sorted({r['machine'] for r in rows})]
    return add
