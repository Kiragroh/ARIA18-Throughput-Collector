from dataclasses import dataclass, field, asdict
from datetime import date
import json
from pathlib import Path

KINDS = {"counselling", "observation", "treatment_external", "treatment_brachy",
         "treatment_legacy", "treatment_xray", "block", "ignore"}


@dataclass
class Profile:
    start: str = "2025-01-01"
    end: str = "2025-12-31"
    period_reason: str = ""
    site: str = "Standort"
    model: str = "activity"
    minimum_patients: int = 5
    confirmed: bool = False
    sources_complete: bool = False
    complete_through: str = ""
    timezone: str = "Europe/Berlin"
    activity_codes: dict = field(default_factory=dict)
    activity_names: dict = field(default_factory=dict)
    status_codes: dict = field(default_factory=dict)
    machines: dict = field(default_factory=dict)
    manual_machine_labels: dict = field(default_factory=lambda: {
        "treatment_legacy": "Historische Therapie", "treatment_brachy": "Brachytherapie",
        "treatment_xray": "Roentgentherapie"})
    require_numeric_patient_id: bool = False
    equipment_periods: list = field(default_factory=list)
    max_interval_minutes: int = 240
    imaging_before_beam_minutes: int = 120
    visit_merge_minutes: int = 5
    opening_hours: dict = field(default_factory=dict)
    opening_hours_confirmed: bool = False

    def __post_init__(self):
        start, end = date.fromisoformat(self.start), date.fromisoformat(self.end)
        if start > end:
            raise ValueError("start must precede end")
        if self.complete_through:
            checked = date.fromisoformat(self.complete_through)
            if checked >= date.today():
                raise ValueError("complete_through must be a complete past date")
        if self.model not in {"activity", "workflow", "technical"}:
            raise ValueError("Invalid time model")
        if self.minimum_patients < 5:
            raise ValueError("minimum_patients must be >=5 for shareable output")
        if not (0 <= self.visit_merge_minutes <= 30 and 1 <= self.max_interval_minutes <= 480):
            raise ValueError("Invalid interval limits")
        if not 0 <= self.imaging_before_beam_minutes <= 240:
            raise ValueError("Invalid imaging window")
        if any(kind not in KINDS for kind in [*self.activity_codes.values(), *self.activity_names.values()]):
            raise ValueError("Unknown activity classification")
        if any(value not in {'completed','cancelled','open','deleted','other'} for value in self.status_codes.values()):
            raise ValueError('Unknown status classification')
        if len(set(self.machines.values())) != len(self.machines):
            raise ValueError("Machine labels must be unique")
        if any(len(str(label)) > 80 for label in self.machines.values()):
            raise ValueError("Machine labels too long")
        for hours in self.opening_hours.values():
            if not 0 < float(hours) <= 24:
                raise ValueError("opening_hours must be hours per active device-day (0,24]")
        eras = {}
        for item in self.equipment_periods:
            if item.get("machine") not in self.machines:
                raise ValueError("Equipment needs a configured machine")
            a, b = date.fromisoformat(item["start"]), date.fromisoformat(item["end"])
            if a > b or any(not (b < x or a > y) for x,y in eras.get(item["machine"],[])):
                raise ValueError("Equipment periods overlap or are reversed")
            eras.setdefault(item["machine"],[]).append((a,b))
            if item.get("cbct_modality","unknown") not in {"kv","mv","unknown"}:
                raise ValueError("Unknown CBCT modality")
            if not isinstance(item.get("confirmed",False), bool):
                raise ValueError("Equipment confirmation must be boolean")

    def as_dict(self):
        return asdict(self)

    def classify_status(self,value):
        from .metrics import status_group
        return self.status_codes.get(str(value),status_group(value))

    def classify_activities(self, frame):
        kinds = frame.activity_code.map(self.activity_codes)
        if "activity_name" in frame:
            kinds = frame.activity_name.map(self.activity_names).combine_first(kinds)
        return kinds.fillna("unknown")


def load_profile(path: Path) -> Profile:
    return Profile(**json.loads(path.read_text(encoding="utf-8")))
