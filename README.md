# Japan B2B Lead Radar

**Which Japanese companies should a foreign B2B company contact first, and why?**

Japan B2B Lead Radar builds a pool of candidate companies from Japanese government open data and scores each one on fit with an ideal customer profile (ICP) and on buying signals. It explains every score, drafts account briefs and outreach for the top leads, and exports the list to a CRM.

Demo scenario: a US software company selling an AI-powered inventory management tool to mid-size manufacturers in the Kanto region.

**Core promise:** every signal shown has a source, a date, and a link to the source record. The app never invents facts about a company. Missing values are shown as "No data".

> Status: Phase 0 (setup and data check). Live demo link and screenshots will be added once the app is deployed.

## Target user

Sales and business-development teams at foreign B2B companies entering Japan, who need a short, defensible list of accounts to approach first.

## Data sources

| Layer | Source | Freshness | What it tells a salesperson |
| --- | --- | --- | --- |
| Fresh | National Tax Agency corporate number data (法人番号公表サイト) | Daily diffs on business days | Newly established, relocated, or renamed companies |
| Recent | EDINET annual securities reports (listed companies) | Filed mostly in June | Current priorities and pain points |
| Background | gBizINFO REST API v2 (METI) | Daily to yearly, depending on the original source | Subsidies, certifications, procurement, size |

Attribution:

- 出典：「Gビズインフォ」（経済産業省）(https://info.gbiz.go.jp/) を加工して作成
- 出典：国税庁法人番号公表サイト（国税庁）(https://www.houjin-bangou.nta.go.jp/) を加工して作成
- 出典：EDINET閲覧（提出）サイト (https://disclosure2.edinet-fsa.go.jp/) をもとに作成、PDL1.0

API details, terms, and the freshness check are in [docs/data-source-notes.md](docs/data-source-notes.md).

## Run locally

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then add your gBizINFO token
.venv/bin/streamlit run app.py
```

## How scoring works

Coming in Phase 2.

## How AI output is constrained

Coming in Phase 3.

## Validation

Coming in Phase 5.

## Known limitations

- **gBizINFO**
  - Covers only companies with administrative-procedure records.
  - Updates are not real-time.
  - It has no phone numbers.
  - It has no revenue time series except for EDINET filers.
  - Search cannot filter by industry, so industry is filtered from each company's detail record.
- **EDINET**
  - Covers listed and other reporting companies only.
- **NTA corporate number data**
  - Contains only name, address, and change history.
  - The downloadable diff files cover about the last two months.
