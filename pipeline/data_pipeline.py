
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Optional: Google Sheets push
SHEET_ID = os.getenv("SHEET_ID", "")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
PUSH_TO_SHEETS = bool(SHEET_ID and GOOGLE_SERVICE_ACCOUNT_JSON)

def load_data():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    ga = pd.read_csv(os.path.join(data_dir, "google_ads.csv"), parse_dates=["date"])
    fb = pd.read_csv(os.path.join(data_dir, "facebook_ads.csv"), parse_dates=["date"])
    web = pd.read_csv(os.path.join(data_dir, "web_analytics.csv"), parse_dates=["date"])
    return ga, fb, web

def quality_checks(df_ads):
    # basic sanity checks — no negative values, CTR <= 1, CPC/CPA finite
    issues = []
    for col in ["impressions","clicks","spend","conversions","revenue"]:
        if (df_ads[col] < 0).any():
            issues.append(f"Negative values found in {col}.")
    # CTR
    df_ads["ctr"] = df_ads["clicks"] / df_ads["impressions"].replace(0, np.nan)
    if (df_ads["ctr"] > 1).any():
        issues.append("CTR > 100% detected.")
    # CPC & CPA
    df_ads["cpc"] = df_ads["spend"] / df_ads["clicks"].replace(0, np.nan)
    df_ads["cpa"] = df_ads["spend"] / df_ads["conversions"].replace(0, np.nan)
    if not issues:
        print("Quality checks passed.")
    else:
        print("QUALITY WARNINGS:")
        for i in issues:
            print(" -", i)
    return df_ads

def transform(ga, fb, web):
    ads = pd.concat([ga.assign(source="google_ads"), fb.assign(source="facebook_ads")], ignore_index=True)
    ads = quality_checks(ads)

    # Derived metrics
    ads["ctr"] = (ads["clicks"] / ads["impressions"]).fillna(0.0)
    ads["cpc"] = (ads["spend"] / ads["clicks"]).replace([np.inf, -np.inf, np.nan], 0.0)
    ads["cpa"] = (ads["spend"] / ads["conversions"]).replace([np.inf, -np.inf, np.nan], 0.0)
    ads["roas"] = (ads["revenue"] / ads["spend"]).replace([np.inf, -np.inf, np.nan], 0.0)

    # Aggregate for Looker Studio sheet
    ads_daily = ads.groupby(["date","source"], as_index=False).agg({
        "impressions":"sum","clicks":"sum","spend":"sum","conversions":"sum","revenue":"sum"
    })
    ads_daily["ctr"] = (ads_daily["clicks"] / ads_daily["impressions"]).replace([np.inf, -np.inf, np.nan], 0.0)
    ads_daily["cpc"] = (ads_daily["spend"] / ads_daily["clicks"]).replace([np.inf, -np.inf, np.nan], 0.0)
    ads_daily["cpa"] = (ads_daily["spend"] / ads_daily["conversions"]).replace([np.inf, -np.inf, np.nan], 0.0)
    ads_daily["roas"] = (ads_daily["revenue"] / ads_daily["spend"]).replace([np.inf, -np.inf, np.nan], 0.0)

    # Web daily per channel
    web_daily = web.copy()
    web_daily = web_daily.rename(columns={"channel": "source"})

    # Consolidated for Tableau
    consolidated = ads_daily.merge(web_daily, how="left", on=["date","source"])
    consolidated = consolidated.fillna({"sessions":0,"users":0,"transactions":0,"revenue_y":0})
    # Fix revenue naming: ads revenue as revenue_ads, web revenue as revenue_web
    consolidated = consolidated.rename(columns={"revenue_x":"revenue_ads", "revenue_y":"revenue_web"})

    # Write outputs
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    consolidated.to_csv(os.path.join(out_dir, "consolidated.csv"), index=False)
    ads_daily.to_csv(os.path.join(out_dir, "ads_daily.csv"), index=False)
    web_daily.to_csv(os.path.join(out_dir, "web_daily.csv"), index=False)

    print("Wrote consolidated.csv, ads_daily.csv, web_daily.csv in data/.")

    return ads_daily, web_daily, consolidated

def push_to_google_sheets(ads_daily, web_daily):
    # Optional push to Google Sheets using gspread
    import json, gspread
    from google.oauth2.service_account import Credentials

    creds_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(SHEET_ID)

    # Write ads_daily to "ads_daily"
    def df_to_sheet(df, worksheet_name):
        try:
            ws = sh.worksheet(worksheet_name)
            sh.del_worksheet(ws)
        except Exception:
            pass
        ws = sh.add_worksheet(title=worksheet_name, rows=str(len(df)+10), cols=str(len(df.columns)+5))
        ws.update([df.columns.tolist()] + df.astype(str).values.tolist())

    df_to_sheet(ads_daily, "ads_daily")
    df_to_sheet(web_daily, "web_daily")
    print("Pushed data to Google Sheets.")

if __name__ == "__main__":
    ga, fb, web = load_data()
    ads_daily, web_daily, consolidated = transform(ga, fb, web)
    if PUSH_TO_SHEETS:
        try:
            push_to_google_sheets(ads_daily, web_daily)
        except Exception as e:
            print("Sheets push failed:", e)
            print("Continuing without push...")
