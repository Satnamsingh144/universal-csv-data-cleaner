# from pathlib import Path

# file_path = Path(r"C:\Users\MSI\fiverr_project_01\input\sales_messy.csv")

# data = """Customer Name,City,Product,Quantity,Price,Sale Date
# Rahul,Delhi,Laptop,2,55000,2026-01-05
# Aman,Mumbai,Mouse,5,500,2026-01-06
# Simran,Delhi,Keyboard,3,1200,2026-01-07
# Rahul,Delhi,Laptop,2,55000,2026-01-05
# Priya,,Monitor,1,15000,2026-01-08
# Aman,Mumbai,Mouse,,500,2026-01-09
# Karan,Chandigarh,Keyboard,2,,2026-01-10
# Simran,Delhi,,3,1200,2026-01-11
# Priya,,Monitor,1,15000,2026-01-08
# """

# # Make sure the input folder exists
# file_path.parent.mkdir(parents=True, exist_ok=True)

# # Create and write the CSV file
# file_path.write_text(data, encoding="utf-8")

# print("✅ sales_messy.csv created successfully!")
# print(f"📁 Location: {file_path}")
from pathlib import Path

# Main location
base_path = Path(r"C:\Users\MSI")

# Project folder
project = base_path / "portfolio_project_01"

# Create folder
project.mkdir(exist_ok=True)

# Create files
files = {
    "README.md": "# Portfolio Project 01\n\nData Cleaning Project",
    "sample_input.csv": "",
    "sample_output.csv": "",
    "cleaning_report.txt": ""
}

for filename, content in files.items():
    file_path = project / filename
    file_path.write_text(content, encoding="utf-8")

print("✅ Project created successfully!")
print(f"📁 Location: {project}")

# Show structure
print("\nProject Structure:")
for item in project.iterdir():
    print(f"├── {item.name}")