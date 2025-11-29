"""
clean_average_age.py

Reads Average_Age_Per_County.csv and creates a cleaned CSV where
- 'Galway City' + 'Galway County' are averaged and replaced by 'Galway'
- 'Cork City' + 'Cork County' are averaged and replaced by 'Cork'
- 'Dún Laoghaire-Rathdown' + 'Fingal' + 'Dublin City' are averaged and replaced by 'Dublin'

Output: Average_Age_Per_County.cleaned.csv

Usage: python clean_average_age.py
"""

import pandas as pd
import os

INPUT = "Average_Age_Per_County.csv"
OUTPUT = "Average_Age_Per_County.cleaned.csv"

AGG_MAPPING = {
    # new_name: list of names to aggregate
    "Galway": ["Galway County", "Galway City"],
    "Cork": ["Cork County", "Cork City"],
    "Dublin": ["Dún Laoghaire-Rathdown", "Fingal", "Dublin City", "South Dublin"],
    "Waterford": ["Waterford City and County"],
    "Limerick": ["Limerick City and County"],
}

KEY_COLS = ["Statistic Label", "Year", "Sex", "UNIT"]
COUNTY_COL = "County and State"
VALUE_COL = "VALUE"


def load_df(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    # Ensure VALUE is numeric
    df[VALUE_COL] = pd.to_numeric(df[VALUE_COL], errors="coerce")
    return df


def aggregate_and_replace(df: pd.DataFrame) -> pd.DataFrame:
    # We'll collect new rows in a list
    new_rows = []

    # Work on a copy to avoid side effects
    output_df = df.copy()

    for new_name, members in AGG_MAPPING.items():
        # Filter rows that belong to the set of members
        members_mask = output_df[COUNTY_COL].isin(members)
        members_df = output_df[members_mask]

        if members_df.empty:
            # Nothing to do for this mapping
            continue

        # For each KEY_COL grouping we calculate the mean of VALUE for available members
        grouped = (
            members_df
            .groupby(KEY_COLS, as_index=False)[VALUE_COL]
            .mean()
        )

        # Create new rows with COUNTY set to new_name
        for _, row in grouped.iterrows():
            out_row = {col: row[col] for col in KEY_COLS}
            out_row[COUNTY_COL] = new_name
            out_row[VALUE_COL] = row[VALUE_COL]
            new_rows.append(out_row)

        # Remove original member rows from output_df
        output_df = output_df[~members_mask]

    # Append new_rows to output_df (keeping other columns if present)
    if new_rows:
        new_df = pd.DataFrame(new_rows)

        # If there are extra columns in the original, merge on KEY_COLS + COUNTY_COL
        # Keep original other columns where possible by left-merge
        extra_cols = [c for c in output_df.columns if c not in (KEY_COLS + [COUNTY_COL, VALUE_COL])]
        if extra_cols:
            # We'll add those columns with empty/NaN values in the new rows to preserve structure
            for c in extra_cols:
                new_df[c] = pd.NA

        # Reorder columns to match original
        new_df = new_df[output_df.columns]

        # Concat and reset index
        output_df = pd.concat([output_df, new_df], ignore_index=True, sort=False)

    # Sort rows consistently
    sort_cols = KEY_COLS + [COUNTY_COL]
    output_df = output_df.sort_values(sort_cols).reset_index(drop=True)

    return output_df


if __name__ == "__main__":
    print("Loading input CSV:", INPUT)
    df = load_df(INPUT)
    print("Rows loaded:", len(df))

    cleaned = aggregate_and_replace(df)
    print("Rows after cleaning:", len(cleaned))

    print("Writing cleaned CSV:", OUTPUT)
    cleaned.to_csv(OUTPUT, index=False)

    print("Done. Preview of cleaned counties for 2021: \n",
          cleaned[cleaned["Year"] == 2021][[COUNTY_COL, VALUE_COL]].drop_duplicates().head(30))
