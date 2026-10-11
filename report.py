#!/usr/bin/env python3
"""CLI fallback for the dashboard: print the same metrics and save PNG charts.

Usage:
    python report.py                  # reads incidents.csv, writes charts/
    python report.py --csv data.csv --out figs/
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless — no display needed
import matplotlib.pyplot as plt

import metrics


def save_bar(series, title, ylabel, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    series.plot(kind="bar", ax=ax, color="#4C78A8", edgecolor="black")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def save_line(series, title, ylabel, path):
    fig, ax = plt.subplots(figsize=(8, 4))
    series.plot(kind="line", ax=ax, marker="o", color="#F58518")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Incident ops CLI report.")
    parser.add_argument("--csv", default="incidents.csv")
    parser.add_argument("--out", default="charts", help="PNG output directory")
    args = parser.parse_args(argv)

    df = metrics.load(args.csv)
    k = metrics.kpis(df)

    print("=" * 46)
    print("INCIDENT OPERATIONS REPORT (synthetic demo data)")
    print("=" * 46)
    print(f"Total incidents : {k['total']}")
    print(f"SLA attainment  : {k['sla_attainment_pct']}%")
    print(f"Avg MTTR        : {k['mttr_h']} hours")
    print(f"P1 incidents    : {k['p1_count']}")
    print(f"SLA breaches    : {k['breaches']}")
    print()
    print("Incidents by severity:")
    for sev, n in metrics.severity_distribution(df).items():
        print(f"  {sev}: {n}")
    print()
    print("Avg MTTR by severity (hours):")
    for sev, v in metrics.mttr_by_severity(df).items():
        print(f"  {sev}: {v:.1f}")
    print()
    print("SLA attainment by team:")
    for team, v in metrics.sla_by_team(df).items():
        print(f"  {team}: {v:.1f}%")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    save_bar(metrics.severity_distribution(df), "Incidents by severity",
             "Count", out / "severity.png")
    save_bar(metrics.weekly_volume(df), "Weekly incident volume",
             "Count", out / "weekly_volume.png")
    save_line(metrics.mttr_trend_weekly(df), "MTTR trend (hours per week)",
              "Hours", out / "mttr_trend.png")
    save_bar(metrics.sla_by_team(df), "SLA attainment by team (%)",
             "Percent", out / "sla_by_team.png")
    print(f"\ncharts saved to {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
