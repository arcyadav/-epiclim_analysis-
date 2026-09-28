"""Hypothesis test H5 (see spec.md section 4): more outbreaks are reported
in monsoon months.

H0: the monthly outbreak count in monsoon months (Jun-Sep) is not higher
    than in non-monsoon months.
H1: it is higher (one-sided).

Unit of analysis is one year-month's total outbreak record count (all
diseases). Runs Welch's t-test and Mann-Whitney U side by side, with
Shapiro-Wilk and Levene checks showing whether the t-test's assumptions
hold, and effect sizes Cohen's d (t-test) and rank-biserial correlation
(Mann-Whitney).

Main analysis excludes 2020 and 2022: 2020 reporting collapsed (likely
COVID) and the data ends in June 2022, so both years would drag counts
down for reasons unrelated to season. A sensitivity run on all months is
reported alongside.

Input:  data/Final_data_imputed.csv
Output: data/h5_monsoon_outbreak_results.csv
"""
import numpy as np
import pandas as pd
from scipy import stats

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/h5_monsoon_outbreak_results.csv"

MONSOON_MONTHS = [6, 7, 8, 9]
EXCLUDED_YEARS = [2020, 2022]
ALPHA = 0.05


def run_tests(monthly, label):
    monsoon = monthly.loc[monthly["mon"].isin(MONSOON_MONTHS), "outbreaks"].to_numpy()
    other = monthly.loc[~monthly["mon"].isin(MONSOON_MONTHS), "outbreaks"].to_numpy()

    _, shapiro_monsoon_p = stats.shapiro(monsoon)
    _, shapiro_other_p = stats.shapiro(other)
    _, levene_p = stats.levene(monsoon, other)

    t_stat, t_p = stats.ttest_ind(monsoon, other, equal_var=False, alternative="greater")
    pooled_sd = np.sqrt(
        ((len(monsoon) - 1) * monsoon.var(ddof=1) + (len(other) - 1) * other.var(ddof=1))
        / (len(monsoon) + len(other) - 2)
    )
    cohens_d = (monsoon.mean() - other.mean()) / pooled_sd

    u_stat, u_p = stats.mannwhitneyu(monsoon, other, alternative="greater")
    rank_biserial = 2 * u_stat / (len(monsoon) * len(other)) - 1

    return {
        "analysis": label,
        "n_monsoon_months": len(monsoon),
        "n_other_months": len(other),
        "monsoon_mean": monsoon.mean(),
        "other_mean": other.mean(),
        "monsoon_median": np.median(monsoon),
        "other_median": np.median(other),
        "monsoon_std": monsoon.std(ddof=1),
        "other_std": other.std(ddof=1),
        "shapiro_monsoon_p": shapiro_monsoon_p,
        "shapiro_other_p": shapiro_other_p,
        "levene_p": levene_p,
        "welch_t": t_stat,
        "welch_p_one_sided": t_p,
        "cohens_d": cohens_d,
        "mannwhitney_U": u_stat,
        "mannwhitney_p_one_sided": u_p,
        "rank_biserial": rank_biserial,
        "reject_H0_welch": t_p < ALPHA,
        "reject_H0_mannwhitney": u_p < ALPHA,
    }


def main():
    df = pd.read_csv(IN_PATH)
    monthly = df.groupby(["year", "mon"]).size().rename("outbreaks").reset_index()

    results = pd.DataFrame([
        run_tests(monthly[~monthly["year"].isin(EXCLUDED_YEARS)],
                  f"main (excl. {', '.join(map(str, EXCLUDED_YEARS))})"),
        run_tests(monthly, "sensitivity (all months)"),
    ])
    results.to_csv(OUT_PATH, index=False)

    pd.set_option("display.width", 200)
    print("H5: monthly outbreak count, monsoon (Jun-Sep) vs. other months, "
          "one-sided\n")
    print(results.set_index("analysis").T.to_string(
        float_format=lambda v: f"{v:.4g}"))
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
