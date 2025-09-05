
# Cross-Channel Marketing Performance Dashboard — Portfolio Starter

A complete, **free** starter kit to build a marketing analytics portfolio project for a role like **Marketing Analytics Visualization Specialist**.  
You will publish:
- A **Looker Studio** dashboard (auto-refresh via Google Sheets).
- A **Tableau Public** dashboard (snapshot for portfolio).
- A public **GitHub repo** showing your automation + documentation.

> Tools used: Python, GitHub Actions, Google Sheets, Looker Studio, Tableau Public. All have free tiers.

---

## 0) What you'll build

**Business Scenario:** A consumer brand runs paid campaigns across Google Ads & Facebook Ads. The goal is one view to track spend efficiency and conversion performance, alongside website behavior.

**Dashboards you'll ship:**  
- **KPI tiles:** Spend, Clicks, Conversions, ROAS.  
- **Trends:** KPIs over time with date filter.  
- **Breakdowns:** Channel/Campaign performance (CPA, ROAS).  
- **Funnel:** Impressions → Clicks → Sessions → Transactions.

**Automation you'll showcase:**  
- A Python pipeline that aggregates daily data and **pushes it to Google Sheets**.  
- A **GitHub Actions** cron job (daily) that runs the pipeline, so Looker Studio stays fresh.

---

## 1) Setup the project locally

1. Download this zip and unzip it locally.  
2. (Optional) Initialize a new GitHub repo and commit the files.

Directory structure:
```
marketing-analytics-portfolio-starter/
  data/
    google_ads.csv
    facebook_ads.csv
    web_analytics.csv
  pipeline/
    data_pipeline.py
    requirements.txt
  .github/workflows/
    update-data.yml
  sql/
    derived_metrics.sql
  README.md
```

Install Python deps (prefer a virtualenv):
```bash
pip install -r pipeline/requirements.txt
```

---

## 2) Generate outputs & preview KPIs

Run the pipeline locally:
```bash
python pipeline/data_pipeline.py
```
This will create three files in `data/`:
- `ads_daily.csv` — aggregated ads KPIs per day + channel
- `web_daily.csv` — web sessions/transactions per day + source
- `consolidated.csv` — joined dataset for **Tableau**

---

## 3) OPTIONAL: Set up auto-refresh to Google Sheets (free)

Why: Looker Studio connects to Google Sheets easily and refreshes automatically.

### A) Create a Google Sheet
- Create a sheet named **Marketing Dashboard Data**
- Keep it empty for now; we'll let the script create tabs.

### B) Create a Google Service Account
1. Go to https://console.cloud.google.com/ (free).
2. Create a project (any name).
3. Enable the **Google Sheets API**.
4. Create a **Service Account**, generate a **JSON key**.
5. Copy the **service account email** (something like `my-sa@project.iam.gserviceaccount.com`).
6. Share your Google Sheet with that email (Editor).

### C) Run the pipeline with env vars
Locally:
```bash
export SHEET_ID="YOUR_SHEET_ID"  # found in the sheet URL after /d/
export GOOGLE_SERVICE_ACCOUNT_JSON='{ your JSON key contents here }'

python pipeline/data_pipeline.py
```
The script will create two tabs: `ads_daily` and `web_daily` in your sheet.

### D) Automate with GitHub Actions (no servers needed)
- Push your repo to GitHub.
- Go to **Settings → Secrets and variables → Actions → New repository secret**:
  - `SHEET_ID` = your sheet id
  - `GOOGLE_SERVICE_ACCOUNT_JSON` = paste the whole JSON from step B
- The provided workflow (`.github/workflows/update-data.yml`) runs **daily** at 12:00 UTC and updates the sheet.

---

## 4) Build the **Looker Studio** dashboard (free)

1. Go to https://lookerstudio.google.com/ → **Create** → **Report**.  
2. **Add data source** → **Google Sheets** → pick your sheet → select `ads_daily` and `web_daily`.  
3. Recommended fields (Looker Studio will infer most):
   - `ctr` = clicks / impressions
   - `cpc` = spend / clicks
   - `cpa` = spend / conversions
   - `roas` = revenue / spend
4. Build pages:
   - **Overview:** Scorecards for Spend, Clicks, Conversions, ROAS; time-series for each.
   - **Channels:** Table by `source` with Spend, CTR, CPC, CPA, ROAS.
   - **Trends:** Time-series segmented by `source` with Date filter.
   - **Funnel:** Impressions → Clicks (ads_daily) → Sessions → Transactions (web_daily).
5. Share the dashboard link publicly (view only).

---

## 5) Build the **Tableau Public** dashboard (free)

1. Install **Tableau Public** (free).  
2. **Connect to a Text File** → select `data/consolidated.csv`.  
3. Create calculated fields:
   - `CTR` = [clicks] / [impressions]
   - `CPC` = [spend] / [clicks]
   - `CPA` = [spend] / [conversions]
   - `ROAS` = [revenue_ads] / [spend]
4. Build sheets:
   - **KPI tiles** (use WINDOW_SUM over Date range).
   - **Trend by Date** (line chart).
   - **Channel/Campaign performance** (bar chart with filters).
5. **Publish** to Tableau Public. Copy the public URL.

---

## 6) Portfolio polish (data quality & docs)

- **QA checklist** (already in pipeline): negative values, CTR > 100%, divide-by-zero.  
- Add a **README section** explaining how your automation reduces manual reporting time.  
- Include the `sql/derived_metrics.sql` to show SQL fluency.

---

## 7) Case study write-up (use this outline in your repo + LinkedIn)

**Context** — A brand runs cross-channel campaigns; leaders want one source of truth.  
**Approach** — Unified ads + web data; created ROAS/CPA views; automated daily refresh.  
**Solution** — Looker Studio (refreshing) + Tableau Public (snapshot) dashboards.  
**Impact** — Clear KPIs, faster insights, reduced manual work; scalable standards documented.

---

## 8) LinkedIn post template

> Wrapped a hands-on analytics project yesterday: a **cross-channel marketing dashboard** unifying Google & Facebook Ads with web outcomes.  
> Built with **Tableau Public** + **Looker Studio** and a small **Python** pipeline that auto-updates a Google Sheet daily (free + serverless via GitHub Actions).  
> Highlights: ROAS/CPA trends, channel/campaign drill-downs, and a simple QA layer to catch oddities (like CTR > 100%).  
> If you’re into marketing analytics or building reporting that scales, I’d love your feedback.  
> 🔗 Tableau Public: [link] | 🔗 Live Looker Studio: [link] | 💻 Code: [GitHub link]

---

## 9) Demo checklist (for interviews)

- 60–90 sec walk-through: Problem → Data → Metrics → Dashboard → Automation.  
- Show the sheet updating and the Looker dashboard reflecting it.  
- Open the repo and point to the workflow + pipeline code.

---

## Notes
- Everything here runs on **free tiers**.  
- Replace mock data with real API pulls later using the same pipeline structure.
