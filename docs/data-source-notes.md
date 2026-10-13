# Data source notes

Reviewed on 2026-10-12 from official documentation only. Items marked **Not confirmed** must be checked against a real API response before code depends on them.

## Summary

| | gBizINFO REST API v2 | NTA corporate number data | EDINET API v2 |
| --- | --- | --- | --- |
| Publisher | METI (経済産業省) | National Tax Agency (国税庁) | Financial Services Agency (金融庁) |
| Access | Free token, apply online | Downloads: no registration. Web-API: free application ID (2 weeks to 1 month) | Free Subscription-Key; signup needs email, password, phone MFA |
| License | 政府標準利用規約 2.0 (CC BY 4.0 compatible), commercial use allowed | PDL1.0 (CC BY 4.0 compatible) | PDL1.0 (CC BY 4.0 compatible) |
| Rate limit | No stated cap; restriction guideline around 200,000 requests/hour | No number published; HTTP 403 on heavy access | No number published; HTTP 429 on heavy access |
| Company size / industry | Yes, per-company detail only | No | Code list has listing status, industry, capital |
| Record link | `https://info.gbiz.go.jp/hojin/ichiran?hojinBango={number}` | `https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html?selHouzinNo={number}` | `https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?{docID}` |

All three record-link patterns work, but none is formally documented as a permanent link.

---

## 1. gBizINFO REST API v2

### Access
- Base URL: `https://api.info.gbiz.go.jp/hojin/v2/hojin`. No trailing slash; a trailing `/` returns HTTP 500.
- Authentication: header `X-hojinInfo-api-token`.
- Token application: https://info.gbiz.go.jp/hojin/various_registration/form. The token is shown via a link in the confirmation email.
- Our secret name: `GBIZINFO_API_TOKEN` in `.streamlit/secrets.toml`.
- Errors: 400 bad parameter, 401 missing or invalid token, 404 no data.
- Sources: OpenAPI spec https://api.info.gbiz.go.jp/hojin/v3/api-docs/v2 ; https://content.info.gbiz.go.jp/api/index.html

### Endpoints (all GET)
- `/v2/hojin`: search.
- `/v2/hojin/{corporate_number}`: basic info for one company.
- `/v2/hojin/{corporate_number}/{certification|commendation|corporation|finance|patent|procurement|subsidy|workplace}`: one category for one company.
- `/v2/hojin/updateInfo[/{category}]?from=yyyyMMdd&to=yyyyMMdd&page=`: records changed in a date range.
  - `updateInfo/corporation` was switched off on 2026-07-31.
- Every endpoint accepts `metadata_flg=true` to return source and update metadata.

### Search filters (`/v2/hojin`)

| Need | Parameter | Supported? |
| --- | --- | --- |
| Prefecture | `prefecture`: 2-digit local government code. Kanto: 08 Ibaraki, 09 Tochigi, 10 Gunma, 11 Saitama, 12 Chiba, 13 Tokyo, 14 Kanagawa | Yes. Multiple values **not confirmed**, so query one prefecture at a time |
| City | `city`: digits 3-5 of the local government code. For designated cities, use the ward | Yes |
| Employee count | `employee_number_from`, `employee_number_to` | Yes, as a range |
| Capital | `capital_stock_from`, `capital_stock_to` (yen) | Yes, as a range |
| Industry | none | **No.** Industry exists only in per-company detail (`industry`, JSIC codes), so we filter on our side |
| Business keyword | none. `name` is a partial match on the company name only | **No** |
| Other filters | `corporate_type`, `founded_year`, `exist_flg`, `source` (1 procurement, 2 commendation, 3 certification, 4 subsidy, 5 patent, 6 finance), `ministry`, `subsidy` / `certification` / `procurement` / `patent` (title partial match), amount ranges, sales and asset ranges, workplace bands | Yes |
| Paging | `page` (1-10), `limit` (0-5000, default 1000) | Probable maximum is 50,000 rows per query (inferred, not stated) |

Search results are thin. They contain only `corporate_number`, `name`, `name_en`, `location`, `postal_code`, `status`, `update_date`, `number_of_activity` and `meta-data`. Size, industry and signals need one detail call per company. For a large pool, the official bulk download at https://info.gbiz.go.jp/hojin/DownloadTop, updated roughly daily, is the recommended alternative.

