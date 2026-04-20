-- Top 5 Renewal Accounts by Region × Segment (Q1/Q2, No Open Opportunities)
-- Returns: CRM_ACCOUNT_ID, CRM_ACCOUNT_NAME, region, segment, ae, arr, renewal_date, quarter,
--          has_ai_agents_rec, has_copilot_rec, has_seat_upgrade_rec, has_es_rec, rank

WITH sales_hierarchy AS (
  SELECT DISTINCT
    crm_account_id,
    ae_name
  FROM presentation.gtm_sales_ops.control_and_impact_dash
),
accounts_with_renewals AS (
  SELECT
    c.CRM_ACCOUNT_ID,
    c.CRM_ACCOUNT_NAME,
    CASE WHEN c.PRO_FORMA_REGION = 'NA' THEN 'AMER' ELSE COALESCE(c.PRO_FORMA_REGION, 'Unknown') END as region,
    COALESCE(c.PRO_FORMA_MARKET_SEGMENT, 'Unknown') as segment,
    c.CRM_NET_ARR_USD as arr,
    c.CRM_NEXT_RENEWAL_DATE as renewal_date,
    COALESCE(h.ae_name, 'Not Assigned') as ae,
    CASE
      WHEN c.CRM_NEXT_RENEWAL_DATE BETWEEN '2026-02-01' AND '2026-04-30' THEN 'Q1'
      WHEN c.CRM_NEXT_RENEWAL_DATE BETWEEN '2026-05-01' AND '2026-07-31' THEN 'Q2'
    END as quarter
  FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD c
  LEFT JOIN sales_hierarchy h ON c.CRM_ACCOUNT_ID = h.crm_account_id
  WHERE c.SERVICE_DATE = (SELECT MAX(SERVICE_DATE) FROM PRESENTATION.CUSTOMER_EXPERIENCE.CUSTOMER_SUCCESS__CS_RESET_DASHBOARD)
    AND c.AS_OF_DATE = 'Quarterly'
    AND c.CRM_NET_ARR_USD > 0
    AND c.CRM_NEXT_RENEWAL_DATE BETWEEN '2026-02-01' AND '2026-07-31'
),
open_opps AS (
  SELECT DISTINCT CRM_ACCOUNT_ID
  FROM functional.gtm_sales_ops.gtmsi_consolidated_pipeline_bookings
  WHERE OPPORTUNITY_STATUS = 'Open'
    AND DATE_LABEL = 'today'
),
accounts_without_opps AS (
  SELECT a.*
  FROM accounts_with_renewals a
  LEFT JOIN open_opps o ON a.CRM_ACCOUNT_ID = o.CRM_ACCOUNT_ID
  WHERE o.CRM_ACCOUNT_ID IS NULL
),
bullseye_recommendations AS (
  SELECT
    crm_account_id,
    MAX(CASE WHEN rec.value:priority::INT IN (1, 2) AND rec.value:type::STRING = 'AI_AGENTS_ADVANCED' THEN 1 ELSE 0 END) as has_ai_agents_rec,
    MAX(CASE WHEN rec.value:priority::INT IN (1, 2) AND rec.value:type::STRING = 'COPILOT' THEN 1 ELSE 0 END) as has_copilot_rec,
    MAX(CASE WHEN rec.value:priority::INT IN (1, 2) AND rec.value:type::STRING = 'SEAT_CHANGE' THEN 1 ELSE 0 END) as has_seat_upgrade_rec,
    MAX(CASE WHEN rec.value:priority::INT IN (1, 2) AND rec.value:type::STRING = 'ES' THEN 1 ELSE 0 END) as has_es_rec
  FROM PRESENTATION.BULLSEYE_PRO.CUSTOMERS,
       LATERAL FLATTEN(input => RECOMMENDATIONS) rec
  GROUP BY crm_account_id
),
ranked AS (
  SELECT
    a.*,
    COALESCE(b.has_ai_agents_rec, 0) as has_ai_agents_rec,
    COALESCE(b.has_copilot_rec, 0) as has_copilot_rec,
    COALESCE(b.has_seat_upgrade_rec, 0) as has_seat_upgrade_rec,
    COALESCE(b.has_es_rec, 0) as has_es_rec,
    ROW_NUMBER() OVER (PARTITION BY a.region, a.segment ORDER BY a.arr DESC) as rank
  FROM accounts_without_opps a
  LEFT JOIN bullseye_recommendations b ON a.CRM_ACCOUNT_ID = b.crm_account_id
)
SELECT
  CRM_ACCOUNT_ID,
  CRM_ACCOUNT_NAME,
  region,
  segment,
  ae,
  arr,
  renewal_date,
  quarter,
  has_ai_agents_rec,
  has_copilot_rec,
  has_seat_upgrade_rec,
  has_es_rec,
  rank
FROM ranked
WHERE rank <= 5
ORDER BY
  CASE region WHEN 'AMER' THEN 1 WHEN 'EMEA' THEN 2 WHEN 'APAC' THEN 3 WHEN 'LATAM' THEN 4 ELSE 99 END,
  CASE segment WHEN 'Enterprise' THEN 1 WHEN 'Strategic' THEN 2 WHEN 'Public Sector' THEN 3 WHEN 'Commercial' THEN 4 WHEN 'SMB' THEN 5 WHEN 'Digital' THEN 6 ELSE 99 END,
  rank;
