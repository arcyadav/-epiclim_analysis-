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

# Hypothesis test results

Hypotheses are defined in `spec.md` section 4. Each is tested by its own
script, which prints a results table and saves it as a CSV in `data/`.

## H1. Precipitation lag differs by transmission route
**Script:** `20_h1_precip_lag_test.py` → `data/h1_precip_lag_results.csv`

Pearson and Spearman correlation between national mean precipitation at
month *(t − lag)* and each disease's outbreak count at month *t*, lag 0 and
1, over 158 months (no empty months in the range). p-values Holm-corrected
across the 10 disease × lag tests within each method.

| Disease | Pearson r (lag 0 / lag 1) | Spearman ρ (lag 0 / lag 1) | Strongest lag |
|---|---|---|---|
| Acute Diarrhoeal Disease | **0.58** / 0.36 | **0.55** / 0.41 | 0 |
| Dengue | 0.44 / **0.52** | 0.46 / **0.50** | 1 |
| Chikungunya | 0.20 / **0.30** | 0.24 / **0.30** | 1 |
| Cholera | **0.51** / 0.33 | **0.54** / 0.46 | 0 |
| Malaria | **0.36** / 0.34 | **0.47** / 0.45 | 0 (near tie) |

- **H0 rejected for all 20 tests** (every Holm-adjusted p < 0.05; largest
  is Chikungunya lag-0 Pearson, p ≈ 0.012). Rainfall and outbreak frequency
  are positively correlated for every disease at both lags.
- **The lag pattern splits along transmission route**, and Pearson and
  Spearman agree on the strongest lag for every disease:
  - *Aedes*-borne **Dengue and Chikungunya** are strongest at lag 1 — the
    mosquito-breeding delay.
  - Waterborne **ADD and Cholera** are strongest at lag 0 — contaminated
    water acts immediately. (Note: Cholera is waterborne, not vector-borne
    as the #11 writeup above groups it; this result fits that.)
  - **Malaria** is effectively tied between lags 0 and 1 (Δr ≈ 0.02), so it
    doesn't cleanly support either side.
- Spearman is higher than Pearson for Malaria and Cholera lag 1, suggesting
  a monotonic but not linear relationship (a few extreme months pull
  Pearson down).
- **Limitations:** whether lag 1 is *significantly* stronger than lag 0 is
  not formally tested — only that each correlation is non-zero. Monthly
  series are autocorrelated and share the monsoon seasonal cycle, so
  p-values are optimistic and some of the correlation is seasonality
  itself rather than a direct rainfall effect.

## H2. Outbreaks are seasonal
**Script:** `21_h2_seasonality_test.py` → `data/h2_seasonality_results.csv`

Chi-square goodness-of-fit per disease: outbreak record counts by calendar
month vs. an even spread. The expected counts are weighted by how often
each calendar month occurs in the data range (**2009-05 to 2022-06**, so
May/June occur 14 times, the rest 13). p-values Holm-corrected across the
8 diseases; df = 11 for all.

| Disease | n | χ² | Holm p | Cramér's V | Peak month (share) |
|---|---|---|---|---|---|
| Acute Diarrhoeal Disease | 5126 | 1432 | 1e-299 | 0.16 | Jul (17%) |
| Dengue | 1618 | 511 | 1e-101 | 0.17 | Sep (16%) |
| Chikungunya | 731 | 73 | 9e-11 | 0.10 | Aug (13%) |
| Cholera | 666 | 329 | 4e-63 | 0.21 | Jul (21%) |
| Malaria | 544 | 182 | 3e-32 | 0.17 | Jul (16%) |
| Acute Encephalitis Syndrome | 111 | 80 | 5e-12 | 0.26 | Jun (27%) |
| Acute Gastroenteritis | 100 | 49 | 2e-6 | 0.21 | Jun (20%) |
| Other | 88 | 45 | 5e-6 | 0.22 | Sep (19%) |

- **H0 rejected for all 8 diseases.** Every disease's outbreaks cluster in
  certain months. All expected counts are ≥ 7, so the chi-square
  approximation is valid even for the small diseases.
- **Every peak falls in Jun–Sep**, the monsoon window. An even spread would
  put ~8% in each month; the peaks hold 13–27%.
- **Chikungunya is the weakest** (V = 0.10). This fits its concentrated
  2011–2012 epidemic wave: one burst of outbreaks rather than a strong
  repeating annual cycle.
- **Record-count peaks differ from the case-weighted peaks in #6.** By
  outbreak count, Dengue peaks in Sep (not Jul), Cholera in Jul (not May),
  and Malaria in Jul (not Sep). The #6 heatmap weights months by case
  totals, so a few huge outbreaks (e.g. the 2009 Cholera outlier in a May
  reporting week) shifted its peaks. How *often* outbreaks happen follows
  the monsoon more uniformly than how *large* they get.
- **The data ends in June 2022**, confirming the suspicion in #9 that 2022
  is an incomplete year rather than a real drop.
- **Limitations:** records in the same district or outbreak wave aren't
  fully independent, which inflates χ². With p-values this small the
  conclusion holds anyway; the Cramér's V values (0.10–0.26, small to
  medium) are the fairer measure of how strong the seasonality is.

