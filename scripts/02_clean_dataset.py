"""Clean the raw EpiClim dataset.

Steps:
  1. Drop the leftover `Unnamed: 0` index column.
  2. Disease: keep the 7 well-populated categories, bucket everything else as "Other".
  3. Cases: drop the one row with a non-numeric value ("3/1"), cast the rest to int.
  4. Deaths: fill missing values with 0 (assumed "no deaths reported").
  5. Temp: convert Kelvin -> Celsius.
  6. week_of_outbreak: extract the plain integer week number (e.g. "1st week" -> 1).

Input:  data/Final_data.csv
Output: data/Final_data_cleaned.csv
"""
import pandas as pd

IN_PATH = "data/Final_data.csv"
OUT_PATH = "data/Final_data_cleaned.csv"

KEEP_DISEASES = {
    "Acute Diarrhoeal Disease",
    "Dengue",
    "Chikungunya",
    "Cholera",
    "Malaria",
    "Acute Encephalitis Syndrome",
    "Acute Gastroenteritis",
}


def main():
    df = pd.read_csv(IN_PATH)
    print("Before:", df.shape)

    df = df.drop(columns=["Unnamed: 0"])

    df["Disease"] = df["Disease"].where(df["Disease"].isin(KEEP_DISEASES), "Other")

    bad_mask = pd.to_numeric(df["Cases"], errors="coerce").isna()
    if bad_mask.any():
        print("Dropping rows with non-numeric Cases:", df.loc[bad_mask, "Cases"].tolist())
    df = df.loc[~bad_mask].copy()
    df["Cases"] = pd.to_numeric(df["Cases"]).astype(int)

    df["Deaths"] = df["Deaths"].fillna(0)

    df["Temp"] = df["Temp"] - 273.15

    df["week_of_outbreak"] = df["week_of_outbreak"].str.extract(r"(\d+)").astype(int)

    print("After:", df.shape)
    df.to_csv(OUT_PATH, index=False)
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
