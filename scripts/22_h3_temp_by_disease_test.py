"""Hypothesis test H3 (see spec.md section 4): diseases occur under
different temperature conditions.

H0: temperature at outbreak time has the same distribution (mean for ANOVA,
    rank distribution for Kruskal-Wallis) across diseases.
H1: at least one disease differs.

Uses only rows with a measured temperature (Temp_imputed == False), since
the imputation regression had R^2 ~ 0.17. Runs:
  - assumption checks: Shapiro-Wilk per disease (normality) and Levene
    (equal variances), which decide whether ANOVA can be trusted
  - one-way ANOVA (effect size eta^2) and Kruskal-Wallis (effect size
    epsilon^2) side by side
  - post-hoc: pairwise Mann-Whitney U, Bonferroni-corrected, with
    rank-biserial correlation as the per-pair effect size

Input:  data/Final_data_imputed.csv
Output: data/h3_temp_by_disease_summary.csv   (per-disease stats + tests)
        data/h3_temp_by_disease_pairwise.csv  (post-hoc Mann-Whitney pairs)
"""
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats

IN_PATH = "data/Final_data_imputed.csv"
SUMMARY_PATH = "data/h3_temp_by_disease_summary.csv"
PAIRWISE_PATH = "data/h3_temp_by_disease_pairwise.csv"

DISEASE_ORDER = [
    "Acute Diarrhoeal Disease",
    "Dengue",
    "Chikungunya",
    "Cholera",
    "Malaria",
    "Acute Encephalitis Syndrome",
    "Acute Gastroenteritis",
    "Other",
]
ALPHA = 0.05
# scipy's Shapiro-Wilk p-value is only accurate up to n = 5000
SHAPIRO_MAX_N = 5000
RANDOM_SEED = 0


def main():
    df = pd.read_csv(IN_PATH)
    measured = df[~df["Temp_imputed"].astype(bool)]
    print(f"Rows with measured Temp: {len(measured)} of {len(df)}")

    groups = {d: measured.loc[measured["Disease"] == d, "Temp"].to_numpy()
              for d in DISEASE_ORDER}
    groups = {d: g for d, g in groups.items() if len(g) > 0}
    all_temps = np.concatenate(list(groups.values()))
    n, k = len(all_temps), len(groups)

    rng = np.random.default_rng(RANDOM_SEED)
    summary_rows = []
    for disease, temps in groups.items():
        sample = temps if len(temps) <= SHAPIRO_MAX_N else rng.choice(
            temps, SHAPIRO_MAX_N, replace=False)
        _, shapiro_p = stats.shapiro(sample)
        summary_rows.append({
            "disease": disease,
            "n": len(temps),
            "mean": temps.mean(),
            "median": np.median(temps),
            "std": temps.std(ddof=1),
            "shapiro_p": shapiro_p,
            "normal": shapiro_p >= ALPHA,
        })
    summary = pd.DataFrame(summary_rows)

    levene_stat, levene_p = stats.levene(*groups.values())

    f_stat, anova_p = stats.f_oneway(*groups.values())
    grand_mean = all_temps.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups.values())
    ss_total = ((all_temps - grand_mean) ** 2).sum()
    eta_sq = ss_between / ss_total

    h_stat, kruskal_p = stats.kruskal(*groups.values())
    epsilon_sq = (h_stat - k + 1) / (n - k)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    fmt = lambda v: f"{v:.4g}"
    print("\nTemperature (deg C) at outbreak time, by disease:\n")
    print(summary.to_string(index=False, float_format=fmt))

    print("\nAssumption checks for ANOVA:")
    print(f"  Shapiro-Wilk: {int((~summary['normal']).sum())} of {k} diseases "
          f"reject normality (alpha {ALPHA})")
    print(f"  Levene:       W = {levene_stat:.4g}, p = {levene_p:.4g} "
          f"({'unequal' if levene_p < ALPHA else 'equal'} variances)")

    print("\nOmnibus tests:")
    print(f"  One-way ANOVA:  F({k - 1}, {n - k}) = {f_stat:.4g}, p = {anova_p:.4g}, "
          f"eta^2 = {eta_sq:.4f}")
    print(f"  Kruskal-Wallis: H({k - 1}) = {h_stat:.4g}, p = {kruskal_p:.4g}, "
          f"epsilon^2 = {epsilon_sq:.4f}")

    tests = pd.DataFrame([
        {"disease": "[ANOVA]", "stat": f_stat, "p": anova_p, "effect_size": eta_sq},
        {"disease": "[Kruskal-Wallis]", "stat": h_stat, "p": kruskal_p,
         "effect_size": epsilon_sq},
        {"disease": "[Levene]", "stat": levene_stat, "p": levene_p, "effect_size": np.nan},
    ])
    pd.concat([summary, tests], ignore_index=True).to_csv(SUMMARY_PATH, index=False)

    pairs = list(combinations(groups.keys(), 2))
    pair_rows = []
    for a, b in pairs:
        u_stat, p = stats.mannwhitneyu(groups[a], groups[b], alternative="two-sided")
        pair_rows.append({
            "disease_a": a,
            "disease_b": b,
            "median_a": np.median(groups[a]),
            "median_b": np.median(groups[b]),
            "U": u_stat,
            "p": p,
            "p_bonferroni": min(p * len(pairs), 1.0),
            # positive = disease_a tends to be warmer than disease_b
            "rank_biserial": 2 * u_stat / (len(groups[a]) * len(groups[b])) - 1,
        })
    pairwise = pd.DataFrame(pair_rows)
    pairwise["significant"] = pairwise["p_bonferroni"] < ALPHA
    pairwise.to_csv(PAIRWISE_PATH, index=False)

    print(f"\nPost-hoc pairwise Mann-Whitney U ({len(pairs)} pairs, Bonferroni):\n")
    print(pairwise.sort_values("rank_biserial", key=abs, ascending=False)
          .to_string(index=False, float_format=fmt))

    print(f"\nSaved to {SUMMARY_PATH} and {PAIRWISE_PATH}")


if __name__ == "__main__":
    main()
