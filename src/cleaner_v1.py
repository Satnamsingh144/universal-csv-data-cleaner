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

    date_columns = []

    for column in df.columns:

        column_name = column.lower()

        if any(keyword in column_name for keyword in date_keywords):

            converted = pd.to_datetime(
                    df[column],
                    errors="coerce",
                    format="mixed"
                )

            non_empty = df[column].notna().sum()

            if non_empty > 0:

                valid_dates = converted.notna().sum()

                if valid_dates / non_empty >= 0.8:
                    df[column] = converted
                    date_columns.append(column)

    return df, date_columns


# -----------------------------
# 4. HANDLE MISSING VALUES
# -----------------------------

def handle_missing_values(df):

    for column in df.columns:

        if pd.api.types.is_numeric_dtype(df[column]):

            df[column] = df[column].fillna(0)

        elif pd.api.types.is_datetime64_any_dtype(df[column]):

            # Keep missing dates as missing
            # because we cannot safely guess a date
            pass

        else:

            df[column] = df[column].fillna("Unknown")

    return df


# -----------------------------
# 5. FIX NUMERIC TYPES
# -----------------------------

def fix_numeric_types(df):

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[column]):
            continue

        converted = pd.to_numeric(df[column], errors="coerce")

        original_non_empty = df[column].notna().sum()
        valid_numeric = converted.notna().sum()

        if original_non_empty > 0:

            numeric_ratio = valid_numeric / original_non_empty

            if numeric_ratio >= 0.8:
                df[column] = converted

                if (df[column].dropna() % 1 == 0).all():
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

    report = f"""
DATA CLEANING REPORT
====================

Original rows: {original_rows}
Final rows: {final_rows}

Duplicate rows removed: {duplicates_removed}

Missing values before cleaning: {missing_before}
Missing values after cleaning: {missing_after}

Detected date columns:
"""

    if date_columns:
        for column in date_columns:
            report += f"- {column}\n"
    else:
        report += "- None\n"

    report += """
Final columns:
"""

    for column in df.columns:
        report += f"- {column}\n"

    return report


# -----------------------------
# 8. MAIN PROGRAM
# -----------------------------

def main():

    input_path = Path(input("Enter input CSV file path: ").strip())

    output_path = Path("output/cleaned_data.csv")
    report_path = Path("output/cleaning_report.txt")

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
