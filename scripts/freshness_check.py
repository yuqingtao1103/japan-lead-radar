"""Phase 0 freshness check: how recent are subsidy and certification records in gBizINFO?

Picks 5 companies at random from a gBizINFO search (Kanagawa, companies with subsidy
records) and reports the most recent subsidy year and certification date for each.

Usage:
    .venv/bin/python scripts/freshness_check.py [--prefecture 14] [--seed 42]
"""

import argparse
import os
import random
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lead_radar.gbizinfo import RECORD_URL, GBizInfoClient  # noqa: E402

SOURCE_SUBSIDY = "4"  # gBizINFO `source` code for subsidy records


def load_token() -> str | None:
    secrets_path = ROOT / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with secrets_path.open("rb") as f:
            token = tomllib.load(f).get("GBIZINFO_API_TOKEN")
        if token:
            return token
    return os.environ.get("GBIZINFO_API_TOKEN") or None


def latest(records: list[dict], date_field: str) -> tuple[str, str]:
    """Return (date, title) of the most recent record, or ("No data", "")."""
    dated = [r for r in records if r.get(date_field)]
    if not dated:
        return "No data", ""
    newest = max(dated, key=lambda r: str(r[date_field])[:10])
    return str(newest[date_field])[:10], newest.get("title") or ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefecture", default="14", help="2-digit prefecture code (default 14 Kanagawa)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args()

    token = load_token()
    if not token:
        sys.exit("GBIZINFO_API_TOKEN not found in .streamlit/secrets.toml or the environment.")
    client = GBizInfoClient(token)

    pool = client.search(prefecture=args.prefecture, source=SOURCE_SUBSIDY, limit="500", page="1")
    print(f"Search returned {len(pool)} companies (prefecture={args.prefecture}, has subsidy records).")
    if not pool:
        sys.exit("No companies returned.")
    sample = random.Random(args.seed).sample(pool, min(args.n, len(pool)))

    print()
    print("| Company | Corporate number | Subsidies | Latest subsidy | Certifications | Latest certification | Record |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for company in sample:
        number = company["corporate_number"]
        subsidies = client.category(number, "subsidy")
        certifications = client.category(number, "certification")
        sub_date, sub_title = latest(subsidies, "date_of_approval")
        cert_date, cert_title = latest(certifications, "date_of_approval")
        print(
            f"| {company.get('name')} | {number} | {len(subsidies)} | {sub_date} {sub_title[:40]} "
            f"| {len(certifications)} | {cert_date} {cert_title[:40]} | {RECORD_URL.format(corporate_number=number)} |"
        )


if __name__ == "__main__":
    main()
