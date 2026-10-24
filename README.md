# Universal CSV Data Cleaner 2.0

A reusable Python and Pandas tool that cleans, standardizes, validates, and reports issues in CSV datasets.

## Features

- **Duplicate Removal:** Detects and removes duplicate rows.
- **Column Standardization:** Converts column names into consistent formats.
- **Duplicate Column Name Handling:** Makes normalized column names unique.
- **Text Normalization:** Removes unnecessary leading and trailing whitespace.
- **Numeric Conversion:** Converts suitable columns into numeric data types while preserving missing values.
- **Missing-Value Handling:** Applies defined cleaning rules and reports remaining missing values.
- **Date Detection and Conversion:** Detects date-related columns and supports configured date formats.
- **Input Validation:** Handles missing paths, directories, unsupported file types, and empty datasets.
- **Output Protection:** Generates alternative output filenames to avoid overwriting existing files during ordinary sequential runs.
- **Cleaning Reports:** Records row counts, duplicates removed, missing-value counts, detected date columns, and final column names.
- **Error Handling:** Provides useful messages for common input problems.

## Project Structure

```text
fiverr_project_01/
├── input/
│   └── sample_input.csv
├── output/
│   ├── cleaned_data.csv
│   └── cleaning_report.txt
├── src/
│   └── cleaner.py
├── backups/
│   └── cleaner_v1.py
├── portfolio/
├── README.md
└── V2_UPGRADE_PLAN.txt
```

*Note: Some files and folders are created during testing or may vary in your local project.*

## Requirements

- Python 3
- Pandas

Install Pandas:

```bash
pip install pandas
```

## How to Run

From the project root directory, run:

```bash
python src/cleaner.py
```

Enter the path to the CSV file when prompted. The program saves the cleaned dataset and cleaning report in the output directory.

## Cleaning Process

1. Validate the input path and file type.
2. Load the CSV dataset.
3. Check whether the dataset contains usable data.
4. Remove duplicate rows.
5. Standardize column names and resolve naming collisions.
6. Normalize text values.
7. Detect and convert supported date columns.
8. Convert suitable columns to numeric types.
9. Apply missing-value handling rules.
10. Validate the cleaned dataset.
11. Save the cleaned CSV and generate a report.

## Example Use Case

A business has a CSV file containing inconsistent column names, duplicate records, unnecessary whitespace, missing values, and date columns.

This tool helps standardize the dataset and produces a cleaning report so the user can review the results before further analysis.

## Date-Handling Notes

The cleaner supports configured date formats, including:

- ISO format: `2026-01-05`
- Day-first slash format: `05/01/2026`
- Day-first hyphen format: `05-01-2026`

Slash-separated dates can be ambiguous. For example, `03/04/2026` could mean 3 April or March 4, depending on the convention. The current configuration interprets it as 3 April.

Review dates and missing values before using cleaned data for important decisions.

## Limitations

- Designed for CSV files; Excel support is not claimed.
- Date conversion depends on supported formats and the date-column detection rules.
- Numeric conversion uses heuristics and may require review for mixed text-and-number columns.
- Missing values may remain when the cleaning rules do not safely fill them.
- The tool does not replace manual review or domain-specific data validation.

## Technologies

- Python
- Pandas
- Regular expressions
- `pathlib`

## Author

Personal portfolio project.