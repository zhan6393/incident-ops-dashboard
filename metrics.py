"""Shared metrics for the incident ops dashboard.

All computations live here so the Streamlit app and the CLI report
always agree.
"""

from __future__ import annotations

import pandas as pd

SEVERITY_ORDER = ["P1", "P2", "P3", "P4"]


def load(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["opened_at", "resolved_at"])
    df["resolution_h"] = (df["resolved_at"] - df["opened_at"]).dt.total_seconds() / 3600
    df["sla_met"] = df["resolution_h"] <= df["sla_target_h"]
    df["week"] = df["opened_at"].dt.to_period("W").dt.start_time.dt.date.astype(str)
    return df


def kpis(df: pd.DataFrame) -> dict:
    return {
        "total": len(df),
        "sla_attainment_pct": round(df["sla_met"].mean() * 100, 1),
        "mttr_h": round(df["resolution_h"].mean(), 1),
        "p1_count": int((df["severity"] == "P1").sum()),
        "breaches": int((~df["sla_met"]).sum()),
    }


def severity_distribution(df: pd.DataFrame) -> pd.Series:
    return df["severity"].value_counts().reindex(SEVERITY_ORDER, fill_value=0)


def mttr_by_severity(df: pd.DataFrame) -> pd.Series:
    return df.groupby("severity")["resolution_h"].mean().reindex(SEVERITY_ORDER)


def weekly_volume(df: pd.DataFrame) -> pd.Series:
    return df.groupby("week").size().sort_index()


def mttr_trend_weekly(df: pd.DataFrame) -> pd.Series:
    return df.groupby("week")["resolution_h"].mean().sort_index()


def sla_by_team(df: pd.DataFrame) -> pd.Series:
    return (df.groupby("team")["sla_met"].mean() * 100).round(1).sort_values()
