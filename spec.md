# Project Spec: EpiClim — Climate-Health EDA & Modeling

> **Status:** Draft / brainstorming phase — data cleaning & imputation pipeline in place
> **Course context:** Project 1 of 4 for this course
> **Last updated:** 2026-09-19

This is a living document. Update it as decisions get made — don't let it drift out of sync with the actual analysis. See the Changelog at the bottom for a history of major decisions.

---

## 1. Project Overview

**Type:** Data Science / Exploratory Data Analysis (EDA), with modeling to follow.

**Working title:** TBD — something like *"Climate Drivers of Vector-Borne and Waterborne Disease Outbreaks in India (2009–2023)"*

**One-line pitch:** Explore how weekly, district-level climate variables (precipitation, temperature, vegetation) relate to disease outbreak patterns (dengue, malaria, acute diarrheal disease) across India, and build a model that captures/predicts that relationship.

---

## 2. Dataset: EpiClim

| Field | Detail |
|---|---|
| **Name** | EpiClim — Weekly District-Wise All-India Multi-Epidemic Climate-Health Dataset |
| **Source** | Integrated Disease Surveillance Programme (IDSP), India |
| **Data file** | `Final_data.csv` (Zenodo record) |
| **Size** | ~8,985 records, ~1.0 MB |
| **Granularity** | District-level, weekly |
| **Time span** | 2009–2023 |
| **License** | Dual-licensed: CC-BY-4.0 / MIT |
| **DOI** | 10.5281/zenodo.14580510 (v1, published 2024-12-31) |
| **Zenodo record** | https://zenodo.org/records/14580510 |
| **Local copy** | `data/Final_data.csv` (downloaded, confirmed 8,985 rows + header, columns match spec) |
| **Derived files** | `data/Final_data_cleaned.csv`, `data/Final_data_imputed.csv`, `data/dataset_profile.md`, `data/correlation_heatmap.png` — all regenerated from the raw file by `scripts/01`–`04` (gitignored, not committed) |

### Pipeline scripts (`scripts/`)

| Script | Input → Output | What it does |
|---|---|---|
| `01_profile_dataset.py` | `Final_data.csv` → `dataset_profile.md` | Per-column dtype, missingness, range, unique values, and a one-line description of what each column represents |
| `02_clean_dataset.py` | `Final_data.csv` → `Final_data_cleaned.csv` | Drops `Unnamed: 0`; buckets `Disease` into the 7 main categories + "Other"; drops the 1 row with non-numeric `Cases` ("3/1") and casts to int; fills missing `Deaths` with 0; converts `Temp` Kelvin→Celsius; extracts `week_of_outbreak` to a plain integer |
| `03_impute_dataset.py` | `Final_data_cleaned.csv` → `Final_data_imputed.csv` | Imputes `Temp` via linear regression on `Latitude`+`Longitude` (R²≈0.17); imputes `LAI` via linear regression on `Latitude`+`Longitude`+`Temp` (R²≈0.20); fills `preci` with the median; adds `Temp_imputed`/`LAI_imputed`/`preci_imputed` boolean flags |
| `04_correlation_heatmap.py` | `Final_data_cleaned.csv` → `correlation_heatmap.png` | Pearson correlation heatmap across all numeric columns |

### Columns

| Column | Description |
|---|---|
| `week_of_outbreak` | Epidemiological week identifier |
| `state_ut` | State / Union Territory |
| `district` | District name |
| `Disease` | Disease type (dengue, malaria, acute diarrheal disease) |
| `Cases` | Number of reported cases |
| `Deaths` | Number of reported deaths |
| `day`, `mon`, `year` | Date components |
| `Latitude`, `Longitude` | District centroid coordinates |
| `preci` | Precipitation (mm) |
| `LAI` | Leaf Area Index (vegetation proxy) |
| `Temp` | Temperature (Kelvin) |

