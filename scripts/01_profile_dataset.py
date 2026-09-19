"""Profile the raw EpiClim dataset: dtypes, missingness, ranges, unique values.

Input:  data/Final_data.csv
Output: data/dataset_profile.md
"""
import pandas as pd

COLUMN_DESCRIPTIONS = {
    "Unnamed: 0": "Leftover row index from the CSV export; not real data.",
    "week_of_outbreak": "The week of the year (1st-53rd) in which the outbreak was reported.",
    "state_ut": "Indian state or union territory where the outbreak occurred.",
    "district": "District within the state/UT where the outbreak occurred.",
    "Disease": "Name of the disease responsible for the outbreak (e.g. Malaria, Dengue, Cholera).",
    "Cases": "Number of cases reported for that outbreak record.",
    "Deaths": "Number of deaths reported for that outbreak record.",
    "day": "Day-of-month component of the outbreak report date.",
    "mon": "Month component of the outbreak report date.",
    "year": "Year component of the outbreak report date.",
    "Latitude": "Latitude coordinate of the district/location.",
    "Longitude": "Longitude coordinate of the district/location.",
    "preci": "Precipitation (rainfall) measured at the location around the time of the outbreak.",
    "LAI": "Leaf Area Index - a satellite-derived vegetation density measure for the area.",
    "Temp": "Ambient temperature at the location (values suggest degrees Kelvin, ~260-328K).",
}

IN_PATH = "data/Final_data.csv"
OUT_PATH = "data/dataset_profile.md"


def main():
    df = pd.read_csv(IN_PATH)
    n = len(df)

    lines = []
    lines.append("# Dataset Profile: Final_data.csv\n")
    lines.append(f"**Rows:** {n}  \n**Columns:** {df.shape[1]}\n")

    lines.append("## Column Summary\n")
    lines.append("| Column | Dtype | Missing | Missing % | Unique | Min | Max | What it represents |")
    lines.append("|---|---|---|---|---|---|---|---|")

    for col in df.columns:
        s = df[col]
        missing = s.isna().sum()
        missing_pct = round(missing / n * 100, 2)
        nunique = s.nunique(dropna=True)
        dtype = str(s.dtype)
        desc = COLUMN_DESCRIPTIONS.get(col, "")

        if pd.api.types.is_numeric_dtype(s):
            mn = round(s.min(), 4) if pd.notna(s.min()) else ""
            mx = round(s.max(), 4) if pd.notna(s.max()) else ""
        else:
            mn, mx = "", ""

        col_display = col if col.strip() != "" else "(unnamed index)"
        lines.append(f"| {col_display} | {dtype} | {missing} | {missing_pct}% | {nunique} | {mn} | {mx} | {desc} |")

    lines.append("\n## Column Details\n")

    for col in df.columns:
        s = df[col]
        missing = s.isna().sum()
        missing_pct = round(missing / n * 100, 2)
        nunique = s.nunique(dropna=True)
        col_display = col if col.strip() != "" else "(unnamed index)"
        desc = COLUMN_DESCRIPTIONS.get(col, "")

        lines.append(f"### {col_display}")
        if desc:
            lines.append(f"- What it represents: {desc}")
        lines.append(f"- Dtype: `{s.dtype}`")
        lines.append(f"- Missing: {missing} ({missing_pct}%)")
        lines.append(f"- Unique values: {nunique}")

        if pd.api.types.is_numeric_dtype(s):
            desc_stats = s.describe()
            lines.append(f"- Range: {desc_stats.get('min')} to {desc_stats.get('max')}")
            lines.append(
                f"- Mean: {round(desc_stats.get('mean'), 4)}, "
                f"Median: {round(s.median(), 4)}, Std: {round(desc_stats.get('std'), 4)}"
            )
        else:
            vc = s.value_counts(dropna=True)
            if nunique <= 40:
                top_vals = ", ".join(f"{k} ({v})" for k, v in vc.items())
                lines.append(f"- Values (count): {top_vals}")
            else:
                top_vals = ", ".join(f"{k} ({v})" for k, v in vc.head(10).items())
                lines.append(f"- Top 10 values (count): {top_vals}")
        lines.append("")

    dup_count = df.duplicated().sum()
    lines.append(f"## Duplicate Rows\n- Fully duplicated rows: {dup_count}\n")

    lines.append("## Data Quality Notes")
    lines.append(
        "- `Cases` is stored as text (`object`), not numeric, because at least one row has a "
        "non-integer value (e.g. `\"3/1\"`). This blocks direct numeric aggregation until cleaned."
    )
    lines.append(
        "- `Deaths` has substantial missingness - likely means \"no deaths reported\" rather than "
        "true missingness; consider filling with 0 if that assumption holds for this surveillance data."
    )
    lines.append("- `LAI` and `Temp` also have notable missingness worth an explicit imputation strategy.")
    lines.append(
        "- `Unnamed: 0` is a leftover index column from a prior CSV export and duplicates the row "
        "order; it carries no information and can be dropped."
    )

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Profile written to {OUT_PATH} ({n} rows, {df.shape[1]} columns)")


if __name__ == "__main__":
    main()
