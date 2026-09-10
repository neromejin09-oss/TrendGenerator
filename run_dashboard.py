import time
from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.chart import LineChart, Reference

EXTRACT_DIR = Path("extract")
BOARD_DIR = Path("board")


def create_dashboards():
    BOARD_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    xlsx_files = sorted(list(EXTRACT_DIR.glob("*.xlsx")))

    if not xlsx_files:
        print(f"⚠️ No processed files found in directory '{EXTRACT_DIR.resolve()}'.")
        return

    print(f"🚀 Generating dashboards for {len(xlsx_files)} file(s)...\n")
    start_time = time.time()

    for file_path in xlsx_files:
        print(f"📄 Generating dashboard for: {file_path.name} ...")
        t0 = time.time()
        try:
            wb = openpyxl.load_workbook(file_path)
            
            # Select cleaned data or default worksheet
            ws_name = "Cleaned_Data" if "Cleaned_Data" in wb.sheetnames else wb.sheetnames[0]
            ws = wb[ws_name]

            # Read sheet using Pandas for statistics calculations
            df = pd.read_excel(file_path, sheet_name=ws_name)
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

            # Create or overwrite Dashboard Sheet
            if "Dashboard" in wb.sheetnames:
                del wb["Dashboard"]
            ws_dash = wb.create_sheet(title="Dashboard", index=0)

            # Write Summary Statistics Cards
            ws_dash["A1"] = "Metric Summary"
            ws_dash["A2"] = "Column Name"
            ws_dash["B2"] = "Count"
            ws_dash["C2"] = "Average"
            ws_dash["D2"] = "Max"
            ws_dash["E2"] = "Min"

            row_idx = 3
            for col in numeric_cols:
                ws_dash[f"A{row_idx}"] = col
                ws_dash[f"B{row_idx}"] = len(df[col].dropna())
                ws_dash[f"C{row_idx}"] = round(df[col].mean(), 2) if not df[col].empty else 0
                ws_dash[f"D{row_idx}"] = round(df[col].max(), 2) if not df[col].empty else 0
                ws_dash[f"E{row_idx}"] = round(df[col].min(), 2) if not df[col].empty else 0
                row_idx += 1

            # Render Line Charts for numeric columns
            chart_start_row = row_idx + 2
            if numeric_cols and ws.max_row > 1:
                chart = LineChart()
                chart.title = "Numeric Trends Analysis"
                chart.style = 13
                chart.y_axis.title = "Values"
                chart.x_axis.title = "Index"

                data_ref = Reference(ws, min_col=2, min_row=1, max_col=len(numeric_cols)+1, max_row=ws.max_row)
                chart.add_data(data_ref, titles_from_data=True)

                ws_dash.add_chart(chart, f"A{chart_start_row}")

            out_path = BOARD_DIR / file_path.name
            wb.save(out_path)
            print(f"  └─ ✅ Dashboard generated -> board/{out_path.name} (Time: {time.time() - t0:.2f}s)")

        except Exception as e:
            print(f"  └─ ❌ Dashboard creation failed: {e}")

    print(f"\n🎉 All dashboards generated successfully! Total time: {time.time() - start_time:.2f}s")


if __name__ == "__main__":
    create_dashboards()