### Diseases covered
Raw data actually contains 22 distinct `Disease` labels, many near-duplicates
(e.g. `Dengue`, `Dengue Fever`, `Suspected Dengue`, `Dengue/Chikungunya` all
separate strings). Cleaning buckets these into 7 well-populated categories and
lumps the rest into `Other`:
- Acute Diarrhoeal Disease (5,126 records)
- Dengue (1,619)
- Chikungunya (731)
- Cholera (666)
- Malaria (544)
- Acute Encephalitis Syndrome (111)
- Acute Gastroenteritis (100)
- Other (88 — rare/suspected/combo labels)

### Known data considerations (to verify during EDA)
- [x] Raw CSV has an unnamed leading index column (artifact of source export) — drop on load
- [x] `Deaths` has missing values in raw data (seen in first rows) — confirm extent and handle
- [x] Check for missing values per column, especially climate variables (`preci`, `LAI`, `Temp`) — see `data/dataset_profile.md`. Missingness: `Deaths` 71.6%, `LAI` 24.4%, `Temp` 10.4%, `preci` 1.5%
- [ ] Check reporting completeness/consistency across years (surveillance quality may improve or change over time)
- [ ] Check district/state name consistency (spelling variants, renamed districts, new UTs formed during 2009–2023 — e.g., J&K/Ladakh split in 2019)
- [x] Check for duplicate week/district/disease rows — 0 fully duplicated rows found (whole-row duplicate check only; a targeted week+district+disease duplicate check is still open)
- [x] Temp is in Kelvin — convert to Celsius for interpretability — done in `02_clean_dataset.py`
- [ ] Understand how `week_of_outbreak` aligns with `day`/`mon`/`year` — `week_of_outbreak` and `mon` correlate at 0.90 (expected, one derives from the other), but full alignment not yet verified
- [x] Class imbalance across diseases / districts / states (some regions likely report far more than others) — confirmed via `dataset_profile.md`: heavily imbalanced (e.g. Maharashtra 1,195 records vs. Andaman & Nicobar 3; Acute Diarrhoeal Disease 5,126 vs. many single-digit disease labels)

---

## 3. Goals for This Project

- [ ] Perform thorough EDA on the EpiClim dataset
- [ ] Identify and test hypotheses about climate–disease relationships
- [ ] Build at least one predictive/explanatory model
- [ ] Communicate findings clearly (visualizations + writeup)

*(To be refined once course requirements/rubric are confirmed — e.g., is a specific deliverable format, page count, or presentation required?)*

---

## 4. Research Questions & Hypotheses

> **Status: TBD — brainstorming in progress.** This section will be filled in collaboratively.

Some candidate directions to evaluate (not finalized):

- Does precipitation lag correlate with dengue/malaria case spikes (mosquito breeding lag effect)?
- Does temperature range affect disease type differently (dengue vs. malaria vs. ADD)?
- Is there a seasonal pattern per disease, and does it shift geographically (e.g., monsoon-driven spread from south to north)?
- Does Leaf Area Index (vegetation greenness) correlate with vector-borne disease incidence (proxy for mosquito habitat)?
- Have outbreak patterns shifted over the 15-year span (e.g., climate change signal, urbanization, policy interventions)?
- Which states/districts are consistent hotspots vs. sporadic outbreak sites?
- Can climate variables predict an outbreak (case count above threshold) N weeks in advance?

**Action item:** Finalize 2–4 concrete, testable hypotheses before moving from EDA to modeling.

---

## 5. Planned EDA Approach

- [ ] Univariate analysis: distributions of cases, deaths, climate variables
- [ ] Temporal analysis: trends over years, seasonality within years, week-of-year patterns per disease
- [ ] Spatial analysis: choropleth/map of cases by state/district, hotspot identification
- [ ] Bivariate/correlation analysis: climate variables vs. case counts (overall and per disease)
- [ ] Lag analysis: does climate at week *t* predict cases at week *t+k*?
- [ ] Disease comparison: how do dengue, malaria, and ADD differ in climate sensitivity?

---

## 6. Modeling Plan

