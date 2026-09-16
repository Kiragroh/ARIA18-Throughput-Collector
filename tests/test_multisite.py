import copy
import hashlib
import json

import pytest


def site(index=1):
    from analysis.provenance import CALCULATION_SETTINGS
    from analysis.contracts import Profile
    profile = Profile()
    return dict(version="2.0.0-rc.6", site=f"Private clinic {index}",
        start="2025-01-01", end="2025-12-31", data_through="2026-04-01",
        provenance=dict(schema=1, export_sha256=hashlib.sha256(str(index).encode()).hexdigest(),
            run_sha256=hashlib.sha256(f"run-{index}".encode()).hexdigest(),
            analysis_sha256="a"*64, collector_release="2.0.0-rc.6", contract_version="2.0",
            context_start="2024-01-01", settings={k:getattr(profile,k) for k in CALCULATION_SETTINGS},
            fields=["source", "event_start", "event_end", "activity_start", "activity_end", "completed",
                    "plan_key", "fraction", "time_source", "patient_class", "resource_status",
                    "planned_fractions", "plan_first_treatment", "milestone_time", "activity_name"],
            capabilities=[dict(source="DWH.Fact", column="Time", required=True, available=True)],
            dependencies={"pandas":"2.2", "numpy":"2.0"}),
        quality=dict(profile_confirmed=True, source_coverage_confirmed=True),
        population=dict(summary=dict(patients=100, fractions=800, technical_fractions=780,
            manual_fractions=20, treated_plans=120, new_plans=90, treatment_days=200)),
        flow=dict(sources_complete=True, mature_episodes=100, unresolved_mature=20,
                  unresolved_pct=20, counselling_episodes=110, treatment_episodes=95),
        imaging=dict(available=True, groups=[]),
        periods={"year":{"activity":[dict(label="2025",start="2025-01-01",end="2025-12-31",partial=False,
            groups=[dict(machine="ALL", suppressed=False, pool_excludes_suppressed=False,
                kpi=dict(visits=600, expected_visits=610, relevant_slots=610, measurable_slots=590,
                    overlap_minutes_in_slots=7000, booked_minutes=10000, slot_coverage_pct=70,
                    measured_visits_pct=600/610*100, complete_device_days=195, incomplete_device_days=5,
                    free_hours=250, window_hours=1000, free_pct=25),
                distributions=dict(duration=dict(n=600,patients=100,suppressed=False,
                    low=4,q1=8,median=10,q3=13,high=20)))])]}})


def compare(sites, reviewed=None):
    from analysis.compare import build_comparison
    return build_comparison(sites, reviewed=set(sites) if reviewed is None else reviewed)


def test_six_sites_keep_values_denominators_and_no_pooled_median():
    result = compare({f"S{i}":site(i) for i in range(1,7)})
    assert len(result["sites"]) == 6
    assert len(result["checks"]) == 15
    assert all(c["domains"]["throughput"]["compatible"] for c in result["checks"])
    assert result["periods"][0]["kpi"]["booked_minutes"] == 10000
    assert result["periods"][0]["distributions"]["duration"]["median"] == 10
    text = json.dumps(result)
    assert "Private clinic" not in text
    assert "pooled_median" not in text


@pytest.mark.parametrize("change,reason", [
    (lambda d: d.update(start="2024-01-01"), "period_mismatch"),
    (lambda d: d["provenance"].update(analysis_sha256="b"*64), "analysis_mismatch"),
    (lambda d: d["provenance"]["settings"].update(visit_merge_minutes=10), "settings_mismatch"),
    (lambda d: d["provenance"]["capabilities"][0].update(available=False), "required_source_missing"),
    (lambda d: d["quality"].update(profile_confirmed=False), "profile_unconfirmed"),
])
def test_incompatible_inputs_are_not_silently_joined(change, reason):
    a,b = site(1),site(2)
    change(b)
    result = compare({"A":a,"B":b})
    check = result["checks"][0]["domains"]["throughput"]
    assert not check["compatible"] and reason in check["reasons"]
    assert len(result["periods"]) == 2


def test_same_analysis_does_not_hide_different_collector_semantics():
    a,b = site(1),site(2)
    b["provenance"]["collector_release"] = "2.0.0-rc.7"
    result = compare({"A":a,"B":b})
    for domain in result["checks"][0]["domains"].values():
        assert "collector_mismatch" in domain["reasons"]
        assert not domain["compatible"]


