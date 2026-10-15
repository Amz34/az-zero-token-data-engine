#!/usr/bin/env python3
"""
Zero-Token Data & Spreadsheet Analytical Engine (Az. consultancy)
Cleans, audits, and summarizes CSV/Excel files locally without sending raw datasets to LLM.
"""
import sys
import os
import json
import argparse

try:
    import pandas as pd
    import openpyxl
except ImportError as e:
    print(json.dumps({"error": f"Missing library: {e}"}))
    sys.exit(1)

def analyze_file(filepath):
    if not os.path.exists(filepath):
        return {"error": f"File not found: {filepath}"}
    
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in ['.xlsx', '.xls']:
            excel = pd.ExcelFile(filepath)
            sheets_summary = {}
            for sheet in excel.sheet_names:
                df = excel.parse(sheet)
                sheets_summary[sheet] = {
                    "rows": int(df.shape[0]),
                    "columns": list(df.columns),
                    "null_counts": {k: int(v) for k, v in df.isnull().sum().to_dict().items() if v > 0},
                    "dtypes": {k: str(v) for k, v in df.dtypes.to_dict().items()},
                    "numeric_summary": df.describe().round(2).to_dict() if not df.select_dtypes(include='number').empty else {}
                }
            return {
                "file": filepath,
                "type": "excel",
                "sheets_count": len(excel.sheet_names),
                "sheets": sheets_summary
            }
        elif ext in ['.csv', '.tsv']:
            sep = '\t' if ext == '.tsv' else ','
            df = pd.read_csv(filepath, sep=sep)
            return {
                "file": filepath,
                "type": "csv",
                "rows": int(df.shape[0]),
                "columns": list(df.columns),
                "null_counts": {k: int(v) for k, v in df.isnull().sum().to_dict().items() if v > 0},
                "numeric_summary": df.describe().round(2).to_dict() if not df.select_dtypes(include='number').empty else {},
                "sample_head": df.head(3).to_dict(orient="records")
            }
        else:
            return {"error": f"Unsupported format: {ext}"}
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Deterministic Zero-Token Data Analyzer")
    parser.add_argument("file", help="Path to Excel (.xlsx) or CSV file")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")
    args = parser.parse_args()

    res = analyze_file(args.file)
    if args.pretty:
        print(json.dumps(res, indent=2))
    else:
        print(json.dumps(res))

if __name__ == "__main__":
    main()