### Response fields we plan to use
- **Basic info:** `corporate_number`, `name`, `name_en`, `location`, `postal_code`, `status`, `kind`, `capital_stock`, `employee_number`, `founding_year`, `date_of_establishment`, `business_summary`, `company_url`, `industry[]`, `business_items[]`, `update_date`.
  - `representative_name` is an individual's name. We drop it (CLAUDE.md rule 7).
- **Subsidy:** `date_of_approval`, `title`, `amount` (returned as a string), `target`, `government_departments`.
- **Certification:** `date_of_approval`, `title`, `category`, `target`, `government_departments`.
- **Commendation:** `date_of_commendation`, `title`, `category`, `target`, `government_departments`, `note`.
- **Procurement:** `date_of_order`, `title`, `amount` (integer), `government_departments`, `note`.
- **Finance:** `management_index[]` with `period`, `net_sales_summary_of_business_results`, `number_of_employees`, and more. Available only for EDINET filers.
- **Metadata (`metadata_flg=true`):** `data_quality` (government-approved or self-reported), `source`, `import_frequency`, `last_acquisition_date`, `last_update_date`.
- **Date format in API responses:** **Not confirmed.** The download examples show both `2024-01-01` and `2024-01-02T00:00:00+09:00`.
- Empty values come back as `null`.

### Update frequency (by original source)

| Frequency | Sources |
| --- | --- |
| Daily | NTA corporate numbers, GEPS unified qualification, workplace information site, EDINET |
| Monthly | Official gazette, DX promotion portal (IPA), SME Agency |
| Every six months | Japan Pension Service (establishment info) |
| Yearly | Patent Office |
| Irregular | Other ministries, NEDO |

- Data has been collected since January 2016.
- A company appears with activity data only if public records could be linked to its corporate number.
- Source: https://help.info.gbiz.go.jp/hc/ja/articles/4795050523806

### Rate limits
- The FAQ states there is no usage cap. Very concentrated traffic (about 200,000 requests/hour) may be restricted.
- The API terms forbid excessive access and using several tokens to get around limits.
- Our plan: throttle requests, cache results locally, and use the bulk download for large pulls.
- Sources: https://help.info.gbiz.go.jp/hc/ja/articles/4648561526686 ; terms https://help.info.gbiz.go.jp/hc/ja/articles/4999421139102

