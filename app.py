"""Incident Operations Dashboard — Streamlit app.

Run:
    streamlit run app.py
Then open the local URL Streamlit prints (usually http://localhost:8501).
"""

from pathlib import Path

import streamlit as st

import metrics

CSV = Path(__file__).resolve().parent / "incidents.csv"

st.set_page_config(page_title="Incident Operations Dashboard", layout="wide")
st.title("Incident Operations Dashboard")
st.caption("Synthetic demo data — `python generate_data.py` to regenerate.")

if not CSV.exists():
    st.error("incidents.csv not found. Run `python generate_data.py` first.")
    st.stop()

df = metrics.load(str(CSV))

# ---- filters ----
teams = st.sidebar.multiselect("Team", sorted(df["team"].unique()),
                              default=sorted(df["team"].unique()))
sevs = st.sidebar.multiselect("Severity", metrics.SEVERITY_ORDER,
                              default=metrics.SEVERITY_ORDER)
fdf = df[df["team"].isin(teams) & df["severity"].isin(sevs)]
if fdf.empty:
    st.warning("No incidents match the selected filters.")
    st.stop()

# ---- KPI row ----
k = metrics.kpis(fdf)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total incidents", k["total"])
c2.metric("SLA attainment", f"{k['sla_attainment_pct']}%")
c3.metric("Avg MTTR", f"{k['mttr_h']} h")
c4.metric("P1 incidents", k["p1_count"])
c5.metric("SLA breaches", k["breaches"])

# ---- charts ----
left, right = st.columns(2)
with left:
    st.subheader("Incidents by severity")
    st.bar_chart(metrics.severity_distribution(fdf))
with right:
    st.subheader("Weekly volume")
    st.bar_chart(metrics.weekly_volume(fdf))

left, right = st.columns(2)
with left:
    st.subheader("MTTR trend (hours / week)")
    st.line_chart(metrics.mttr_trend_weekly(fdf))
with right:
    st.subheader("Avg MTTR by severity (hours)")
    st.bar_chart(metrics.mttr_by_severity(fdf))

st.subheader("SLA attainment by team (%)")
st.bar_chart(metrics.sla_by_team(fdf))

with st.expander("Raw data"):
    st.dataframe(fdf.sort_values("opened_at", ascending=False), use_container_width=True)
