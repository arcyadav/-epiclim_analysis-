# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

EpiClim: an exploratory data analysis (EDA) project on a weekly, district-level
Indian disease-surveillance dataset (dengue, malaria, cholera, etc.) joined
with climate variables (precipitation, temperature, vegetation/LAI),
May 2009 – June 2022 (2022 is a partial year).
This is a course project (project 1 of 4); EDA, hypothesis tests and models
are done — see `spec.md` for goals/status and `EDA_FINDINGS.md` for the full
writeup of every result. Both are living documents — read them
before assuming the current state of the analysis, and update them (plus the
Changelog at the bottom of `spec.md`) when you add or change EDA/modeling work,
rather than duplicating findings only in code comments.

## Commands

No build, lint, or test tooling — this is a linear sequence of standalone
Python scripts, run manually one at a time:

```
python scripts/<NN>_<name>.py
```

Run scripts **from the repository root** — every script hardcodes paths like
`data/Final_data.csv` relative to the current working directory, not to the
script's own location.

Dependencies are listed in `requirements.txt` (`pip install -r
requirements.txt`): pandas, numpy, matplotlib, scikit-learn (imputation and
models), scipy (hypothesis tests). Minimum versions only, no lockfile.

## Architecture: the pipeline

Scripts in `scripts/` are numbered and must run in order, each consuming the
previous step's output:

1. `01_profile_dataset.py` — `data/Final_data.csv` → `data/dataset_profile.md`
   (per-column dtype/missingness/range profile)
2. `02_clean_dataset.py` — → `data/Final_data_cleaned.csv` (disease bucketing,
   drops the one bad `Cases` row, Kelvin→Celsius, etc.)
3. `03_impute_dataset.py` — → `data/Final_data_imputed.csv` (regression-based
   imputation for `Temp`/`LAI`, median fill for `preci`, adds `*_imputed` flags)
4. `04` through `19` — all read `data/Final_data_imputed.csv` and each
   produces one EDA plot PNG in `data/`. These are independent of each other
   (order among them doesn't matter), but all depend on steps 1–3 having run.
5. `20`+ — hypothesis-test scripts, one per hypothesis defined in `spec.md`
   section 4. Each reads `data/Final_data_imputed.csv`, prints a results
   table, and saves it as a CSV in `data/`; results are written up in
   `EDA_FINDINGS.md`. Tests are limited to the course's set: t-test,
   Mann-Whitney, ANOVA, Kruskal-Wallis, chi-square, Pearson, Spearman.
6. Modeling: `25_build_district_month_grid.py` → `data/district_month_grid.csv`
   (canonical district names, constructed zero rows, features), then
   `26_train_outbreak_model.py`, which reads that grid (not the imputed
   CSV) and writes metrics/importance CSVs and a results plot.
   `28_train_route_models.py` trains three transmission-route models
   (waterborne / Aedes / Anopheles); it reads the same grid plus the
   imputed CSV. Run 25 before 26 and 28. (27, a Dengue-only model, was
   deliberately dropped — the Aedes model supersedes it.) Splits are temporal (train ≤2017, validate 2018, test 2019,
   stress 2020–22); never use a random split, and keep features past-only.

7. Deployment: `docs/` is the project website, served by GitHub Pages from
   `main` / `docs`. `docs/index.html` is a hand-written static report of the
   findings (numbers copied from `EDA_FINDINGS.md`), and `docs/img/` holds
   copies of the plot PNGs from `data/` — committed, unlike `data/*.png`.
   If a plot or result changes, re-copy the PNG and update the page text.
   `docs/transcript.html` (session transcript, generated from `transcript.md`
   by `python tools/transcript_to_html.py transcript.md docs/transcript.html
   "<title>" "<note>"`) and `docs/viva_prep.html` (hand-written viva study
   guide) are also served from here, since the viva submission takes URLs.

Numbering has gaps (e.g. 11, 12, 15 are missing) — some exploratory scripts
were tried and deliberately deleted after review; this is expected, not a
missing-file bug. Do not renumber existing scripts to close gaps.

Every script follows the same shape: a module docstring stating its
Input/Output paths, `IN_PATH`/`OUT_PATH` constants, all logic in a `main()`,
guarded by `if __name__ == "__main__":`. Follow this shape for any new script
you add to `scripts/`.

Plotting scripts share a small hand-rolled visual style (not a shared theme
module — each script redefines it): warm off-white background (`SURFACE`,
`#fcfcfb`/`#fcfbf7`-ish), near-black ink for titles (`INK`), muted brown-gray
for axis text (`MUTED`), light warm gridlines (`GRID`), top/right spines
hidden, left/bottom spines colored to match `GRID`. Match this palette in new
plots rather than using matplotlib defaults.

## Data files and git

Per `.gitignore`, the raw dataset (`data/Final_data.csv`) and all `scripts/`
are committed, but everything derived/regenerable is gitignored: every
`data/*.csv` except the raw file (cleaned/imputed data, hypothesis-test
results, the model grid and metrics), `data/*.md` (`dataset_profile.md`),
and all `data/*.png` plots. Regenerate them by
re-running the pipeline rather than expecting them to already be in a fresh
checkout. `EDA_FINDINGS.md` exists specifically because the PNGs themselves
aren't committed — it's the durable record of what each plot showed.

Cases and outbreak-count are two different signals used throughout the EDA:
raw `Cases` is heavily skewed by a handful of extreme outlier records (see the
2009 Cholera outlier documented in `EDA_FINDINGS.md`), while outbreak *record
count* per period is the steadier, more climate-aligned signal. Later scripts
(16+) deliberately switched from Cases-based to count-based versions of
earlier analyses (e.g. `17_outbreak_trends_by_disease.py` vs. `06_disease_trends.py`,
`19_precip_lag_analysis_outbreak_count.py` superseding a since-deleted
Cases-based version) — prefer outbreak count over raw Cases as a signal in any
new analysis unless you have a specific reason to look at case totals.