### Terms and attribution
- Main terms (https://help.info.gbiz.go.jp/hc/ja/articles/4795140981406) follow 政府標準利用規約 2.0, compatible with CC BY 4.0. Commercial use, copying, redistribution and adaptation are allowed with credit.
- Credit format: 「出典：「Gビズインフォ」（経済産業省）（URL）（○年○月○日に利用）」
- Because we process the data, we must add 「…を加工して作成」. Processed output must not look as if the government made it, and must not harm the listed companies.
- Links to the site should be labeled 「Gビズインフォ」 and open in a new window. Embedding is not allowed. The terms also mention notifying gBizINFO after setting up a link, but are internally inconsistent on whether this is required.
- API terms: use only for the purpose declared in the token application.
- Data from partner APIs follows partner terms listed in a 「別紙」 that we could not locate (**Not confirmed**).

### Freshness check (5 sample companies)
_Pending: requires `GBIZINFO_API_TOKEN`. Run `python scripts/freshness_check.py`; the results will be recorded here._

---

## 2. National Tax Agency corporate number data (法人番号公表サイト)

### Download files (no registration)
- **Formats:** CSV Shift-JIS, CSV Unicode, or XML Unicode, each as a zip with a signature file. CSV files have **no header row**.
- **Full data:** https://www.houjin-bangou.nta.go.jp/download/zenken/
  - Rebuilt at each month-end. Available as a national file or one file per prefecture.
  - The national CSV is about 250 MB.
- **Incremental (差分) data:** https://www.houjin-bangou.nta.go.jp/download/sabun/
  - Published daily on business days around 16:00.
  - Only the last 40 business days are kept, which is about 2 months.
- **Links are not stable URLs.** Each download is a form POST with a per-session token. Automating it would mean replaying the web form, which conflicts with our no-scraping rule. Downloads must therefore be manual, or we use the Web-API.

### CSV columns (30, in order)
1. `sequenceNumber`
2. `corporateNumber`
3. `process`
4. `correct`
5. `updateDate`
6. `changeDate`
7. `name`
8. `nameImageId`
9. `kind`
10. `prefectureName`
11. `cityName`
12. `streetNumber`
13. `addressImageId`
14. `prefectureCode`
15. `cityCode`
16. `postCode`
17. `addressOutside`
18. `addressOutsideImageId`
19. `closeDate`
20. `closeCause`
21. `successorCorporateNumber`
22. `changeCause`
23. `assignmentDate`
24. `latest`
25. `enName`
26. `enPrefectureName`
27. `enCityName`
28. `enAddressOutside`
29. `furigana`
30. `hihyoji`

Source: https://www.houjin-bangou.nta.go.jp/pc/download/images/k-resource-dl.pdf

### Codes
- **`process`** (what changed):
  - 01 new
  - 11 name change
  - 12 domestic address change (also covers municipal mergers)
  - 13 overseas address change
  - 21 registration closed
  - 22 registration revived
  - 71 absorption merger
  - 72 merger invalidated
  - 81 trade name deleted
  - 99 deleted
- **`changeDate`:** the date of the event. **`updateDate`:** when NTA updated its data.
- **`kind`:** 301 kabushiki kaisha, 302 yugen kaisha, 305 godo kaisha, among others.
- The data contains **no** employee count, capital, or industry. It has only name, address and corporate number, plus history.

### Web-API (needs an application ID)
- **Application:** https://www.invoice-kohyo.nta.go.jp/web-api/. Free; the ID arrives by email after 2 weeks to 1 month. The ID must not be shared.
- **Base URL:** `https://api.houjin-bangou.nta.go.jp/4/`
- **`/diff`:** changes in a date range.
  - Parameters: `id`, `from`, `to`, `type`, `address` (prefecture code), `kind` (03 = registered corporations), `divide`.
  - Windows are at most 50 days. Each page has up to 2,000 rows.
  - This is the scriptable source for the "recently changed" flag. Six months is about four windows per prefecture.
- **`/num`:** up to 10 corporate numbers per call.
- **`/name`:** name search.
- **Rate limit:** no number published. Heavy access returns HTTP 403, and mass access in a short time is forbidden.
- Sources: https://www.houjin-bangou.nta.go.jp/webapi/ ; https://www.houjin-bangou.nta.go.jp/pc/webapi/images/k-web-api-kinou-gaiyo.pdf

### Terms and attribution
- **Site terms** (https://www.houjin-bangou.nta.go.jp/riyokiyaku/): PDL1.0.
  - Credit format: 「出典：国税庁法人番号公表サイト（国税庁）（URL）」
  - If processed, add 「…を加工して作成」.
- **Web-API terms** (https://www.houjin-bangou.nta.go.jp/webapi/riyokiyaku.html): a service using the Web-API must display, in a place users can see:
  > このサービスは、国税庁法人番号システムWeb-API機能を利用して取得した情報をもとに作成しているが、サービスの内容は国税庁によって保証されたものではない

---

## 3. EDINET API v2

### Access
- **Subscription-Key is required.** It is passed as a **query parameter** (`Subscription-Key=`), not a header.
- **Signup** is through a Microsoft-hosted login: email, CAPTCHA, a password, and mandatory phone MFA. The owner must do this herself.
- Keys unused for 2 years are deleted.
- Must be called from the server side, because cross-domain browser calls are blocked.
- Source: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf (API spec v2, June 2026)

### Endpoints
- **`GET https://api.edinet-fsa.go.jp/api/v2/documents.json?date=YYYY-MM-DD&type=2`:** the documents filed on a date, up to 10 years back.
- **`GET https://api.edinet-fsa.go.jp/api/v2/documents/{docID}?type=N`:**
  - 1: main filing + XBRL (zip)
  - 2: PDF
  - 3: attachments
  - 4: English files
  - 5: XBRL converted to CSV (only when `csvFlag` = "1")
- Errors still return HTTP 200 with a JSON body. Check `Content-Type` to detect them.

### Document list fields we plan to use
- `docID`, `edinetCode`, `secCode`, **`JCN`** (13-digit corporate number, which lets us join to gBizINFO and NTA), `filerName`, `docTypeCode`, `ordinanceCode`, `formCode`, `periodStart`, `periodEnd`, `submitDateTime`, `docDescription`, `csvFlag`, `withdrawalStatus`, `legalStatus`.
- **Annual securities reports of domestic companies:** `docTypeCode=120`, `ordinanceCode=010`, `formCode=030000`. Investment trusts also use 120, so all three filters are needed.

### Target section
- **XBRL element:** `jpcrp_cor:BusinessPolicyBusinessEnvironmentIssuesToAddressEtcTextBlock` (経営方針、経営環境及び対処すべき課題等).
- **The type=5 CSV is tab-separated UTF-16LE** with these columns: 要素ID, 項目名, コンテキストID, 相対年度, 連結・個別, 期間・時点, ユニットID, 単位, 値.
- **Text values are cut at 30,000 characters.** Use type=1 when the full text is needed.
- Whether text blocks in the CSV are plain text or HTML: **Not confirmed**.

### EDINET code list
- **URL:** https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip. This is a stable link.
- **File:** `EdinetcodeDlInfo.csv`, Shift_JIS.
- **Columns:** ＥＤＩＮＥＴコード, 提出者種別, 上場区分, 連結の有無, 資本金, 決算日, 提出者名, 提出者名（英字）, 提出者名（ヨミ）, 所在地, 提出者業種, 証券コード, 提出者法人番号.
- This tells us which corporate numbers are listed, and their TSE-style industry. The unit of 資本金 is **Not confirmed**; samples suggest millions of yen.

Downloaded on 2026-10-13 with `scripts/download_edinet_codelist.py`, saved as `data/edinet_codelist.parquet` (git-ignored):
- **Records:** 11,414 in total. 3,811 are listed domestic companies (上場, 内国法人・組合), and 3,809 of those have a corporate number.
- **Listed manufacturers nationwide:** 1,397 (the 16 TSE manufacturing sectors). The largest sectors are 電気機器 (230), 機械 (213), 化学 (201) and 食料品 (125).
- **`所在地` usually omits the prefecture** (for example 「中央区日本橋…」 or 「横浜市都筑区…」). Only 42 of 3,811 addresses start with a prefecture name. Prefecture must come from joining on the corporate number with gBizINFO or NTA data, not from this column.

### Rate limits
- No number published. HTTP 429 means too many requests.
- The FAQ suggests polling the list at most once a minute. Mass access in a short time is prohibited, and access can be restricted by IP.

### Terms and attribution
- **Terms:** https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0030.html, revised 2025-04-25.
- **Site content is PDL1.0.**
  - Credit format: 「出典：EDINET閲覧（提出）サイト（URL）、PDL1.0（規約URL）」
  - If processed or excerpted, add 「…をもとに作成」 or 「…より抜粋して作成」.
- The terms do not say explicitly that API data falls under PDL1.0. We apply the same credit to be safe.
- Scraping the website is banned, so we use the API only.

---

## App footer attribution (current text)

- 出典：「Gビズインフォ」（経済産業省）(https://info.gbiz.go.jp/) を加工して作成
- 出典：国税庁法人番号公表サイト（国税庁）(https://www.houjin-bangou.nta.go.jp/) を加工して作成
- 出典：EDINET閲覧（提出）サイト (https://disclosure2.edinet-fsa.go.jp/) をもとに作成、PDL1.0 (https://www.digital.go.jp/resources/open_data/public_data_license_v1.0)
- Add the NTA Web-API disclaimer once the app calls the NTA Web-API.

## Known limitations
- **gBizINFO**
  - Covers only companies with administrative-procedure records.
  - It is not real-time.
  - It has no phone numbers and no revenue time series, except for EDINET filers.
  - Industry is often empty, and search cannot filter by industry.
- **NTA**
  - Basic information only (name, address, history).
  - Downloadable diff files cover only about 2 months.
- **EDINET**
  - Listed and other reporting companies only.
  - Annual reports are filed mostly in June.
