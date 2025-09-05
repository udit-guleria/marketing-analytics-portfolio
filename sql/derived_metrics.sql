
-- Example: Derive marketing KPIs from a combined ads table (date, source, impressions, clicks, spend, conversions, revenue)
SELECT
  date,
  source,
  SUM(impressions) AS impressions,
  SUM(clicks)      AS clicks,
  SUM(spend)       AS spend,
  SUM(conversions) AS conversions,
  SUM(revenue)     AS revenue,
  SAFE_DIVIDE(SUM(clicks), SUM(impressions)) AS ctr,
  SAFE_DIVIDE(SUM(spend),  SUM(clicks))      AS cpc,
  SAFE_DIVIDE(SUM(spend),  SUM(conversions)) AS cpa,
  SAFE_DIVIDE(SUM(revenue),SUM(spend))       AS roas
FROM ads_raw
GROUP BY 1,2
ORDER BY 1,2;