@pytest.mark.parametrize("release", [None, "", "unknown", "not-a-release"])
def test_unknown_collectors_are_not_accepted_even_when_identical(release):
    a,b = site(1),site(2)
    for data in [a,b]:
        data["provenance"]["collector_release"] = release
    check = compare({"A":a,"B":b})["checks"][0]["domains"]["throughput"]
    assert "collector_missing" in check["reasons"]
    assert not check["compatible"]


def test_known_old_resource_query_stays_descriptive_after_reanalysis():
    a,b = site(1),site(2)
    for data in [a,b]:
        data["provenance"]["collector_release"] = "2.0.0-rc.4"
    result = compare({"A":a,"B":b})
    assert "collector_resources_legacy" in result["checks"][0]["domains"]["throughput"]["reasons"]
    assert result["sites"][0]["population"]["patients"] == 100


def test_comparison_exposes_source_audit_and_actionable_notes_without_private_text(tmp_path):
    from analysis.compare import write_outputs
    a,b = site(1),site(2)
    a["provenance"]["collector_release"] = "2.0.0-rc.4"
    b["provenance"]["capabilities"] = []
    a["notes"] = ["PRIVATE-SOURCE-PATH"]
    result = compare({"A":a,"B":b})
    audit = result["sites"][0]
    assert audit["collector_release"] == "2.0.0-rc.4"
    assert audit["context_start"] == "2024-01-01"
    assert audit["capability_count"] == 1
    assert audit["available_capability_count"] == 1
    assert result["sites"][1]["capability_count"] == 0
    write_outputs(result,tmp_path)
    notes = (tmp_path/"Pruefhinweise.md").read_text(encoding="utf-8")
    assert "RDL" in notes and "Excel" in notes and "Quelleninventar" in notes
    assert "PRIVATE-SOURCE-PATH" not in notes
    assert "2.0.0-rc.4" in notes and "2.0.0-rc.6" in notes
    assert "profile_unconfirmed" not in notes


def test_missing_intervals_keep_free_time_explicitly_limited_to_complete_days():
    result = compare({"A":site(1),"B":site(2)})
    period = result["periods"][0]
    assert "incomplete_device_days" in period["reasons"]
    assert period["kpi"]["free_hours"] == 250
    assert period["kpi"]["complete_device_days"] == 195
    assert period["kpi"]["incomplete_device_days"] == 5
    assert any(item["reason"] == "incomplete_device_days" for item in result["review_actions"])
    a,b = site(1),site(2)
    for data in [a,b]:
        data["periods"]["year"]["activity"][0]["groups"][0]["kpi"]["incomplete_device_days"] = 0
    assert all("incomplete_device_days" not in p["reasons"] for p in compare({"A":a,"B":b})["periods"])


def test_flow_followup_and_imaging_source_have_separate_gates():
    a,b = site(1),site(2)
    b["data_through"] = "2026-06-01"
    b["imaging"]["available"] = False
    result = compare({"A":a,"B":b})["checks"][0]["domains"]
    assert result["throughput"]["compatible"]
    assert "followup_mismatch" in result["flow"]["reasons"]
    assert "imaging_unavailable" in result["imaging"]["reasons"]


def test_legacy_and_unreviewed_inputs_remain_descriptive():
    old = site(2)
    old.pop("provenance")
    result = compare({"A":site(1),"B":old}, reviewed=set())
    reasons = result["checks"][0]["domains"]["throughput"]["reasons"]
    assert "provenance_missing" in reasons and "local_review_missing" in reasons
    assert result["sites"][1]["population"]["patients"] == 100


def test_duplicates_and_alias_collisions_are_rejected():
    with pytest.raises(ValueError, match="Duplicate"):
        compare({"A":site(),"B":site()})
    with pytest.raises(ValueError, match="alias"):
        compare({"A":site(1),"a":site(2)})


def test_suppression_and_missing_values_are_not_zero_or_reconstructed():
    a,b = site(1),site(2)
    a["periods"]["year"]["activity"][0]["groups"][0]["suppressed"] = True
    b["population"]["summary"]["patients"] = None
    result = compare({"A":a,"B":b})
    assert all(v is None for v in result["periods"][0]["kpi"].values())
    assert result["periods"][0]["distributions"] == {}
    assert result["sites"][1]["population"]["patients"] is None


