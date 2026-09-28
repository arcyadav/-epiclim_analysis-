"""Hypothesis test H4 (see spec.md section 4): diseases have distinct
geographic footprints.

H0: disease type is independent of region.
H1: the disease mix differs by region.

States/UTs are grouped into 6 regions following India's Zonal Councils
(North, Central, East, West, South, Northeast). Runs a chi-square test of
independence on the disease x region table of outbreak record counts, with
Cramer's V as effect size. To show which cells drive the result, it also
reports adjusted standardized residuals: |residual| above the
Bonferroni-corrected critical z (across all cells) marks a cell with
significantly more (+) or fewer (-) outbreaks than independence predicts.

"Other" is excluded: it is a grab-bag of rare/suspected/combo labels, not
one disease, so a geographic footprint for it isn't meaningful.

Input:  data/Final_data_imputed.csv
Output: data/h4_disease_region_observed.csv
        data/h4_disease_region_residuals.csv
"""
import numpy as np
import pandas as pd
from scipy import stats

IN_PATH = "data/Final_data_imputed.csv"
OBSERVED_PATH = "data/h4_disease_region_observed.csv"
RESIDUALS_PATH = "data/h4_disease_region_residuals.csv"

REGIONS = {
    "North": ["Jammu and Kashmir", "Himachal Pradesh", "Punjab", "Haryana",
              "Chandigarh", "Delhi", "Uttarakhand", "Rajasthan"],
    "Central": ["Uttar Pradesh", "Madhya Pradesh", "Chhattisgarh"],
    "East": ["Bihar", "Jharkhand", "Odisha", "West Bengal",
             "Andaman and Nicobar Islands"],
    "West": ["Maharashtra", "Gujarat", "Goa", "Dadra and Nagar Haveli",
             "Daman and Diu"],
    "South": ["Karnataka", "Tamil Nadu", "Kerala", "Andhra Pradesh",
              "Telangana", "Puducherry", "Lakshadweep"],
    "Northeast": ["Assam", "Arunachal Pradesh", "Meghalaya", "Tripura",
                  "Manipur", "Nagaland", "Mizoram", "Sikkim"],
}
REGION_ORDER = list(REGIONS)
DISEASE_ORDER = [
    "Acute Diarrhoeal Disease",
    "Dengue",
    "Chikungunya",
    "Cholera",
    "Malaria",
    "Acute Encephalitis Syndrome",
    "Acute Gastroenteritis",
]
ALPHA = 0.05


def main():
    df = pd.read_csv(IN_PATH)
    state_to_region = {s: r for r, states in REGIONS.items() for s in states}
    df["region"] = df["state_ut"].map(state_to_region)
    unmapped = sorted(df.loc[df["region"].isna(), "state_ut"].unique())
    if unmapped:
        raise ValueError(f"States with no region mapping: {unmapped}")

    df = df[df["Disease"].isin(DISEASE_ORDER)]
    observed = (
        pd.crosstab(df["Disease"], df["region"])
        .reindex(index=DISEASE_ORDER, columns=REGION_ORDER, fill_value=0)
    )
    n = int(observed.to_numpy().sum())
    r, c = observed.shape

    chi2, p, dof, expected = stats.chi2_contingency(observed)
    expected = pd.DataFrame(expected, index=observed.index, columns=observed.columns)
    cramers_v = np.sqrt(chi2 / (n * min(r - 1, c - 1)))
    n_low = int((expected < 5).to_numpy().sum())

    row_share = observed.sum(axis=1).to_numpy()[:, None] / n
    col_share = observed.sum(axis=0).to_numpy()[None, :] / n
    residuals = (observed - expected) / np.sqrt(expected * (1 - row_share) * (1 - col_share))
    z_crit = stats.norm.ppf(1 - ALPHA / (2 * r * c))

    observed.to_csv(OBSERVED_PATH)
    residuals.to_csv(RESIDUALS_PATH)

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print(f"Records tested: {n} ('Other' excluded)\n")
    print("Observed outbreak records (disease x region):\n")
    print(observed.to_string())
    print("\nRow percentages (share of each disease's outbreaks by region):\n")
    print((observed.div(observed.sum(axis=1), axis=0) * 100).round(1).to_string())

    print(f"\nExpected counts < 5: {n_low} of {r * c} cells "
          f"(min expected = {expected.to_numpy().min():.3g})")
    print(f"\nChi-square test of independence: chi2({dof}) = {chi2:.4g}, "
          f"p = {p:.4g}, Cramer's V = {cramers_v:.4f}")
    print(f"Reject H0 at alpha {ALPHA}: {p < ALPHA}")

    print(f"\nAdjusted standardized residuals (|z| > {z_crit:.2f} is significant, "
          f"Bonferroni over {r * c} cells):\n")
    print(residuals.round(1).to_string())

    print(f"\nSaved to {OBSERVED_PATH} and {RESIDUALS_PATH}")


if __name__ == "__main__":
    main()