## H3. Diseases occur under different temperature conditions
**Script:** `22_h3_temp_by_disease_test.py` →
`data/h3_temp_by_disease_summary.csv`, `data/h3_temp_by_disease_pairwise.csv`

Temperature at outbreak time compared across the 8 diseases, using only the
8,046 rows with a measured (non-imputed) `Temp`.

| Disease | n | Mean °C | Median °C | SD |
|---|---|---|---|---|
| Chikungunya | 684 | 33.8 | 33.1 | 5.9 |
| Dengue | 1471 | 31.5 | 30.8 | 6.3 |
| Other | 78 | 31.4 | 31.0 | 5.1 |
| Acute Diarrhoeal Disease | 4542 | 31.2 | 30.0 | 7.3 |
| Cholera | 590 | 31.2 | 29.7 | 6.7 |
| Acute Gastroenteritis | 82 | 30.5 | 30.3 | 9.6 |
| Malaria | 493 | 30.2 | 29.0 | 5.7 |
| Acute Encephalitis Syndrome | 106 | 27.5 | 27.8 | 7.8 |

- **ANOVA assumptions fail:** Shapiro-Wilk rejects normality for 7 of 8
  diseases, and Levene rejects equal variances (p ≈ 4e-14). So
  **Kruskal-Wallis is the test to trust**, with ANOVA shown for comparison.
- **H0 rejected by both tests:** ANOVA F(7, 8038) = 18.9, p ≈ 4e-25;
  Kruskal-Wallis H(7) = 162, p ≈ 1e-31. The two agree, which makes the
  conclusion robust to the assumption violations.
- **But the effect is tiny:** η² = 0.016 and ε² = 0.019. Disease type
  explains only ~2% of the variation in outbreak temperature. It's
  significant mainly because n is large. The medians of 5 of the 8 diseases
  sit within about 2°C of each other (29.0–31.0°C).
- **Post-hoc (28 pairwise Mann-Whitney tests, Bonferroni):** 13 pairs
  differ significantly. Two diseases drive almost all of it:
  - **Chikungunya is warmest** (median 33.1°C). It differs from every
    well-sampled disease, most strongly from Malaria (rank-biserial r = 0.36).
  - **AES is coolest** (median 27.8°C). It differs from most diseases, most
    strongly from Chikungunya (r = 0.50, a large effect).
  - Dengue vs. Malaria (r = 0.16) and ADD vs. Malaria (r = 0.10) are
    significant but small. ADD, Dengue, Cholera, Acute Gastroenteritis and
    Other are statistically indistinguishable from one another.
