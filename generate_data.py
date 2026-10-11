#!/usr/bin/env python3
"""Generate a synthetic incident dataset for the ops dashboard demo.

Writes ``incidents.csv`` with ~300 rows. All data is randomly generated
(seed = 42, so the output is reproducible) — no real company data.

Schema:
    incident_id   INC-0001, INC-0002, ...
    title         short synthetic title
    severity      P1 | P2 | P3 | P4
    team          owning team
    category      failure category
    opened_at     ISO timestamp
    resolved_at   ISO timestamp (always after opened_at)
    sla_target_h  SLA target in hours for the severity

Usage:
    python generate_data.py                 # writes incidents.csv
    python generate_data.py --rows 500 --seed 7 -o data.csv
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta

SEVERITIES = ["P1", "P2", "P3", "P4"]
SEV_WEIGHTS = [0.05, 0.20, 0.35, 0.40]
# SLA targets (hours) per severity — typical enterprise values
SLA_TARGETS = {"P1": 4, "P2": 24, "P3": 72, "P4": 168}

TEAMS = ["Platform", "Data Engineering", "Network", "App Support"]
CATEGORIES = ["Database", "API", "Infrastructure", "Deployment", "Monitoring", "Auth"]

TITLES = {
    "Database": ["connection pool exhausted", "replica lag spiking", "slow query blocking writes"],
    "API": ["elevated 5xx on checkout API", "latency p99 breach", "auth token refresh failures"],
    "Infrastructure": ["node disk pressure", "pod evictions in prod cluster", "DNS resolution flakiness"],
    "Deployment": ["canary rollback triggered", "failed deploy stuck in pipeline", "config drift detected"],
    "Monitoring": ["alert storm from noisy monitor", "dashboard gap in metrics", "pager misroute"],
    "Auth": ["SSO login failures", "token expiry storm", "MFA push delays"],
}


def gen_incidents(rows: int, seed: int, start: datetime) -> list[dict]:
    rng = random.Random(seed)
    out = []
    for i in range(1, rows + 1):
        sev = rng.choices(SEVERITIES, weights=SEV_WEIGHTS)[0]
        team = rng.choice(TEAMS)
        cat = rng.choice(CATEGORIES)
        # Incidents spread over the last 12 weeks, busier on weekdays
        days_ago = rng.randint(0, 83)
        opened = start - timedelta(days=days_ago,
                                   hours=rng.randint(0, 23),
                                   minutes=rng.randint(0, 59))
        if opened.weekday() >= 5 and rng.random() < 0.6:
            opened -= timedelta(days=rng.choice([1, 2]))  # shift weekend noise to weekdays

        # Resolution time: lognormal-ish around a fraction of the SLA target,
        # with ~12% breaching the target for realism.
        target = SLA_TARGETS[sev]
        if rng.random() < 0.12:
            hours = target * rng.uniform(1.05, 2.5)          # breach
        else:
            hours = target * rng.uniform(0.05, 0.95)         # within SLA
        resolved = opened + timedelta(hours=hours)

        out.append({
            "incident_id": f"INC-{i:04d}",
            "title": rng.choice(TITLES[cat]),
            "severity": sev,
            "team": team,
            "category": cat,
            "opened_at": opened.strftime("%Y-%m-%d %H:%M"),
            "resolved_at": resolved.strftime("%Y-%m-%d %H:%M"),
            "sla_target_h": target,
        })
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic incident data.")
    parser.add_argument("--rows", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("-o", "--output", default="incidents.csv")
    args = parser.parse_args(argv)

    rows = gen_incidents(args.rows, args.seed, datetime.now().replace(microsecond=0))
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} incidents -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
