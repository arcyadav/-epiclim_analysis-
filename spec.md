# Project Spec: EpiClim — Climate-Health EDA & Modeling

> **Status:** Analysis concluded (2026-09-28). Data cleaning, EDA, hypothesis testing (H1–H5) and district × month outbreak models (any-disease + three transmission-route models) are complete; see `EDA_FINDINGS.md` for all results. Only the writeup/presentation remains. Possible future work: neighbouring-district outbreak features, district-level rainfall (IMD/CHIRPS), population normalization, confusion matrices and bootstrap CIs for the model metrics.
> **Course context:** Project 1 of 4 for this course
> **Last updated:** 2026-09-28

This is a living document. Update it as decisions get made — don't let it drift out of sync with the actual analysis. See the Changelog at the bottom for a history of major decisions.

---

## 1. Project Overview

**Type:** Data Science / Exploratory Data Analysis (EDA), with modeling to follow.

**Working title:** TBD — something like *"Climate Drivers of Vector-Borne and Waterborne Disease Outbreaks in India (2009–2022)"*

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
| **Time span** | May 2009 – June 2022 in the actual data (the Zenodo record describes it as 2009–2023; the last record is June 2022, so 2022 is a partial year) |
| **License** | Dual-licensed: CC-BY-4.0 / MIT |
| **DOI** | 10.5281/zenodo.14580510 (v1, published 2024-12-31) |
| **Zenodo record** | https://zenodo.org/records/14580510 |
| **Local copy** | `data/Final_data.csv` (downloaded, confirmed 8,985 rows + header, columns match spec) |
| **Derived files** | `data/Final_data_cleaned.csv`, `data/Final_data_imputed.csv`, plus a `dataset_profile.md` and ~13 EDA plot PNGs in `data/` — all regenerated from the raw file by `scripts/01`–`03` and the plotting scripts below (gitignored, not committed) |

### Pipeline scripts (`scripts/`)

| Script | Input → Output | What it does |
|---|---|---|
| `01_profile_dataset.py` | `Final_data.csv` → `dataset_profile.md` | Per-column dtype, missingness, range, unique values, and a one-line description of what each column represents |
| `02_clean_dataset.py` | `Final_data.csv` → `Final_data_cleaned.csv` | Drops `Unnamed: 0`; buckets `Disease` into the 7 main categories + "Other"; drops the 1 row with non-numeric `Cases` ("3/1") and casts to int; fills missing `Deaths` with 0; converts `Temp` Kelvin→Celsius; extracts `week_of_outbreak` to a plain integer |
| `03_impute_dataset.py` | `Final_data_cleaned.csv` → `Final_data_imputed.csv` | Imputes `Temp` via linear regression on `Latitude`+`Longitude` (R²≈0.17); imputes `LAI` via linear regression on `Latitude`+`Longitude`+`Temp` (R²≈0.20); fills `preci` with the median; adds `Temp_imputed`/`LAI_imputed`/`preci_imputed` boolean flags |
| `04`–`19` (EDA plots) | `Final_data_imputed.csv` → various PNGs in `data/` | Correlation heatmap, time trends, disease/geographic small multiples, seasonality heatmap, box plot, state/year totals, and precipitation-lag & disease-correlation analyses — **see `EDA_FINDINGS.md` for the full list, what each one shows, and the key findings** (some intermediate scripts were tried and removed after review; the doc reflects only what was kept) |
| `20_h1_precip_lag_test.py` | `Final_data_imputed.csv` → `h1_precip_lag_results.csv` | Hypothesis H1: Pearson + Spearman tests of precipitation (lag 0/1) vs. monthly outbreak count per disease, Holm-corrected — results in `EDA_FINDINGS.md` |
| `21_h2_seasonality_test.py` | `Final_data_imputed.csv` → `h2_seasonality_results.csv` | Hypothesis H2: chi-square goodness-of-fit of outbreak records by calendar month, per disease, Holm-corrected, with Cramér's V — results in `EDA_FINDINGS.md` |
| `22_h3_temp_by_disease_test.py` | `Final_data_imputed.csv` → `h3_temp_by_disease_summary.csv`, `h3_temp_by_disease_pairwise.csv` | Hypothesis H3: Shapiro-Wilk/Levene assumption checks, ANOVA vs. Kruskal-Wallis on measured `Temp` across diseases, pairwise Mann-Whitney post-hoc (Bonferroni) — results in `EDA_FINDINGS.md` |
| `23_h4_disease_region_test.py` | `Final_data_imputed.csv` → `h4_disease_region_observed.csv`, `h4_disease_region_residuals.csv` | Hypothesis H4: chi-square test of independence on disease × region (6 Zonal-Council regions), Cramér's V, adjusted standardized residuals — results in `EDA_FINDINGS.md` |
| `24_h5_monsoon_outbreak_test.py` | `Final_data_imputed.csv` → `h5_monsoon_outbreak_results.csv` | Hypothesis H5: Welch's t-test vs. Mann-Whitney U (one-sided) on monthly outbreak count, monsoon vs. other months, excluding 2020/2022 plus an all-months sensitivity run — results in `EDA_FINDINGS.md` |
| `25_build_district_month_grid.py` | `Final_data_imputed.csv` → `district_month_grid.csv` | Canonicalizes district names (795 → 764), builds the full district × month grid with a binary `outbreak` target, region-month climate features (lag 0/1) and past-only district-history features |
| `26_train_outbreak_model.py` | `district_month_grid.csv` → `outbreak_model_metrics.csv`, `outbreak_model_importance.csv`, `outbreak_model_results.png` | Tunes on 2018, refits on 2009–2018, scores 2019 and 2020–22: logistic regression and gradient boosting, each with and without climate features; permutation importance; PR-curve + importance plot |
| `28_train_route_models.py` | `district_month_grid.csv` + `Final_data_imputed.csv` → `route_model_metrics.csv`, `route_model_importance.csv`, `route_model_results.png` | Three transmission-route models (waterborne / *Aedes* / *Anopheles*), each gradient boosting with vs. without climate, same temporal split |

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
- [ ] Check district/state name consistency (spelling variants, renamed districts, new UTs formed during 2009–2022 — e.g., J&K/Ladakh split in 2019)
- [x] Check for duplicate week/district/disease rows — 0 fully duplicated rows found (whole-row duplicate check only; a targeted week+district+disease duplicate check is still open)
- [x] Temp is in Kelvin — convert to Celsius for interpretability — done in `02_clean_dataset.py`
- [ ] Understand how `week_of_outbreak` aligns with `day`/`mon`/`year` — `week_of_outbreak` and `mon` correlate at 0.90 (expected, one derives from the other), but full alignment not yet verified
- [x] Class imbalance across diseases / districts / states (some regions likely report far more than others) — confirmed via `dataset_profile.md`: heavily imbalanced (e.g. Maharashtra 1,195 records vs. Andaman & Nicobar 3; Acute Diarrhoeal Disease 5,126 vs. many single-digit disease labels)