- **Likely geographic confound:** the two outliers match the hotspot maps
  in #5. Chikungunya is concentrated in the hot south (Kerala/Tamil Nadu),
  and AES in the northeast/eastern UP–Bihar belt. Temp also correlates with
  latitude/longitude (#1). So this probably reflects *where* each disease
  occurs more than a temperature preference. Testing that would need
  temperature compared within regions.

## H4. Diseases have distinct geographic footprints
**Script:** `23_h4_disease_region_test.py` →
`data/h4_disease_region_observed.csv`, `data/h4_disease_region_residuals.csv`

Chi-square test of independence on the disease × region table of outbreak
record counts. States/UTs are grouped into 6 regions following India's
Zonal Councils: North (J&K, HP, Punjab, Haryana, Chandigarh, Delhi,
Uttarakhand, Rajasthan), Central (UP, MP, Chhattisgarh), East (Bihar,
Jharkhand, Odisha, West Bengal, A&N), West (Maharashtra, Gujarat, Goa,
DNH, Daman & Diu), South (Karnataka, TN, Kerala, AP, Telangana,
Puducherry, Lakshadweep), Northeast (the 8 NE states incl. Sikkim). All 36
state names in the data mapped cleanly, with no spelling variants.
"Other" is excluded (a grab-bag of labels, not one disease), leaving
8,896 records.

Share of each disease's outbreaks by region (%):

| Disease | North | Central | East | West | South | Northeast |
|---|---|---|---|---|---|---|
| Acute Diarrhoeal Disease | 11.6 | 17.5 | 25.4 | 15.1 | 24.9 | 5.5 |
| Dengue | 6.6 | 7.2 | 13.5 | 24.5 | **41.3** | 6.8 |
| Chikungunya | 1.4 | 7.0 | 5.9 | 25.2 | **59.6** | 1.0 |
| Cholera | **18.5** | 7.1 | 21.2 | 19.5 | 26.4 | 7.4 |
| Malaria | 4.8 | **25.0** | 21.5 | 23.0 | 10.5 | **15.3** |
| Acute Encephalitis Syndrome | 5.4 | 7.2 | 27.9 | 13.5 | 0.0 | **45.9** |
| Acute Gastroenteritis | 18.0 | 16.0 | 9.0 | **33.0** | 19.0 | 5.0 |

- **H0 rejected:** χ²(30) = 1440, p ≈ 3e-284, **Cramér's V = 0.18**. For
  a table this shape (min dimension 6, so 5 degrees of freedom for the
  effect) that's a medium-to-large effect, much stronger than H3's
  temperature effect. No expected counts are below 5 (min 6.6), so the
  test is valid.
- **Which cells drive it** (adjusted standardized residuals; significant if
  |z| > 3.24, Bonferroni over 42 cells):
  - **Chikungunya → South** (z = +18.6, 60% of its outbreaks), rare in the
    North/East/Northeast. The strongest cell in the table.
  - **AES → Northeast** (z = +16.8, 46%), and **zero** outbreaks in the
    South. Confirms the AES belt from #5.
  - **Dengue → South and West** (+11.4, +6.7), under-represented in
    North/Central/East.
  - **Malaria → Central and Northeast** (+7.4, +8.4), strongly
    under-represented in the South (−10.1).
  - **Cholera → North** (+7.7), matching the Punjab/J&K cluster in #5. It
    is *not* over-represented in the East (z = 0.2). The West Bengal
    hotspot in #5 was case-weighted (driven by the 2009 outlier), while by
    outbreak count Cholera's share of the East matches the average.
  - **ADD → North, Central, East** (+6 to +12), with a lower share in the
    West/South, where vector-borne diseases take a bigger slice.
  - Acute Gastroenteritis has only one significant cell (West, +3.7).
- **Interpretation note:** the test compares each region's *mix* of
  diseases, not raw burden, so differences in how much each region reports
  overall (surveillance capacity, population) are largely factored out.
  It still counts outbreak records rather than cases per population.

## H5. More outbreaks are reported in monsoon months
**Script:** `24_h5_monsoon_outbreak_test.py` → `data/h5_monsoon_outbreak_results.csv`

Each data point is one year-month's total outbreak record count (all
diseases). Monsoon (Jun–Sep) vs. all other months, one-sided (monsoon
higher). Main analysis excludes 2020 (COVID reporting collapse) and 2022
(data ends in June); a sensitivity run on all months is alongside.

| | Main (excl. 2020, 2022) | All months |
|---|---|---|
| Months (monsoon / other) | 48 / 92 | 53 / 105 |
| Mean outbreaks/month (monsoon / other) | 98.7 / 42.5 | 90.7 / 39.8 |
| Median (monsoon / other) | 95 / 35 | 89 / 32 |
| Welch t-test | t = 9.56, p ≈ 1e-14 | t = 7.97, p ≈ 1e-11 |
| Cohen's d | 1.91 | 1.59 |
| Mann-Whitney U | U = 4002, p ≈ 2e-15 | U = 4689, p ≈ 1e-12 |
| Rank-biserial r | 0.81 | 0.69 |

- **H0 rejected by both tests, in both analyses.** Monsoon months average
  **~2.3× as many outbreaks** as other months (median 95 vs. 35).
