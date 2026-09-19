# EpiClim — EDA Plots & Findings

All plots are generated from `data/Final_data_imputed.csv` by the numbered
scripts in `scripts/`. Re-run any script to regenerate its output PNG in
`data/`. This file records what each plot shows and the key takeaways, so
the insights survive even though the PNGs themselves are gitignored.

---

## 1. Correlation heatmap
**Script:** `04_correlation_heatmap.py` → `data/correlation_heatmap.png`

Pearson correlation across all numeric columns (Cases, Deaths, day/mon/year,
Latitude/Longitude, preci, LAI, Temp).

- `Temp` correlates moderately with `LAI` (-0.44), `preci` (-0.39),
  `Longitude` (-0.37), `Latitude` (-0.30) — used to justify a location/season
  -based imputation for Temp and LAI rather than a flat mean/median fill.
- `mon` and `week_of_outbreak` correlate at 0.90 (expected — one derives
  from the other), so they carry redundant information as model features.
- `Cases`, `Deaths`, `day`, `year` show negligible correlation with
  anything — no useful signal there for imputation or as strong predictors.

## 2. Monthly time trends
**Script:** `05_time_trends.py` → `data/time_trends.png`

Total cases per month, cases per month by disease (overlaid — see caveat
below), and mean Temp/preci/LAI per month, 2009–2022.

- Climate variables (`preci`, `Temp`, `LAI`) show clean, regular annual
  seasonality (monsoon cycle).
- Total cases do **not** show smooth seasonality — instead there are sharp,
  isolated outbreak spikes (2009 Cholera, 2015 Dengue, 2018–19 Malaria).
  Outbreak surveillance data is fundamentally "mostly quiet, occasionally
  huge," not a steady seasonal signal.
- Caveat: the overlaid per-disease panel in this chart is hard to read
  because one disease's spike dwarfs the others on a shared y-axis — see
  plot 3 for the fixed version.

## 3. Per-disease trends (small multiples)
**Script:** `06_disease_trends.py` → `data/disease_trends.png`

Same per-disease monthly case data as plot 2, but each disease gets its own
subplot with its own y-scale, fixing the overplotting/scale problem.

- **Acute Diarrhoeal Disease**: strong, regular annual seasonality; overall
  case volume declining over time (peaks shrink after ~2016).
- **Dengue**: one massive 2015 spike plus smaller recurring spikes —
  outbreak-driven, not steadily seasonal.
- **Chikungunya**: concentrated almost entirely around 2011–2012, quiet
  otherwise — looks like a single epidemic wave.
- **Cholera**: dominated by the 2009 outlier spike (see "Known data-quality
  item" below).
- **Malaria**: two isolated massive spikes (~2015, ~2018), otherwise low
  and flat.
- **AES / Acute Gastroenteritis / Other**: data only starts well after 2009
  for these — worth checking if that's a real trend or a reporting-window
  artifact.

## 4. District hotspots — dominant disease
**Script:** `07_disease_location_scatter.py` → `data/disease_location_scatter.png`

One bubble per district (avoids overplotting from repeated weekly records):
color = the disease responsible for the most cases in that district, size =
that district's total case volume (sqrt-scaled).

- Bubble layout visually resembles India's outline (a nice sanity check that
  Latitude/Longitude are correct).
- Acute Diarrhoeal Disease is the dominant disease in 514 of 791 districts —
  the baseline endemic disease almost everywhere.
- Dengue, Cholera, Chikungunya, and Malaria each dominate distinct, smaller
  clusters of districts (125, 42, 41, 50 districts respectively).

## 5. District hotspots per disease (small multiples)
**Script:** `08_disease_location_small_multiples.py` → `data/disease_location_small_multiples.png`

