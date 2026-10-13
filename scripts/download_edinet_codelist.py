"""Download the official EDINET code list (EdinetcodeDlInfo.csv) and save it as Parquet.

Source: https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip
(stable link documented in the EDINET API specification). Terms: PDL1.0.

Usage:
    .venv/bin/python scripts/download_edinet_codelist.py
"""

import io
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "edinet"
OUT_PATH = ROOT / "data" / "edinet_codelist.parquet"
URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
CSV_NAME = "EdinetcodeDlInfo.csv"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=60) as response:
        payload = response.read()
    zip_path = RAW_DIR / f"Edinetcode_{date.today():%Y%m%d}.zip"
    zip_path.write_bytes(payload)

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        raw_csv = archive.read(CSV_NAME)

    # Row 1 holds the download date and record count; column headers are on row 2.
    first_line = raw_csv.split(b"\n", 1)[0].decode("cp932").strip()
    df = pd.read_csv(io.BytesIO(raw_csv), encoding="cp932", skiprows=1, dtype=str)
    df.attrs["source_header"] = first_line
    df["source_url"] = URL
    df["retrieved_on"] = date.today().isoformat()
    df.to_parquet(OUT_PATH, index=False)

    print(f"Header line: {first_line}")
    print(f"Saved {len(df):,} rows to {OUT_PATH.relative_to(ROOT)}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    sys.exit(main())
