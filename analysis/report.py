import json
from pathlib import Path
from plotly.offline import get_plotlyjs

ALLOWED = {"version","site","start","end","period_reason","data_through","periods",
           "flow","quality","notes","default_model","coverage"}


def render(data, target):
    if set(data)-ALLOWED:
        raise ValueError("Only aggregate report fields are permitted")
    serialized = json.dumps(data,ensure_ascii=True,allow_nan=False)
    for forbidden in ('"patient_key"', '"event_key"', '"plan_key"', '"course_key"', '"activity_name"'):
        if forbidden in serialized:
            raise ValueError("Non-aggregate field in report")
    template = Path(__file__).with_name("report.html").read_text(encoding="utf-8")
    serialized = serialized.replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026")
    html = template.replace("__PLOTLY__",get_plotlyjs()).replace("__REPORT_DATA__",serialized)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(html,encoding="utf-8")
    return target
