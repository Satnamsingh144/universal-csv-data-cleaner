import pandas as pd
import re
from pathlib import Path


# -----------------------------
# 1. LOAD DATA
# -----------------------------

def load_data(file_path):

    try:
        return pd.read_csv(file_path)

    except FileNotFoundError:
        print("\nERROR: The input file was not found.")
        return None

    except Exception as e:
        print(f"\nERROR: Could not read the file: {e}")
        return None

def get_unique_output_path(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        return file_path

    counter = 1

    while True:
        new_path = file_path.with_name(
            f"{file_path.stem}_{counter}{file_path.suffix}"
        )

        if not new_path.exists():
            return new_path

        counter += 1

# -----------------------------
# 2. CLEAN COLUMN NAMES
# -----------------------------

def clean_column_names(df):
    new_columns = []

    for column in df.columns:
        column = str(column).strip().lower()
        column = re.sub(r"[^a-z0-9]+", "_", column)
        column = column.strip("_")

        new_columns.append(column)

    df.columns = new_columns

    return df

def normalize_text_values(df):
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    return df

def make_column_names_unique(df):
    columns = []
    seen = {}

    for column in df.columns:
        if column not in seen:
            seen[column] = 0
            columns.append(column)
        else:
            seen[column] += 1
            new_column = f"{column}_{seen[column]}"

            while new_column in seen:
                seen[column] += 1
                new_column = f"{column}_{seen[column]}"

            seen[new_column] = 0
            columns.append(new_column)

    df.columns = columns
    return df


# -----------------------------
# 3. DETECT DATE COLUMNS
# -----------------------------


def convert_date_columns(df):

    date_keywords = [
        "date",
        "time",
        "created",
        "updated",
        "birth",
        "dob"
    ]

    date_formats = [
        "%Y-%m-%d",  # ISO: 2026-01-05
        "%d/%m/%Y",  # Indian: 05/01/2026
        "%d-%m-%Y"   # Indian: 05-01-2026
    ]

    date_columns = []

    for column in df.columns:

        column_name = column.lower()

        if any(keyword in column_name for keyword in date_keywords):

            original = df[column]
            non_empty = original.notna() & original.astype("string").str.strip().ne("")
            non_empty_count = non_empty.sum()

            if non_empty_count == 0:
                continue

            converted = pd.Series(
                pd.NaT,
                index=df.index,
                dtype="datetime64[ns]"
            )

            remaining = non_empty.copy()

            for date_format in date_formats:

                parsed = pd.to_datetime(
                    original[remaining],
                    errors="coerce",
                    format=date_format
                )

                valid = parsed.notna()

                converted.loc[parsed.index[valid]] = parsed[valid]
                remaining.loc[parsed.index[valid]] = False

            valid_count = converted[non_empty].notna().sum()

            if valid_count / non_empty_count >= 0.8:
                df[column] = converted
                date_columns.append(column)

    return df, date_columns



# -----------------------------
# 4. HANDLE MISSING VALUES
# -----------------------------


def handle_missing_values(df):
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            # Do not guess missing dates.
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            # Preserve missing numeric values until a safe
            # replacement rule is chosen.
            continue

        # Fill missing text values with a clear placeholder.
        df[column] = df[column].fillna("Unknown")

    return df



# -----------------------------
# 5. FIX NUMERIC TYPES
# -----------------------------

def fix_numeric_types(df):
    for column in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            continue

        original = df[column]
        cleaned = (
            original.astype("string")
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        converted = pd.to_numeric(cleaned, errors="coerce")
        non_empty = original.notna() & cleaned.ne("")
        non_empty_count = non_empty.sum()

        if non_empty_count == 0:
            continue

        valid_count = converted[non_empty].notna().sum()
        numeric_ratio = valid_count / non_empty_count

        # Convert only when at least 80% of non-empty values are numeric.
        if numeric_ratio >= 0.6:
            df[column] = converted

            non_missing = converted.dropna()
            if len(non_missing) > 0 and (non_missing % 1 == 0).all():
                df[column] = df[column].astype("Int64")

    return df

# -----------------------------
# 6. VALIDATE DATA
# -----------------------------

def validate_data(df):

    duplicate_count = df.duplicated().sum()
    missing_count = df.isna().sum().sum()

    print("\n--- VALIDATION ---")
    print("Duplicate rows:", duplicate_count)
    print("Total missing values:", missing_count)
    print("Total rows:", len(df))
    print("Total columns:", len(df.columns))

    return duplicate_count, missing_count


# -----------------------------
# 7. CREATE REPORT
# -----------------------------

def create_report(
    original_rows,
    final_rows,
    duplicates_removed,
    missing_before,
    missing_after,
    date_columns,
    df
):
    rows_removed = original_rows - final_rows

    report = f"""
UNIVERSAL CSV CLEANER 2.0
DATA CLEANING REPORT
====================

1. CLEANING SUMMARY
-------------------
Original rows: {original_rows}
Final rows: {final_rows}
Rows removed: {rows_removed}
Duplicate rows removed: {duplicates_removed}

2. MISSING VALUES
-----------------
Missing values before cleaning: {missing_before}
Missing values after cleaning: {missing_after}

3. MISSING VALUES BY COLUMN
---------------------------
"""

    missing_by_column = df.isna().sum()
    columns_with_missing = missing_by_column[missing_by_column > 0]

    if columns_with_missing.empty:
        report += "- No missing values found\n"
    else:
        for column, count in columns_with_missing.items():
            report += f"- {column}: {count}\n"

    report += """
4. DATE DETECTION
-----------------
"""

    if date_columns:
        for column in date_columns:
            report += f"- {column}\n"
    else:
        report += "- No date columns detected\n"

    report += """
5. FINAL COLUMN NAMES
---------------------
"""

    for column in df.columns:
        report += f"- {column}\n"

    report += """
6. NOTES
--------
- Review the cleaned data before using it for important decisions.
- Missing values may remain when they cannot be safely filled.
- Date detection depends on column names and supported date formats.
"""

    return report





# -----------------------------
# 8. MAIN PROGRAM
# -----------------------------

def main():

    raw_input_path = input("Enter input CSV file path: ").strip()

    if not raw_input_path:
        print("\nERROR: Please enter a file path.")
        return

    input_path = Path(raw_input_path)

    if not input_path.exists():
        print("\nERROR: The input path does not exist.")
        return

    if not input_path.is_file():
        print("\nERROR: The input path is not a file.")
        return

    if input_path.suffix.lower() != ".csv":
        print("\nERROR: Please provide a CSV file.")
        return

    output_path = get_unique_output_path(
        Path("output") / f"{input_path.stem}_cleaned.csv"
    )

    report_path = get_unique_output_path(
        Path("output") / f"{input_path.stem}_cleaning_report.txt"
    )

    print("================================")
    print("       UNIVERSAL CSV CLEANER")
    print("================================")

    # Load
    df = load_data(input_path)

    if df is None:
        return

    if df.empty:
        print("\nERROR: The CSV file is empty.")
        return

    if len(df.columns) == 0:
        print("\nERROR: The CSV file has no columns.")
        return

    original_rows = len(df)

    print("\nOriginal rows:", original_rows)
    print("Original columns:", len(df.columns))

    # Missing values before cleaning
    missing_before = df.isna().sum().sum()

    # Remove duplicates
    duplicates_removed = df.duplicated().sum()
    df = df.drop_duplicates()

    # Clean column names
    df = clean_column_names(df)
    df = make_column_names_unique(df)
    df = normalize_text_values(df)

    # Detect dates
    df, date_columns = convert_date_columns(df)

    # Fix numeric types
    df = fix_numeric_types(df)


    # Handle missing values
    df = handle_missing_values(df)


    # Validate
    duplicate_count, missing_after = validate_data(df)

    # Create output folder if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Save cleaned CSV
    df.to_csv(output_path, index=False)

    # Create report
    report = create_report(
        original_rows,
        len(df),
        duplicates_removed,
        missing_before,
        missing_after,
        date_columns,
        df
    )

    report_path.write_text(report, encoding="utf-8")

    print("\n--- OUTPUT ---")
    print("Cleaned file:", output_path)
    print("Report file:", report_path)

    print("\n--- FINAL DATA ---")
    print(df)

    print("\nCleaning completed successfully!")


if __name__ == "__main__":
    main()

#C:\Users\MSI\fiverr_project_01\input\sales_messy.csv