def test_no_forwarding_unknown_fields_notes_or_nonaggregate_identifiers(tmp_path):
    from analysis.compare import write_outputs
    a = site(1)
    a["notes"] = ["PRIVATE-SOURCE-TEXT"]
    a["population"]["summary"]["secret"] = "PRIVATE-SOURCE-TEXT"
    result = compare({"A":a,"B":site(2)})
    write_outputs(result,tmp_path)
    assert "PRIVATE-SOURCE-TEXT" not in (tmp_path/"Standortvergleich.html").read_text(encoding="utf-8")
    a["flow"]["patient_key"] = "not-allowed"
    with pytest.raises(ValueError, match="aggregate"):
        compare({"A":a,"B":site(2)})


def test_invalid_numeric_and_nan_values_are_rejected():
    a = site(1)
    a["population"]["summary"]["patients"] = "=HYPERLINK('bad')"
    with pytest.raises(ValueError, match="numeric"):
        compare({"A":a,"B":site(2)})
    a["population"]["summary"]["patients"] = float("nan")
    with pytest.raises(ValueError, match="numeric"):
        compare({"A":a,"B":site(2)})


def test_provenance_contains_no_profile_labels_or_patient_data(tmp_path):
    from analysis.provenance import create_provenance
    from analysis.contracts import Profile
    path=tmp_path/"private-name.xlsx"
    path.write_bytes(b"private clinical input")
    profile=Profile(site="PRIVATE",machines={"local-machine":"PRIVATE"},activity_names={"PRIVATE":"ignore"})
    data=create_provenance(path,dict(run_id="SECRET-RUN",contract_version="2.0",context_start="2024-01-01"),
                           profile,["event_start"],[])
    assert data["export_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert data["settings"]["visit_merge_minutes"] == 5
    text=json.dumps(data)
    assert not any(s in text for s in ("PRIVATE","SECRET-RUN","private-name","local-machine"))


def test_partial_observation_is_not_a_complete_year_even_after_local_review():
    a,b=site(1),site(2)
    b['data_through']='2025-03-31'
    reasons=compare({'A':a,'B':b})['checks'][0]['domains']['throughput']['reasons']
    assert 'observation_incomplete' in reasons


def test_missing_context_is_not_accepted_for_patient_flow():
    a,b=site(1),site(2)
    a['provenance'].pop('context_start')
    b['provenance'].pop('context_start')
    assert 'context_missing' in compare({'A':a,'B':b})['checks'][0]['domains']['flow']['reasons']


def test_synthetic_and_clinical_inputs_cannot_be_mixed_as_comparable():
    a,b=site(1),site(2)
    a['synthetic']=True
    assert 'synthetic_mixed' in compare({'A':a,'B':b})['checks'][0]['domains']['throughput']['reasons']


def test_schema_inventory_is_allowed_but_nested_record_fields_are_rejected():
    from analysis.contracts import assert_aggregate_payload
    assert_aggregate_payload({'provenance':{'fields':['patient_key','plan_key']}})
    with pytest.raises(ValueError,match='aggregate'):
        assert_aggregate_payload({'flow':{'PatientID':'PRIVATE'}})


def test_cli_rejects_repeated_alias_before_writing_output(tmp_path):
    from analysis.compare import main
    path=tmp_path/'input.json'
    path.write_text(json.dumps(site()),encoding='utf-8')
    with pytest.raises(ValueError,match='alias'):
        main(['--site',f'A={path}','--site',f'A={path}','--output',str(tmp_path/'result')])
    assert not (tmp_path/'result').exists()


def test_new_duration_denominators_use_the_same_slot_subset():
    import pandas as pd
    from analysis.contracts import Profile
    from analysis.throughput import prepare_visits,aggregate
    rows=[]
    for i in range(6):
        start=pd.Timestamp('2025-01-02 08:00')+pd.Timedelta(minutes=20*i)
        rows.append(dict(source='appointment',event_key=str(i),patient_key=str(i),machine='M',
            activity_code='TX',status='completed',event_start=start,event_end=start+pd.Timedelta(minutes=20),
            activity_start=start+pd.Timedelta(minutes=5),activity_end=start+pd.Timedelta(minutes=15)))
    profile=Profile(machines={'M':'Machine'},activity_codes={'TX':'treatment_external'})
    pool=aggregate(prepare_visits(pd.DataFrame(rows),profile),profile)['year']['activity'][0]['groups'][-1]['kpi']
    assert pool['expected_visits']==6
    assert pool['booked_minutes']==120 and pool['overlap_minutes_in_slots']==60
    assert pool['duration_minutes_in_slots']==60 and pool['slot_coverage_pct']==50
