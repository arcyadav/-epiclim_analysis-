"""Hypothesis test H2 (see spec.md section 4): outbreaks are seasonal.

H0: a disease's outbreak records are spread evenly across the 12 calendar
    months.
H1: they are concentrated in particular months.

Runs a chi-square goodness-of-fit test per disease on outbreak record
counts by calendar month. p-values are Holm-corrected across diseases.
Effect size is Cramer's V for goodness-of-fit, sqrt(chi2 / (n * (k - 1))).

"Evenly" is weighted by how many times each calendar month appears in the
data's date range: the range doesn't cover a whole number of years, so some
calendar months occur one more time than others and would get more records
even with no seasonality.

Input:  data/Final_data_imputed.csv
Output: data/h2_seasonality_results.csv
"""
import calendar

import numpy as np
import pandas as pd
from scipy import stats

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/h2_seasonality_results.csv"

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
MONTHS = list(range(1, 13))
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
    month_occurrences = (
        pd.Series(full_range.month).value_counts().reindex(MONTHS, fill_value=0)
    )
    expected_share = month_occurrences / month_occurrences.sum()
    print(f"Date range: {full_range[0]:%Y-%m} to {full_range[-1]:%Y-%m} "
          f"({len(full_range)} months)")
    print("Times each calendar month occurs in range: "
          + ", ".join(f"{calendar.month_abbr[m]}={month_occurrences[m]}" for m in MONTHS))

    counts_by_month = (
        df.groupby(["Disease", "mon"]).size().unstack(fill_value=0)
        .reindex(columns=MONTHS, fill_value=0)
    )

    rows = []
    for disease in DISEASE_ORDER:
        observed = counts_by_month.loc[disease]
        n = int(observed.sum())
        expected = expected_share * n
        chi2, p = stats.chisquare(observed, f_exp=expected)
        peak_month = int(observed.idxmax())
        rows.append({
            "disease": disease,
            "n_records": n,
            "min_expected": expected.min(),
            "chi2": chi2,
            "df": len(MONTHS) - 1,
            "p": p,
            "cramers_v": np.sqrt(chi2 / (n * (len(MONTHS) - 1))),
            "peak_month": calendar.month_abbr[peak_month],
            "peak_share": observed[peak_month] / n,
        })

    results = pd.DataFrame(rows)
    results["p_holm"] = holm_correct(results["p"])
    results["reject_H0"] = results["p_holm"] < ALPHA
    results.to_csv(OUT_PATH, index=False)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("\nH2 chi-square goodness-of-fit per disease (Holm-corrected):\n")
    print(results[[
        "disease", "n_records", "min_expected", "chi2", "df", "p_holm",
        "reject_H0", "cramers_v", "peak_month", "peak_share",
    ]].to_string(index=False, float_format=lambda v: f"{v:.4g}"))

    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