One map panel per disease (all districts shown faintly for context; colored
bubbles sized by that disease's own case count).

Each disease has a visibly distinct geographic footprint:
- **Acute Diarrhoeal Disease**: everywhere (true baseline).
- **Dengue**: north (UP/Bihar/West Bengal, ~85–90°E/25–30°N) and a southern
  cluster (~80°E/12°N); largely absent from central India.
- **Chikungunya**: heavily southern (Kerala/Tamil Nadu) plus one large
  eastern cluster (~87°E/23°N).
- **Cholera**: eastern belt (West Bengal) and a distinct northern cluster
  (Punjab/J&K, ~74–75°E/31–33°N) — a very different footprint from
  dengue/chikungunya.
- **Malaria**: spread across central/east India and the northeast.
- **Acute Encephalitis Syndrome**: tightly clustered in the northeast
  (Assam/eastern UP/Bihar) — the classic AES belt.
- **Acute Gastroenteritis**: odd clustering (Kashmir + central India); may
  just reflect when/where this label started being used.
- **Other**: concentrated in the south.

## 6. Seasonality heatmap (disease × month + climate)
**Script:** `09_seasonality_heatmap.py` → `data/seasonality_heatmap.png`

Rows = 8 diseases (row-normalized: % of that disease's annual cases per
month) + Temp/preci/LAI (row-normalized: month's mean value, min-max scaled
0–1 within the row). Columns = months. Color shows each row's own relative
peak; printed numbers are the real values.

- **Precipitation peaks Jun–Aug** (monsoon), and so do **Acute Diarrhoeal
  Disease** (16.5% of its annual cases in July alone) and **Dengue**
  (42.7% in July) — classic post-monsoon waterborne/mosquito patterns.
- **Chikungunya peaks in August**, one month after Dengue — consistent with
  both being spread by the same *Aedes* mosquito.
- **Temperature peaks Apr–May**, and **Cholera's sharpest peak is May**
  (51.6% of its annual cases in one month) — just before the monsoon.
- **Malaria peaks in September**, after the monsoon — consistent with a
  mosquito-breeding lag after standing water accumulates.
- **LAI (vegetation) peaks Sep–Oct**, lagging precipitation by ~2 months.
- **Acute Encephalitis Syndrome** shows two disconnected peaks (Jan, Jul) —
  likely a small-sample artifact (only 111 records total).

## 7. Cases distribution by disease (box plot)
**Script:** `10_cases_by_disease_boxplot.py` → `data/cases_by_disease_boxplot.png`

Box plot of `Cases` per record, grouped by disease, log y-axis (Cases is
heavily right-skewed).

- All 8 diseases have surprisingly similar **typical** outbreak sizes —
  medians cluster between 9 and 35 cases per record. Dengue/Malaria's large
  *totals* come from outlier events, not larger typical outbreaks.
- Every disease has a long right tail of extreme outliers — "mostly small,
  occasionally massive" is a pattern across all diseases, not just Cholera.
- **Acute Encephalitis Syndrome** stands out with a genuinely lower median
  (9) — its outbreaks tend to be smaller events, not just fewer of them.
- **Malaria and Cholera** have the highest medians (35) and widest IQR.

## 8. Total cases by state/UT
**Script:** `13_cases_by_state.py` → `data/cases_by_state.png`

Horizontal bar chart, states sorted by total reported cases.

- **West Bengal dominates** (~179K total cases) — more than double the
  2nd-place state (Delhi, ~81K). Partly driven by the 2009 Cholera outlier,
  but West Bengal also topped the Cholera hotspot map independently, so
  it's a real pattern, not just the one outlier.
- Sharp drop-off after the top 5–6 states; many small states/UTs (Goa,
  Sikkim, Mizoram, Nagaland, Daman & Diu, Lakshadweep, Andaman & Nicobar)
  have near-zero reported cases — likely reflects population size and
  surveillance capacity as much as actual disease burden.

## 9. Reporting volume over time
**Script:** `14_cases_by_year.py` → `data/cases_by_year.png`

Two panels: number of records reported per year, and total cases per year.

- **2020 and 2022 are clear anomalies** — both records and total cases drop
  to the lowest in the whole span (2020: 151 records/~5K cases; 2022: 188
  records/~8K cases). 2020 is almost certainly COVID-19 disrupting routine
  surveillance; 2022 may be an incomplete year in this dataset (worth
  verifying the data collection cutoff).
- **2015 has a massive cases spike** (~140K) despite average record count —
  matches the Dengue epidemic seen in plot 3.
- Records-per-year is otherwise reasonably stable 2010–2019 (~570–1100),
  suggesting reporting consistency is fine outside the 2020/2022 dip.

## 10. Monthly outbreak-count trends (overall + per disease)
**Scripts:** `16_outbreak_trends.py` → `data/outbreak_trends.png`;
`17_outbreak_trends_by_disease.py` → `data/outbreak_trends_by_disease.png`

Same structure as plots 2–3, but tracking the number of outbreak *records*
reported per month instead of total *case* volume. Outbreak count is a
steadier signal than Cases, since Cases can be dominated by a handful of
extreme records (e.g. the 2009 Cholera outlier) while count just reflects
how often outbreaks were reported.

- **Overall outbreak count shows a genuinely regular annual seasonal
  wave** (peaking ~Jun–Aug, matching precipitation) — unlike total cases,
  which looked spiky and outbreak-driven rather than seasonal. This
  confirms outbreak *frequency* is climate-seasonal; outbreak *case size*
  is what gets randomly inflated by rare extreme events.
- Peak height declines steadily from ~2016 onward, with a sharp drop in
  2020 that doesn't recover by 2022 — consistent with COVID-era
  surveillance disruption and/or an incomplete final year (same anomaly
  seen in plot 9).
- **Per disease, Acute Diarrhoeal Disease, Dengue, Chikungunya, Cholera,
  and Malaria all show real, repeating annual cycles** in outbreak count —
  a genuine seasonal pattern that wasn't visible in any of these diseases'
  case-count charts, where one-off spikes dominated.
- **Cholera's chart no longer looks broken by the 2009 outlier** — with
  count instead of case totals, it shows a normal repeating seasonal
  pattern instead of one dominant spike.
- AES, Acute Gastroenteritis, and Other remain noisy/low-volume, as
  expected from their small record counts.
- **Takeaway for modeling**: outbreak count looks like a more stable,
  climate-aligned target/feature than total cases, which is heavily
  skewed by a small number of extreme outbreak events.

## 11. Precipitation-lag correlation
**Script:** `19_precip_lag_analysis_outbreak_count.py` → `data/precip_lag_correlation_outbreak_count.png`

Pearson correlation between national mean precipitation at month *(t − lag)*
and each disease's outbreak *count* at month *t*, for lag = 0–6 months.
(An earlier version of this used total Cases instead of outbreak count, but
Cases is dominated by a handful of extreme records — e.g. the 2009 Cholera
outlier — which blurred the lag pattern; outbreak count gives a cleaner,
stronger signal and replaced it.)

- **Dengue and Chikungunya peak clearly at lag 1** (0.52 and 0.30) — a
  clean "1-month mosquito-breeding delay" signal.
- **Acute Diarrhoeal Disease peaks at lag 0** (0.58) and decays fastest,
  going most negative by lag 5–6 (~-0.49) — tracks *current* rainfall, not
  a delayed effect.
- **Cholera and Malaria** peak around lag 0–1 rather than showing a sharp
  vector-borne delay, but decay more gradually than ADD.
- All correlations trend negative at long lags (4–6 months), likely just
  reflecting the seasonal cycle reversing rather than a causal effect.
- **Why the lag differs by transmission route**: Acute Diarrhoeal Disease is
  waterborne — contaminated drinking water and flooding from heavy rain
  cause illness almost immediately, so it tracks *current* rainfall (lag 0).
  The vector-borne diseases (Dengue, Chikungunya, Malaria, Cholera here)
  instead need mosquitoes to breed in standing water first, which takes
  time — hence their peak correlation appears at a 1-month lag rather than
  lag 0. The result lines up with this known biological mechanism.

## 12. Disease-to-disease correlation
**Script:** `18_disease_correlation_heatmap.py` → `data/disease_correlation_heatmap.png`

Pearson correlation across the 8 diseases' monthly outbreak-*count* time
series. (An earlier version used total cases instead — see below for why
that was changed and why the result isn't simply "better" as a result.)

- **Correlations are much higher across the board than the cases version**:
  Cholera vs. ADD jumps to 0.82 (was ~0.00 with cases), Malaria vs. ADD to
  0.50 (was 0.04), Dengue vs. Other to 0.48. Nearly every pair is now
  positively correlated.
- **This is not a cleaner signal — it's the shared-seasonality confound
  showing up in full force.** Plot 10 already established that outbreak
  count has a strong, near-universal monsoon-driven seasonal wave across
  almost every disease. Correlating outbreak counts between diseases
  mostly just measures "do both diseases get reported more in monsoon
  months" — which nearly all of them do — rather than genuine
  epidemiological co-occurrence. Ironically, total cases (despite being
  noisier generally) were *less* prone to this specific confound, since
  extreme one-off events broke the shared seasonal rhythm and kept the
  cases-based correlations lower and more differentiated.
- **Chikungunya remains the most independent disease even here** (max
  correlation 0.32, with Dengue) — consistent with its unusual pattern of
  one concentrated 2011–2012 epidemic wave rather than following the
  general seasonal reporting cycle like the others.
- **Net takeaway**: neither version (cases or outbreak count) gives a
  trustworthy read on genuine disease co-occurrence at this monthly/
  national aggregation level — cases wash out real signal under outlier
  noise, while outbreak count washes it out under shared seasonality. A
  real answer would likely need to control for seasonality first (e.g.
  correlate the *deseasonalized residuals* of each disease's monthly
  series) rather than raw monthly values of either metric.

---

## Known data-quality item: the 2009 Cholera outlier

A single record — **South 24 Parganas, West Bengal, 27th week of 2009: 51,225
cases, 23 deaths** — is by far the most extreme value in the dataset (the
next-highest Cholera record is 9,689 cases, same week, Purba Medinipur; the
third-highest anywhere is 5,825). Confirmed present in the raw source file
(not a pipeline artifact). Investigated and **intentionally left as-is**
(no change made) — it may be a genuine large outbreak or a data entry error,
but there's no way to verify externally within this dataset. It drives the
May 2009 spike visible in plots 2 and 3 (both case-count based); it does
**not** show up in the outbreak-count charts (plot 10), since count isn't
affected by how large any single outbreak's case number was.

---

## Open items (not yet addressed — see `spec.md`)

- District/state name consistency (spelling variants, renamed districts,
  J&K/Ladakh 2019 split) not yet checked.
- `week_of_outbreak` vs. `day`/`mon`/`year` alignment not fully verified.
- Targeted duplicate check on week+district+disease combos (only a
  whole-row duplicate check has been done — 0 found).