- **The effect is very large:** Cohen's d = 1.9, and rank-biserial
  r = 0.81 means a randomly chosen monsoon month beats a randomly chosen
  non-monsoon month about 90% of the time. This is the largest effect
  across H1–H5.
- **t-test vs. Mann-Whitney:** the t-test's assumptions are partly broken.
  Non-monsoon counts are clearly non-normal (Shapiro-Wilk p ≈ 4e-7,
  right-skewed), though monsoon counts pass (p = 0.15). Variances are
  unequal (Levene p ≈ 0.006), which is why Welch's version is used rather
  than the pooled t-test. **Mann-Whitney is the more trustworthy test**
  because it makes no normality assumption. The two agree here because
  the samples are large enough (48/92) for the t-test to be fairly robust,
  and because the gap between groups is so big.
- **Excluding 2020/2022 strengthens the result** (d 1.59 → 1.91). Their
  unusually low monsoon months pull the monsoon mean down (98.7 → 90.7)
  and widen its spread (SD 37 → 43), while the non-monsoon SD is unchanged
  (24.9 in both).
- **Limitations:** months aren't independent (consecutive months are
  autocorrelated, and reporting volume drifts over the years; see #9/#10),
  so the p-values are optimistic. With an effect this size the conclusion
  isn't in doubt. H5 overlaps with H2 (both are about seasonality); H2
  shows *which* months each disease peaks in, while H5 measures *how much*
  higher overall reporting is during the monsoon.

---

# Model: district × month outbreak prediction

Setup is documented in `spec.md` section 6.

## Building the grid
**Script:** `25_build_district_month_grid.py` → `data/district_month_grid.csv`

- **District names canonicalized:** 795 raw state + district names → **764**
  districts. Case, punctuation and spacing variants were merged (e.g.
  `Ashok Nagar`/`Ashoknagar`, `North 24 Parganas`/`24 North Parganas`,
  a `Ramanathapuram Paramakudi` spelling with corrupted characters), plus
  two manual merges: `Karbi-Anglong (Diphu)` → `Karbi Anglong`, and
  Rangareddy's pre-2014 Andhra Pradesh records → Telangana. Renamed or
  split districts with *different* names are not merged.
- **Grid:** 764 districts × 158 months = 120,712 cells, 6,700 with an
  outbreak (5.55%).
- **Climate per cell:** the mean measured rainfall/temperature for the
  cell's region that month (lag 0 and lag 1). 94 of 948 region-months have
  no records; those are filled from training-period climatology in the
  training script.

## Results
**Script:** `26_train_outbreak_model.py` → `data/outbreak_model_metrics.csv`,
`data/outbreak_model_importance.csv`, `data/outbreak_model_results.png`

685 districts (those with an outbreak in 2009–2017). Hyperparameters and
the yes/no threshold were chosen on 2018; models were then refit on
2009–2018 and scored once on 2019.

| Model | Test 2019 PR-AUC | ROC-AUC | Precision | Recall | Stress 2020–22 PR-AUC |
|---|---|---|---|---|---|
| Random guessing | 0.061 | 0.50 | — | — | 0.026 |
| Logistic regression, no climate | 0.192 | 0.758 | 0.23 | 0.26 | 0.122 |
| Logistic regression, full | 0.196 | 0.760 | 0.24 | 0.31 | 0.120 |
| Gradient boosting, no climate | 0.195 | 0.779 | 0.27 | 0.22 | 0.125 |
| Gradient boosting, full | 0.196 | 0.777 | 0.25 | 0.29 | 0.120 |

- **The models do learn something real:** PR-AUC ≈ 0.19–0.20 against
  0.061 for random guessing, about **3.2× better**, and ROC-AUC 0.76–0.78.
  At the chosen threshold, roughly 1 in 4 alerts is a real outbreak, and
  the models catch 22–31% of real outbreaks.
- **But they're only moderately useful as forecasters.** Most district-months
  with an outbreak look very similar to ones without, given the available
  features.
- **Climate adds almost nothing.** Each full model beats its no-climate
  version by at most 0.004 PR-AUC, which is within noise. Logistic
  regression and gradient boosting perform about the same, so non-linear
  effects don't help either.
- **Why climate doesn't help, even though H1/H2/H5 found strong climate
  links:** the region-level climate features mostly carry the *seasonal
  cycle*, which month and district history already encode. Permutation
  importance shows this: in the gradient boosting model, shuffling
  `region_preci` hurts (it is the 3rd most important feature), but shuffling
  `mon` doesn't. The model uses rainfall *instead of* month, not *on top
  of* it. The hypothesis tests showed climate and outbreaks move together;
  the model shows that at this resolution climate has no extra predictive
  information beyond "what month is it."
