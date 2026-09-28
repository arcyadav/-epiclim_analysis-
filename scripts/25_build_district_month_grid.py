"""Build the district x month grid for the outbreak model (see spec.md
section 6).

The dataset only contains outbreak records, so "no outbreak" rows have to
be constructed: every district gets one row per calendar month in the data
range, with outbreak = 1 if any disease outbreak was recorded there that
month, else 0. A missing record is assumed to mean no outbreak (it could
also mean no report -- a stated modeling assumption).

Steps:
  1. Canonicalize district names: fix spelling/case/punctuation variants
     within a state, plus a few manual merges (see DISTRICT_ALIASES).
  2. Build the full grid for all districts (restricting to districts seen
     in the training period is done in the training script).
  3. Climate features: rainfall and temperature exist only on outbreak
     rows, so each cell gets its *region's* mean for that month, computed
     from measured (non-imputed) values -- lag 0 and lag 1. Region-months
     with no records stay NaN and are filled in the training script from
     training-period climatology.
  4. District-history features, using only months before t: outbreak last
     month, same month last year, count in the previous 12 months, and
     the district's expanding historical outbreak rate.

Input:  data/Final_data_imputed.csv
Output: data/district_month_grid.csv
"""
import numpy as np
import pandas as pd

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/district_month_grid.csv"

# Same Zonal-Council grouping as 23_h4_disease_region_test.py
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
# (state, normalized name) -> (state, normalized name), applied after
# lowercasing and stripping non-letters. Covers variants that normalization
# alone doesn't merge.
DISTRICT_ALIASES = {
    ("Assam", "karbianglongdiphu"): ("Assam", "karbianglong"),
    # Rangareddy moved to Telangana when the state was formed in 2014
    ("Andhra Pradesh", "rangareddy"): ("Telangana", "rangareddy"),
}


def canonical_districts(df):
    norm = df["district"].str.lower().str.replace(r"[^a-z]", "", regex=True)
    keys = [DISTRICT_ALIASES.get((s, n), (s, n)) for s, n in zip(df["state_ut"], norm)]
    df = df.copy()
    df["state_ut"] = [k[0] for k in keys]
    df["district_key"] = [f"{s}|{n}" for s, n in keys]
    # Display name: the most common original spelling for each key
    display = (df.groupby("district_key")["district"]
               .agg(lambda s: s.value_counts().index[0]))
    df["district"] = df["district_key"].map(display)
    return df


def main():
    df = pd.read_csv(IN_PATH)
    n_raw = df.groupby(["state_ut", "district"]).ngroups
    df = canonical_districts(df)
    state_to_region = {s: r for r, states in REGIONS.items() for s in states}
    df["region"] = df["state_ut"].map(state_to_region)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))
    print(f"Districts: {n_raw} raw state+district names -> "
          f"{df['district_key'].nunique()} after canonicalizing")

    districts = (df.groupby("district_key")
                 .agg(state_ut=("state_ut", "first"), district=("district", "first"),
                      region=("region", "first"),
                      Latitude=("Latitude", "mean"), Longitude=("Longitude", "mean"))
                 .reset_index())
    months = pd.date_range(df["date"].min(), df["date"].max(), freq="MS")
    grid = (districts.merge(pd.DataFrame({"date": months}), how="cross")
            .sort_values(["district_key", "date"]).reset_index(drop=True))
    grid["year"] = grid["date"].dt.year
    grid["mon"] = grid["date"].dt.month

    positives = df[["district_key", "date"]].drop_duplicates().assign(outbreak=1)
    grid = grid.merge(positives, on=["district_key", "date"], how="left")
    grid["outbreak"] = grid["outbreak"].fillna(0).astype(int)

    # Region x month climate from measured values only
    climate = pd.concat([
        df[~df["preci_imputed"].astype(bool)].groupby(["region", "date"])["preci"].mean(),
        df[~df["Temp_imputed"].astype(bool)].groupby(["region", "date"])["Temp"].mean(),
    ], axis=1)
    full_index = pd.MultiIndex.from_product([list(REGIONS), months], names=["region", "date"])
    climate = climate.reindex(full_index).rename(
        columns={"preci": "region_preci", "Temp": "region_temp"})
    climate["region_preci_lag1"] = climate.groupby(level="region")["region_preci"].shift(1)
    climate["region_temp_lag1"] = climate.groupby(level="region")["region_temp"].shift(1)
    grid = grid.merge(climate.reset_index(), on=["region", "date"], how="left")
    missing = climate["region_preci"].isna().sum()
    print(f"Region-months with no rainfall value: {missing} of {len(climate)}")

    # District history -- shift(1) so month t only sees months < t
    by_district = grid.groupby("district_key")["outbreak"]
    grid["prev_month_outbreak"] = by_district.shift(1)
    grid["same_month_last_year"] = by_district.shift(12)
    grid["outbreaks_prev_12m"] = by_district.transform(
        lambda s: s.shift(1).rolling(12, min_periods=1).sum())
    grid["hist_outbreak_rate"] = by_district.transform(
        lambda s: s.shift(1).expanding().mean())

    grid = grid.drop(columns="date")
    grid.to_csv(OUT_PATH, index=False)
    print(f"Grid: {len(grid)} rows ({grid['district_key'].nunique()} districts x "
          f"{len(months)} months), {grid['outbreak'].sum()} positive "
          f"({grid['outbreak'].mean():.2%})")
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
