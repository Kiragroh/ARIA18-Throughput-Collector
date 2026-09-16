# Multisite Comparison Implementation Plan

**Goal:** Implement the already agreed aggregate-only comparison for four to six
sites, with auditable denominators and explicit compatibility checks.
**Architecture:** Keep the released rc.4 RDL unchanged. Extend local aggregate
metadata, consume only aggregate JSON files, and render an offline comparison
without pooling patients or averaging site medians.
**Stack:** Existing Python, pandas and offline Plotly; no new dependencies.

## 1. Regression contract
- [x] Add tests/test_multisite.py: six synthetic sites; changed year, method,
  settings, coverage and follow-up; legacy aggregates; duplicate submissions;
  unknown versus zero; suppressed groups; input privacy; output escaping.
- [x] Run `python -m pytest tests/test_multisite.py -q` and verify missing code fails.

## 2. Reproducibility and exact denominators
- [x] Add analysis/provenance.py: source and run fingerprints, analysis-source
  digest, dependency versions, non-identifying calculation settings, available
  fields/capabilities, collector contract and context dates.
- [x] Wire provenance into analysis/cli.py and report allowlist. Add exact booked
  and overlap minutes plus expected visits to throughput aggregates under the
  existing suppression rules. Do not infer provenance for old outputs.

## 3. Comparison engine and offline view
- [x] Add analysis/compare.py with `--site ALIAS=aggregate.json` (repeatable),
  explicit local `--reviewed ALIAS` flags and `--output`. Reject duplicate inputs.
- [x] Compare period, calculation contract, source fields/capabilities and local
  validation separately for throughput, population, flow and imaging. Different
  follow-up dates additionally prevent a joint flow interpretation.
- [x] Export Standorte.csv, Vergleich.json and Standortvergleich.html. Select
  fields explicitly; never forward source notes, original labels or identifiers.
- [x] Show per-site values, denominator/missingness tables, timing-model and
  period controls, grouped distributions, paired check reasons. No combined
  median, inferential statistics, rank or automatic local clinical approval.

## 4. Short validation and documentation
- [x] Run focused tests then the complete local suite (no new SSRS year runs).
- [x] Generate a six-site synthetic report; verify desktop/mobile, light/dark,
  model/period changes, chart expansion and absence of page errors.
- [x] Run the comparison on existing local aggregates to verify unproven inputs
  remain unproven; do not publish these outputs.
- [x] Document invocation and remaining clinical acceptance.
- [ ] Commit and push the scoped analysis branch. Do not replace the released
  Hamburg test ZIP.

## Verification (2026-09-16)

- Package regression demonstrated missing demo/docs before manifest extension:
  two failures, then 23 focused package/comparison tests passed in 38.69 seconds.
- Complete suite: 126 passed in 47.51 seconds.
- Offline browser: six synthetic sites, 15 pairs; all four domains, three timing
  models, month/quarter controls, expansion, desktop/mobile and light/dark.
- Existing two-site annual aggregates also passed the offline browser checks.
  Missing provenance, unconfirmed source coverage and differing follow-up remain
  explicitly descriptive. No clinical values or outputs added to this repository.
- No live SQL run and no RDL modification. Released rc.5 assets unchanged.
