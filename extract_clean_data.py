import time
from pathlib import Path
import pandas as pd
import openpyxl

CONVERT_DIR = Path("convert")
EXTRACT_DIR = Path("extract")


def clean_and_extract_data():
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    CONVERT_DIR.mkdir(parents=True, exist_ok=True)

    xlsx_files = sorted(list(CONVERT_DIR.glob("*.xlsx")))

    if not xlsx_files:
        print(f"⚠️ No XLSX files found in directory '{CONVERT_DIR.resolve()}'.")
        return

    print(f"🚀 Found {len(xlsx_files)} Excel file(s). Processing data extraction and cleaning...\n")
    start_time = time.time()

    for file_path in xlsx_files:
        print(f"📄 Processing: {file_path.name} ...")
        t0 = time.time()
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet_name = wb.sheetnames[0]
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Drop completely empty rows and columns
            df_cleaned = df.dropna(how="all").dropna(how="all", axis=1)

            # Save cleaned data to a new sheet without corrupting the original sheet
            output_path = EXTRACT_DIR / file_path.name
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Raw_Data", index=False)
                df_cleaned.to_excel(writer, sheet_name="Cleaned_Data", index=False)

            print(f"  └─ ✅ Cleaned & Extracted -> extract/{output_path.name} (Time: {time.time() - t0:.2f}s)")

        except Exception as e:
            print(f"  └─ ❌ Data processing failed: {e}")

    print(f"\n🎉 Data extraction & cleaning completed! Total time: {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    clean_and_extract_data()