> **Status: TBD — to be decided after EDA and hypothesis finalization.**

Candidate approaches to consider:
- Regression (predict case counts from climate variables) — linear, or tree-based (Random Forest / XGBoost) for non-linear effects
- Time-series models (per district/disease) — e.g., ARIMA/Prophet, or lag-feature regression
- Classification (outbreak vs. no-outbreak, threshold-based)
- Spatial-temporal models if scope allows

**Decision needed:** prediction task framing (regression vs. classification), target variable definition, train/test split strategy (likely temporal split given time-series nature, not random split).

---

## 7. Tools & Tech Stack

- **Language:** Python (confirmed)
- **Core libraries used so far:** pandas, numpy, matplotlib, scikit-learn (`LinearRegression` for imputation)
- **Workflow:** plain `.py` scripts in `scripts/`, run from the command line (no notebook used yet — revisit if a notebook deliverable is required)
- **Version control:** git repo initialized locally; `scripts/` and raw `data/Final_data.csv` committed, derived data/plots gitignored for now

---

## 8. Deliverables

- [ ] EDA notebook/report
- [ ] Final model + evaluation
- [ ] Writeup / presentation
- *(Exact deliverable format depends on course requirements — TBD)*

---

## 9. Open Questions

- What exactly does the course require for this project (rubric, format, deadline)?
- Do we need to bring in external data (e.g., population by district for rate normalization, since raw case counts aren't comparable across districts of different sizes)?
- Is there a specific modeling technique the course wants us to demonstrate (since this is likely one of a sequence of 4 projects, each may target different skills)?

---

## 10. Changelog

| Date | Change |
|---|---|
| 2026-09-19 | Initial spec created. Dataset documented. Hypotheses and modeling approach left as TBD pending brainstorming session. |
| 2026-09-19 | Located and downloaded dataset from Zenodo (DOI 10.5281/zenodo.14580510) to `data/Final_data.csv`. Verified row/column counts match spec. Noted unnamed index column and missing `Deaths` values to handle during cleaning. |
| 2026-09-19 | Profiled the raw dataset column-by-column (dtype, missingness, range, unique values) — see `data/dataset_profile.md`. Found `Cases` stuck as text due to one `"3/1"` row, `Disease` has 22 near-duplicate labels, and `Deaths`/`LAI`/`Temp`/`preci` have 71.6%/24.4%/10.4%/1.5% missingness respectively. |
| 2026-09-19 | Cleaned the dataset (`scripts/02_clean_dataset.py` → `Final_data_cleaned.csv`): dropped `Unnamed: 0`; bucketed `Disease` into 7 categories + "Other"; dropped the 1 bad `Cases` row and cast to int; filled missing `Deaths` with 0; converted `Temp` Kelvin→Celsius; extracted `week_of_outbreak` to a plain integer. |
| 2026-09-19 | Plotted a Pearson correlation heatmap over all numeric columns (`scripts/04_correlation_heatmap.py` → `correlation_heatmap.png`) to inform imputation strategy. Strongest relationships: `Temp` vs. `LAI` (-0.44), `Temp` vs. `preci` (-0.39), `Temp` vs. `Longitude` (-0.37); `mon` vs. `week_of_outbreak` (0.90, expected redundancy). |
| 2026-09-19 | Imputed remaining missingness (`scripts/03_impute_dataset.py` → `Final_data_imputed.csv`): `Temp` via linear regression on `Latitude`+`Longitude` (R²≈0.17); `LAI` via linear regression on `Latitude`+`Longitude`+`Temp` (R²≈0.20); `preci` via median fill. Added `Temp_imputed`/`LAI_imputed`/`preci_imputed` flags so imputed rows can be identified later. Note: regression R² is modest, so these are directional imputations, not precise reconstructions. |
| 2026-09-19 | Initialized local git repo. Committed `scripts/` and raw `data/Final_data.csv`; derived CSVs, the profile, and the heatmap PNG are gitignored (regenerable from scripts) pending a dedicated results/plots folder. |