- **District history dominates:** the district's long-run outbreak rate,
  its count over the past 12 months, and whether it had one last month are
  the top features for both models. *Where* outbreaks happened before is
  the best predictor of where they'll happen next.
- **Stress test 2020–22:** PR-AUC falls to ~0.12, but the base rate also
  collapses to 2.6%, so the lift over random is still about 4.7×, and
  ROC-AUC holds at 0.75–0.79. The ranking of districts survives the
  COVID-era reporting drop; the absolute probabilities don't, since the
  models were trained when outbreaks were ~2.7× as common.
- **Limitations:**
  - Region-level climate is coarse. District-level rainfall from external
    data (IMD gridded or CHIRPS) is the obvious next step and the fairest
    test of whether climate adds predictive value.
  - Region-month climate is averaged over the outbreak records in that
    region-month, so it is biased toward outbreak locations.
  - A missing record is treated as "no outbreak" but may be "no report."
  - Districts created mid-period get zero-filled months from before they
    existed.

## Transmission-route models
**Script:** `28_train_route_models.py` → `data/route_model_metrics.csv`,
`data/route_model_importance.csv`, `data/route_model_results.png`

Three models, one per transmission route, because H1 and H4 showed the routes
respond to rainfall with different lags and occupy different regions:
**Waterborne** (ADD, Cholera, Acute Gastroenteritis), ***Aedes*** (Dengue,
Chikungunya: same mosquito), ***Anopheles*** (Malaria). AES is left out
(a syndrome with mixed causes). Same grid and split as the any-disease
model. One model type per route, gradient boosting, with the same model
minus climate features as the baseline. History features count only that
group's past outbreaks, and each model covers only districts with a group
outbreak in 2009–2017.

| Route | Districts | Test 2019 positives | Random | No climate | With climate | ROC-AUC (with climate) |
|---|---|---|---|---|---|---|
| Waterborne | 611 | 290 | 0.040 | 0.133 | 0.130 | 0.744 |
| *Aedes* | 315 | 162 | 0.043 | 0.187 | 0.185 | 0.813 |
| *Anopheles* | 184 | **18** | 0.008 | 0.058 | 0.093 | 0.865 |

(Values in the Random / No climate / With climate columns are PR-AUC.)

- **All three beat random:** waterborne ~3.3×, *Aedes* ~4.3×, *Anopheles*
  ~11× on PR-AUC. *Aedes* outbreaks are the most predictable in absolute
  terms (PR-AUC 0.19, ROC-AUC 0.81); waterborne the least (0.13).
- **Climate still adds no measurable score for waterborne or *Aedes***
  (−0.003 and −0.002 PR-AUC, within noise).
- **But the models use the rainfall lag each route's biology predicts,
  reproducing H1 from a completely different method:**
  - The **waterborne** model relies on **same-month rainfall**
    (`region_preci`, 4th most important) and ignores last month's.
  - The ***Aedes*** model relies on **last month's rainfall**
    (`region_preci_lag1`, its #1 feature) and ignores same-month rain.
  - In both, `mon` falls to ~zero importance: rainfall acts as the seasonal
    clock instead of month, which is why the score doesn't rise.
- **Anopheles is too small to judge.** Malaria reporting thinned out after
  2016, leaving only 10 positives in the validation year and 18 in the test
  year. Climate *appears* to help (0.058 → 0.093 on test, 0.128 → 0.214 on
  validation), and the model uses same-month rain, last month's rain and
  temperature. But 18 positives can't separate that from chance: one or two
  extra hits move PR-AUC by that much. The baseline flagged none of the 18
  at its threshold. Treat it as suggestive, not a result.
- **Splitting by route helped interpretability more than accuracy.**
  Waterborne alone scores lower than the mixed any-disease model (0.13 vs.
  0.20), partly because its base rate is lower (4.0% vs. 6.1%). What the
  split does buy is that each model's use of rainfall lines up with its
  transmission mechanism, which the mixed model hid.
- (A Dengue-only model was also tried and dropped: the *Aedes* model
  matched it, 0.185 vs. 0.169 test PR-AUC, with twice the positives, so it
  was redundant.)

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
