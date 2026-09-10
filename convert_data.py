import time
from pathlib import Path
import pandas as pd

INPUT_DIR = Path("input")
CONVERT_DIR = Path("convert")


def find_header_line(file_path, max_check_lines=100):
    """Detect metadata header rows to locate actual table header."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(max_check_lines)]

        comma_counts = [line.count(",") for line in lines]
        if not comma_counts:
            return 0

        max_commas = max(comma_counts)
        for idx, count in enumerate(comma_counts):
            if count >= max_commas * 0.8 and count > 0:
                return idx
    except Exception:
        pass
    return 0


def process_csv_files():
    CONVERT_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_files_set = set(INPUT_DIR.glob("*.csv")).union(set(INPUT_DIR.glob("*.CSV")))
    csv_files = sorted(list(csv_files_set))

    if not csv_files:
        print(f"⚠️ No CSV files found in directory '{INPUT_DIR.resolve()}'.")
        return

    print(f"🚀 Found {len(csv_files)} CSV file(s). Starting conversion...\n")
    start_total_time = time.time()

    for file_path in csv_files:
        print(f"📄 Converting: {file_path.name} ...")
        t0 = time.time()
        try:
            skip_rows = find_header_line(file_path)

            # Read raw data without filtering
            df = pd.read_csv(
                file_path,
                skiprows=skip_rows,
                float_precision="round_trip",
                low_memory=False,
            )

            convert_path = CONVERT_DIR / f"{file_path.stem}.xlsx"

            # Save raw sheet
            with pd.ExcelWriter(convert_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Raw_Data", index=False)

            print(f"  └─ ✅ Converted -> convert/{convert_path.name} (Sheet: Raw_Data | Time: {time.time() - t0:.2f}s)")

        except Exception as e:
            print(f"  └─ ❌ Conversion failed: {e}")

    print(f"\n🎉 All conversions completed! Total time: {time.time() - start_total_time:.2f}s")


if __name__ == "__main__":
    process_csv_files()