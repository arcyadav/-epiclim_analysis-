"""Hypothesis test H1 (see spec.md section 4): precipitation lag differs by
transmission route.

H0: no correlation between national mean precipitation at month (t - lag)
    and a disease's outbreak count at month t.
H1: there is a correlation, and the strongest lag differs by disease
    (expected: Dengue/Chikungunya strongest at lag 1, ADD at lag 0).

For each disease and lag in {0, 1}, runs Pearson and Spearman correlation
tests. p-values are Holm-corrected within each method across all
disease x lag tests. Monthly series are autocorrelated, so p-values are
optimistic -- treat them as indicative, not exact.

Unlike 19_precip_lag_analysis_outbreak_count.py, the monthly series is
reindexed to a full calendar range before shifting, so "lag 1" always means
one calendar month even if some month has no records at all.

Input:  data/Final_data_imputed.csv
Output: data/h1_precip_lag_results.csv
"""
import numpy as np
import pandas as pd
from scipy import stats

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/h1_precip_lag_results.csv"

DISEASE_ORDER = [
    "Acute Diarrhoeal Disease",
    "Dengue",
    "Chikungunya",
    "Cholera",
    "Malaria",
]
LAGS = [0, 1]
ALPHA = 0.05


def holm_correct(p_values):
    """Holm-Bonferroni adjusted p-values, returned in the original order."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adjusted = np.empty(m)
    running_max = 0.0
    for rank, idx in enumerate(order):
        running_max = max(running_max, (m - rank) * p[idx])
        adjusted[idx] = min(running_max, 1.0)
    return adjusted


def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))

    full_range = pd.date_range(df["date"].min(), df["date"].max(), freq="MS")
    monthly_preci = df.groupby("date")["preci"].mean().reindex(full_range)
    outbreaks_by_disease = (
        df.groupby(["date", "Disease"]).size().unstack(fill_value=0)
        .reindex(full_range, fill_value=0)
    )
    n_empty = monthly_preci.isna().sum()
    print(f"Months in range: {len(full_range)} ({n_empty} with no records at all)")

    rows = []
    for disease in DISEASE_ORDER:
        outbreak_count = outbreaks_by_disease[disease]
        for lag in LAGS:
            shifted_preci = monthly_preci.shift(lag)
            valid = shifted_preci.notna()
            x, y = shifted_preci[valid], outbreak_count[valid]
            pearson_r, pearson_p = stats.pearsonr(x, y)
            spearman_rho, spearman_p = stats.spearmanr(x, y)
            rows.append({
                "disease": disease,
                "lag": lag,
                "n_months": int(valid.sum()),
                "pearson_r": pearson_r,
                "pearson_p": pearson_p,
                "spearman_rho": spearman_rho,
                "spearman_p": spearman_p,
            })

    results = pd.DataFrame(rows)
    results["pearson_p_holm"] = holm_correct(results["pearson_p"])
    results["spearman_p_holm"] = holm_correct(results["spearman_p"])
    results["reject_H0_pearson"] = results["pearson_p_holm"] < ALPHA
    results["reject_H0_spearman"] = results["spearman_p_holm"] < ALPHA
    results.to_csv(OUT_PATH, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("\nH1 correlation tests (Holm-corrected within each method):\n")
    print(results[[
        "disease", "lag", "n_months",
        "pearson_r", "pearson_p_holm", "reject_H0_pearson",
        "spearman_rho", "spearman_p_holm", "reject_H0_spearman",
    ]].to_string(index=False, float_format=lambda v: f"{v:.4g}"))

    print("\nStrongest lag per disease:")
    for disease in DISEASE_ORDER:
        sub = results[results["disease"] == disease].set_index("lag")
        best_pearson = sub["pearson_r"].idxmax()
        best_spearman = sub["spearman_rho"].idxmax()
        print(f"  {disease:<26} Pearson: lag {best_pearson}   Spearman: lag {best_spearman}")

    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