---

## 3. Goals for This Project

- [x] Perform thorough EDA on the EpiClim dataset — see `EDA_FINDINGS.md`
- [x] Identify and test hypotheses about climate–disease relationships — H1–H5, see section 4 and `EDA_FINDINGS.md`
- [x] Build at least one predictive/explanatory model — district × month outbreak classifier, see section 6
- [ ] Communicate findings clearly (visualizations + writeup)

*(To be refined once course requirements/rubric are confirmed — e.g., is a specific deliverable format, page count, or presentation required?)*

---

## 4. Research Questions & Hypotheses

> **Status: EDA gives preliminary answers to most of these — see notes below and `EDA_FINDINGS.md`.** Still need to pick 2–4 to carry into modeling.

Some candidate directions to evaluate (not finalized):

- Does precipitation lag correlate with dengue/malaria case spikes (mosquito breeding lag effect)? — **Yes, modestly**: vector-borne diseases peak at a 1-month precipitation lag vs. lag-0 for waterborne ADD (`EDA_FINDINGS.md` #11).
- Does temperature range affect disease type differently (dengue vs. malaria vs. ADD)? — Not conclusively answered by a kept plot; an earlier binned-histogram attempt suggested a temperature "sweet spot" for some diseases but was removed after review, so this is still open.
- Is there a seasonal pattern per disease, and does it shift geographically (e.g., monsoon-driven spread from south to north)? — Seasonal timing per disease confirmed (seasonality heatmap, `EDA_FINDINGS.md` #6); geographic shift over the season not yet tested.
- Does Leaf Area Index (vegetation greenness) correlate with vector-borne disease incidence (proxy for mosquito habitat)? — **Weak/no support** found so far (`EDA_FINDINGS.md` #9 caveats, correlation heatmap).
- Have outbreak patterns shifted over the 15-year span (e.g., climate change signal, urbanization, policy interventions)? — Partially: reporting volume drops sharply in 2020/2022 (likely COVID/data-cutoff, not climate signal) — not yet disentangled.
- Which states/districts are consistent hotspots vs. sporadic outbreak sites? — **Answered**: district/state hotspot maps and totals (`EDA_FINDINGS.md` #4, #5, #8).
- Can climate variables predict an outbreak (case count above threshold) N weeks in advance? — Not yet tested; a modeling question, not an EDA one.

### Finalized hypotheses for testing

Five hypotheses chosen (2026-09-28), each targeting a different EDA finding.
Restricted to the course's test set: t-test, Mann-Whitney U, ANOVA,
Kruskal-Wallis, chi-square, Pearson, Spearman — together H1–H5 use all
seven. Prefer the non-parametric version where data is skewed (`Cases`,
monthly counts), and where both are run, compare them and say which is more
trustworthy. Report effect sizes alongside p-values — with ~9K rows nearly
everything will be "significant". Apply Holm/Bonferroni correction within any
hypothesis that runs multiple tests.

| # | Hypothesis | H₀ | Test | Notes |
|---|---|---|---|---|
| H1 | **Precipitation lag differs by transmission route** | No correlation between national mean precipitation at month *t − lag* and a disease's outbreak count at month *t* | Pearson + Spearman at lag 0 and lag 1, per disease; compare which lag is strongest | Expect Dengue/Chikungunya strongest at lag 1, ADD at lag 0 (`EDA_FINDINGS.md` #11). Monthly series are autocorrelated, so p-values are optimistic — note as a limitation |
| H2 | **Outbreaks are seasonal** | Each disease's outbreak records are uniformly distributed across the 12 months | Chi-square goodness-of-fit, per disease, Holm-corrected | Expect strong rejection for ADD/Dengue/Cholera/Malaria; AES (n=111) may not (`EDA_FINDINGS.md` #6, #10) |
| H3 | **Diseases occur under different temperature conditions** | Temp at outbreak time has the same distribution (mean) across diseases | One-way ANOVA and Kruskal-Wallis side by side; pairwise Mann-Whitney (Bonferroni) as post-hoc; η² / ε² effect size | Check ANOVA assumptions (Shapiro-Wilk, Levene). Use only `Temp_imputed == False` rows (imputation R²≈0.17); optionally repeat for `preci` |
| H4 | **Diseases have distinct geographic footprints** | Disease type is independent of region | Chi-square test of independence + Cramér's V | Map `state_ut` → ~5 regions (N/S/E/W/NE); merge/drop sparse diseases if expected counts < 5 (`EDA_FINDINGS.md` #4, #5) |
| H5 | **More outbreaks are reported in monsoon months** | Monthly outbreak count in monsoon months (Jun–Sep) is not higher than in non-monsoon months | Welch's t-test and Mann-Whitney U side by side (one-sided) | Unit = each year-month's total outbreak count. Counts are skewed, so Mann-Whitney is the more trustworthy of the two — contrast them in the writeup. Consider excluding 2020/2022 (reporting anomalies, `EDA_FINDINGS.md` #9) |

**Framing caveat:** the dataset contains only reported-outbreak records (no
zero/no-outbreak weeks), so H3/H4/H5 compare conditions *when outbreaks
occurred*, not whether conditions *cause* outbreaks.

---

## 5. Planned EDA Approach

- [x] Univariate analysis: distributions of cases, deaths, climate variables — box plot of Cases by disease
- [x] Temporal analysis: trends over years, seasonality within years, week-of-year patterns per disease — monthly time trends, seasonality heatmap, outbreak-count trends
- [x] Spatial analysis: choropleth/map of cases by state/district, hotspot identification — district lat/long hotspot maps, state totals bar chart
- [x] Bivariate/correlation analysis: climate variables vs. case counts (overall and per disease) — correlation heatmap, disease-to-disease correlation
- [x] Lag analysis: does climate at week *t* predict cases at week *t+k*? — done at monthly resolution (precipitation-lag correlation); weekly resolution tried and dropped as too noisy across 14 merged years
- [x] Disease comparison: how do dengue, malaria, and ADD differ in climate sensitivity? — per-disease small multiples for trends, hotspots, and seasonality

All of the above are detailed in `EDA_FINDINGS.md`, including which findings
turned out weak/negative (e.g. disease-to-disease correlation, vegetation/LAI
as a case-count driver).

---

## 6. Modeling Plan

> **Status: first model built and evaluated (2026-09-28)** — scripts `25`/`26`, results in `EDA_FINDINGS.md` ("Model" section).

**Why this framing:** forecasting national outbreak totals isn't viable (only
158 monthly points, data ends 2022-06, and 2020–22 are distorted by
COVID-era reporting). Instead the model asks whether climate and season can
predict *when and where* outbreaks happen.

**Decisions made:**
- **Task:** binary classification per district × month: did the district
  report *any* disease outbreak? (Per-disease models were considered and
  skipped.) The dataset has only outbreak records, so the grid's zeros are
  constructed, assuming a missing record means no outbreak.
- **Climate source:** region × month mean of this dataset's measured
  rainfall/temperature (lag 0 and 1), not external data. Cells without an
  outbreak have no climate value of their own, and per-district averages
  are too sparse (median district has 5 outbreak-months). External
  district-level rainfall (IMD gridded / CHIRPS) is noted as future work.
- **Features:** month, region, lat/long, past-only district history
  (previous month, same month last year, previous-12-month count,
  expanding outbreak rate), and the climate features.
- **Models:** logistic regression and gradient boosting
  (`HistGradientBoostingClassifier`), each with and without climate
  features. The no-climate versions are the baselines that isolate what
  climate adds.
- **Split (temporal):** train 2009-05–2017, validate 2018 (hyperparameters
  and threshold), test 2019 after refitting on 2009–2018, stress test
  2020–22 reported separately. Only districts with an outbreak in the
  training period are modeled.
- **Metrics:** PR-AUC (primary), ROC-AUC, Brier, and precision/recall/F1
  at the validation-chosen threshold. Not accuracy (~94% by always
  predicting "no").

**Result in one line:** about 3× better than random (test PR-AUC ≈ 0.196
vs. 0.061), driven by district history; climate features add essentially
nothing beyond month and history at region resolution.

**Transmission-route models** (`28_train_route_models.py`): since the
diseases respond to climate through different mechanisms, three models:
waterborne (ADD, Cholera, Acute Gastroenteritis), *Aedes* (Dengue,
Chikungunya) and *Anopheles* (Malaria); AES excluded. All beat random
(~3.3×, ~4.3×, ~11×). Climate gives no score gain for waterborne or
*Aedes*, but the waterborne model uses same-month rain and the *Aedes*
model last month's, reproducing H1. *Anopheles* has only 18 test positives,
too few to judge.

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
- [x] Deployment (viva requirement): static report site in `docs/`, served by GitHub Pages
- [x] Transcript HTML (viva requirement): `docs/transcript.html`, generated from `/export transcript.md` by `tools/transcript_to_html.py`
- [x] Viva prep page (viva requirement): `docs/viva_prep.html`
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
| 2026-09-19 | Pushed the repo to a private GitHub repository (`arcyadav/-epiclim_analysis-`). |
| 2026-09-19 | Ran a full EDA plotting pass (`scripts/05`–`19`): monthly time trends, per-disease trends, district/state geographic hotspot maps, a disease×month×climate seasonality heatmap, a Cases-by-disease box plot, monthly outbreak-count trends, a precipitation-lag correlation analysis, and a disease-to-disease correlation heatmap. Two exploratory approaches (a scatter+trend-line climate relationship chart, and a weekly seasonality-by-disease chart) were tried and deliberately removed after review — the first for being too overplotted/noisy, the second for being too noisy once 14 years of data were merged into a single 52-week axis. Full plot-by-plot writeup and findings are in the new `EDA_FINDINGS.md` rather than duplicated here. |
| 2026-09-19 | Key cross-cutting finding: **outbreak count (number of records) is a steadier signal than total Cases**, since Cases is dominated by a handful of extreme records (e.g. the 2009 Cholera outlier). Outbreak-count versions of the monthly trend and precipitation-lag charts were built alongside the Cases versions and show cleaner, stronger seasonal/lag patterns. |
| 2026-09-28 | Finalized 4 hypotheses for testing (section 4): precipitation lag by transmission route, per-disease seasonality, temperature by disease, and disease × region independence. Revised same day to use only the course's test set (t-test, Mann-Whitney, ANOVA, Kruskal-Wallis, chi-square, Pearson, Spearman): H1 switched from Steiger's test to Pearson/Spearman lag correlations, H3 post-hoc switched from Dunn's to pairwise Mann-Whitney and gained an ANOVA comparison, and added H5 (monsoon vs. non-monsoon outbreak count, t-test vs. Mann-Whitney). |
| 2026-09-28 | Tested H1 (`scripts/20_h1_precip_lag_test.py`): H0 rejected for all 5 diseases at both lags. Dengue/Chikungunya correlate most strongly with the previous month's rainfall (lag 1), ADD/Cholera with the current month's (lag 0), Malaria roughly tied. Pearson and Spearman agree. Full table in `EDA_FINDINGS.md`. |
| 2026-09-28 | Tested H2 (`scripts/21_h2_seasonality_test.py`): H0 rejected for all 8 diseases; every peak month falls in Jun–Sep, Chikungunya weakest (Cramér's V 0.10). Also confirmed the data ends 2022-06, so 2022 is an incomplete year. |
| 2026-09-28 | Tested H3 (`scripts/22_h3_temp_by_disease_test.py`): ANOVA assumptions fail (non-normal, unequal variances), but both ANOVA and Kruskal-Wallis reject H0. Effect is tiny (ε² ≈ 0.02); driven by Chikungunya (warmest) and AES (coolest), likely a geographic confound rather than a temperature preference. This also settles the open temperature question in section 4: only a weak effect. |
| 2026-09-28 | Tested H4 (`scripts/23_h4_disease_region_test.py`): states grouped into 6 Zonal-Council regions; H0 rejected, Cramér's V 0.18 (medium-to-large). Strongest footprints: Chikungunya → South, AES → Northeast, Malaria → Central/Northeast, Cholera → North. All 36 state names mapped cleanly (no spelling variants), partly closing the name-consistency open item. |
| 2026-09-28 | Tested H5 (`scripts/24_h5_monsoon_outbreak_test.py`): monsoon months average ~2.3× the outbreaks of other months; H0 rejected by both Welch's t-test and Mann-Whitney, with the largest effect of any hypothesis (Cohen's d 1.9, rank-biserial 0.81). All 5 hypotheses now tested. |
| 2026-09-28 | Built the district × month outbreak model (`scripts/25_build_district_month_grid.py`, `scripts/26_train_outbreak_model.py`); decisions recorded in section 6. Canonicalized district names (795 → 764). Test 2019 PR-AUC ≈ 0.196 vs. 0.061 random for both logistic regression and gradient boosting; climate features add ≤ 0.004 PR-AUC over the no-climate baselines. District history is the dominant signal. |
| 2026-09-28 | Added a Dengue-only model (`scripts/27_train_dengue_model.py`, gradient boosting). Test 2019 PR-AUC 0.169 vs. 0.034 random (~5×); no-climate baseline 0.183, so no measurable climate gain. Lag-1 rainfall is the top feature, consistent with H1, but substitutes for month. |
| 2026-09-28 | Added transmission-route models (`scripts/28_train_route_models.py`): waterborne, *Aedes*, *Anopheles*. Test 2019 PR-AUC 0.130 / 0.185 / 0.093 vs. random 0.040 / 0.043 / 0.008. No climate gain for waterborne or *Aedes*; feature importance splits by route (waterborne → same-month rain, *Aedes* → last month's), matching H1. *Anopheles* has only 18 test positives, so it's inconclusive. |
| 2026-09-28 | Dropped the Dengue-only model (`scripts/27_train_dengue_model.py` deleted): the *Aedes* model covers Dengue with twice the positives and matched its score. Kept the any-disease model (26) as a reference alongside the three route models. |
| 2026-09-28 | Housekeeping: corrected the time span to May 2009 – June 2022; fixed EDA #11, which had grouped Cholera with the vector-borne diseases (it's waterborne); `.gitignore` now ignores all derived `data/*.csv`/`*.png`/`*.md` except the raw dataset; added `requirements.txt` (pandas, numpy, matplotlib, scikit-learn, scipy). |
| 2026-10-26 | Viva requires every project to be deployed: added a static report website in `docs/` (`index.html` plus copies of all 15 plots in `docs/img/`) for GitHub Pages. Repo to be made public for Pages. |
| 2026-10-26 | Repo made public and GitHub Pages enabled: site live at https://arcyadav.github.io/-epiclim_analysis-/. Exported this session's transcript and converted it to `transcript.html` (Turn 1–34, responses collapsed) with `tools/transcript_to_html.py`; the 19 Sep sessions weren't saved, which a note on the page explains. |
| 2026-10-27 | Viva submission takes URLs only: moved `transcript.html` into `docs/` and added `docs/viva_prep.html` (study guide: project story, data decisions, theory of all 7 tests and both model types, results, limitations, 59 Q&As), both linked from the project page. |
