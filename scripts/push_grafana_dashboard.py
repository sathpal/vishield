#!/usr/bin/env python
"""Generate the ViShield Grafana dashboard as code and push it via the Grafana HTTP API.

Reads GRAFANA_URL, GRAFANA_SA_TOKEN and GRAFANA_PROM_DS_UID from the environment
(or observability/.env). Use --dry-run to only write observability/grafana/vishield.json.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests

DASHBOARD_UID = "vishield-overview"
FOLDER_TITLE = "ViShield"

GREEN, AMBER, RED, BLUE, PURPLE, GREY = (
    "green",
    "orange",
    "red",
    "blue",
    "purple",
    "#8e8e8e",
)


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.split("#")[0].strip())


def _ds(uid: str) -> dict[str, str]:
    return {"type": "prometheus", "uid": uid}


def _target(
    expr: str, legend: str = "", ref: str = "A", instant: bool = False, fmt: str | None = None
) -> dict[str, Any]:
    t: dict[str, Any] = {"expr": expr, "legendFormat": legend or "__auto", "refId": ref}
    if instant:
        t["instant"] = True
        t["range"] = False
    if fmt:
        t["format"] = fmt
    return t


def _panel(
    kind: str,
    title: str,
    targets: list[dict[str, Any]],
    grid: tuple[int, int, int, int],
    ds: str,
    description: str = "",
    unit: str | None = None,
    thresholds: list[tuple[str, float | None]] | None = None,
    overrides: list[dict[str, Any]] | None = None,
    options: dict[str, Any] | None = None,
    custom: dict[str, Any] | None = None,
    min_: float | None = None,
    max_: float | None = None,
    decimals: int | None = None,
    transformations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    x, y, w, h = grid
    defaults: dict[str, Any] = {"color": {"mode": "palette-classic"}}
    if unit:
        defaults["unit"] = unit
    if decimals is not None:
        defaults["decimals"] = decimals
    if min_ is not None:
        defaults["min"] = min_
    if max_ is not None:
        defaults["max"] = max_
    if thresholds:
        defaults["color"] = {"mode": "thresholds"}
        defaults["thresholds"] = {
            "mode": "absolute",
            "steps": [{"color": c, "value": v} for c, v in thresholds],
        }
    if custom:
        defaults["custom"] = custom
    return {
        "type": kind,
        "title": title,
        "description": description,
        "datasource": _ds(ds),
        "gridPos": {"x": x, "y": y, "w": w, "h": h},
        "targets": [{**t, "datasource": _ds(ds)} for t in targets],
        "fieldConfig": {"defaults": defaults, "overrides": overrides or []},
        "options": options or {},
        "transformations": transformations or [],
    }


def _row(title: str, y: int) -> dict[str, Any]:
    return {
        "type": "row",
        "title": title,
        "collapsed": False,
        "gridPos": {"x": 0, "y": y, "w": 24, "h": 1},
        "panels": [],
    }


def _level_overrides() -> list[dict[str, Any]]:
    return [
        {
            "matcher": {"id": "byName", "options": name},
            "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": color}}],
        }
        for name, color in (("low", GREEN), ("medium", AMBER), ("high", RED))
    ]


def build(ds: str) -> dict[str, Any]:
    sel = 'job="vishield-api", instance=~"$instance"'
    ts_opts = {
        "legend": {"displayMode": "list", "placement": "bottom"},
        "tooltip": {"mode": "multi", "sort": "desc"},
    }
    stat_opts = {
        "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
        "colorMode": "value",
        "graphMode": "area",
        "textMode": "value",
    }
    panels: list[dict[str, Any]] = []

    # ---------- Row 1: headline stats
    panels.append(_row("Headline (selected time range)", 0))
    panels += [
        _panel(
            "stat",
            "Analyses",
            [_target(f"sum(increase(vishield_analyses_total{{{sel}}}[$__range]))", instant=True)],
            (0, 1, 4, 4),
            ds,
            "Completed analyses in the selected time range.",
            thresholds=[(BLUE, None)],
            decimals=0,
            options=stat_opts,
        ),
        _panel(
            "stat",
            "High-risk share",
            [
                _target(
                    f'sum(increase(vishield_analyses_total{{{sel}, risk_level="high"}}[$__range])) / clamp_min(sum(increase(vishield_analyses_total{{{sel}}}[$__range])), 1)',
                    instant=True,
                )
            ],
            (4, 1, 4, 4),
            ds,
            "Fraction of analyses scored HIGH. Fictional demo traffic, not a real-world rate.",
            unit="percentunit",
            min_=0,
            max_=1,
            thresholds=[(GREEN, None), (AMBER, 0.4), (RED, 0.7)],
            options=stat_opts,
        ),
        _panel(
            "stat",
            "p95 analysis latency",
            [
                _target(
                    f"histogram_quantile(0.95, sum by (le) (rate(vishield_processing_seconds_bucket{{{sel}}}[$__rate_interval])))",
                    instant=True,
                )
            ],
            (8, 1, 4, 4),
            ds,
            "95th percentile end-to-end analysis time.",
            unit="s",
            thresholds=[(GREEN, None), (AMBER, 0.5), (RED, 2)],
            options=stat_opts,
        ),
        _panel(
            "stat",
            "Rejected requests",
            [_target(f"sum(increase(vishield_errors_total{{{sel}}}[$__range]))", instant=True)],
            (12, 1, 4, 4),
            ds,
            "Validation rejections and failures (empty transcript, bad file, oversized...).",
            decimals=0,
            thresholds=[(GREEN, None), (AMBER, 1), (RED, 20)],
            options=stat_opts,
        ),
        _panel(
            "stat",
            "ML model loaded",
            [_target(f"max(vishield_model_loaded{{{sel}}})", instant=True)],
            (16, 1, 4, 4),
            ds,
            "0 means the API is running rules-only.",
            thresholds=[(RED, None), (GREEN, 1)],
            options={**stat_opts, "graphMode": "none"},
            overrides=[
                {
                    "matcher": {"id": "byName", "options": "Value"},
                    "properties": [
                        {
                            "id": "mappings",
                            "value": [
                                {
                                    "type": "value",
                                    "options": {"0": {"text": "NO"}, "1": {"text": "YES"}},
                                }
                            ],
                        }
                    ],
                }
            ],
        ),
        _panel(
            "stat",
            "Last batch F1",
            [_target(f'max(vishield_batch_metric{{{sel}, metric="f1"}})', instant=True)],
            (20, 1, 4, 4),
            ds,
            "F1 from the most recent labelled batch evaluation. n is tiny and fictional.",
            unit="percentunit",
            min_=0,
            max_=1,
            thresholds=[(RED, None), (AMBER, 0.7), (GREEN, 0.9)],
            options={**stat_opts, "graphMode": "none"},
        ),
    ]

    # ---------- Row 2: risk
    panels.append(_row("Risk outcomes", 5))
    panels += [
        _panel(
            "timeseries",
            "Analyses per minute by risk level",
            [
                _target(
                    f"sum by (risk_level) (rate(vishield_analyses_total{{{sel}}}[$__rate_interval])) * 60",
                    "{{risk_level}}",
                )
            ],
            (0, 6, 12, 8),
            ds,
            "Stacked rate of completed analyses split by the fused risk level.",
            unit="short",
            overrides=_level_overrides(),
            custom={"stacking": {"mode": "normal"}, "fillOpacity": 35, "lineWidth": 1},
            options=ts_opts,
        ),
        _panel(
            "bargauge",
            "Risk score distribution",
            [
                _target(
                    f"sum by (le) (increase(vishield_risk_score_bucket{{{sel}}}[$__range]))",
                    "≤ {{le}}",
                    fmt="heatmap",
                )
            ],
            (12, 6, 6, 8),
            ds,
            "Analyses per risk-score bucket (0-100) over the selected range.",
            decimals=0,
            thresholds=[(GREEN, None), (AMBER, 50), (RED, 150)],
            options={
                "orientation": "horizontal",
                "displayMode": "gradient",
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                "showUnfilled": True,
            },
        ),
        _panel(
            "piechart",
            "Risk level mix",
            [
                _target(
                    f"sum by (risk_level) (increase(vishield_analyses_total{{{sel}}}[$__range]))",
                    "{{risk_level}}",
                    instant=True,
                )
            ],
            (18, 6, 6, 8),
            ds,
            "Share of low / medium / high over the range.",
            overrides=_level_overrides(),
            options={
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                "pieType": "donut",
                "legend": {"displayMode": "list", "placement": "right", "values": ["percent"]},
                "displayLabels": ["percent"],
            },
        ),
    ]

    # ---------- Row 3: explainability signals
    panels.append(_row("Explainability signals", 14))
    panels += [
        _panel(
            "barchart",
            "Indicator families detected",
            [
                _target(
                    f"sum by (category) (increase(vishield_indicators_total{{{sel}}}[$__range]))",
                    "{{category}}",
                    instant=True,
                    fmt="table",
                )
            ],
            (0, 15, 12, 8),
            ds,
            "How often each social-engineering indicator family fired (one analysis can fire several).",
            thresholds=[(PURPLE, None)],
            decimals=0,
            transformations=[
                {"id": "organize", "options": {"excludeByName": {"Time": True}}},
                {"id": "sortBy", "options": {"sort": [{"field": "Value", "desc": True}]}},
            ],
            options={
                "orientation": "horizontal",
                "showValue": "auto",
                "legend": {"showLegend": False},
                "xTickLabelSpacing": 0,
            },
            custom={"fillOpacity": 80},
        ),
        _panel(
            "timeseries",
            "Rule score vs classifier probability (p50)",
            [
                _target(
                    f"histogram_quantile(0.5, sum by (le) (rate(vishield_rule_score_bucket{{{sel}}}[$__rate_interval])))",
                    "rule score p50",
                    "A",
                ),
                _target(
                    f"histogram_quantile(0.5, sum by (le) (rate(vishield_ml_probability_bucket{{{sel}}}[$__rate_interval])))",
                    "ML probability p50",
                    "B",
                ),
                _target(
                    f"histogram_quantile(0.5, sum by (le) (rate(vishield_confidence_bucket{{{sel}}}[$__rate_interval])))",
                    "confidence aid p50",
                    "C",
                ),
            ],
            (12, 15, 12, 8),
            ds,
            "Median of each fused component. Divergence between rules and ML is where human review matters most.",
            unit="percentunit",
            min_=0,
            max_=1,
            custom={"lineWidth": 2, "fillOpacity": 10},
            options=ts_opts,
        ),
    ]

    # ---------- Row 4: privacy & quality
    panels.append(_row("Privacy and quality", 23))
    panels += [
        _panel(
            "barchart",
            "Values redacted before persistence",
            [
                _target(
                    f"sum by (kind) (increase(vishield_redactions_total{{{sel}}}[$__range]))",
                    "{{kind}}",
                    instant=True,
                    fmt="table",
                )
            ],
            (0, 24, 8, 8),
            ds,
            "Phone numbers, OTP-like codes, URLs, emails, account and card numbers removed from transcripts.",
            thresholds=[(BLUE, None)],
            decimals=0,
            transformations=[
                {"id": "organize", "options": {"excludeByName": {"Time": True}}},
                {"id": "sortBy", "options": {"sort": [{"field": "Value", "desc": True}]}},
            ],
            options={
                "orientation": "vertical",
                "showValue": "auto",
                "legend": {"showLegend": False},
            },
            custom={"fillOpacity": 80},
        ),
        _panel(
            "timeseries",
            "Rejections by reason",
            [
                _target(
                    f"sum by (code) (rate(vishield_errors_total{{{sel}}}[$__rate_interval])) * 60",
                    "{{code}}",
                )
            ],
            (8, 24, 8, 8),
            ds,
            "Per-minute rate of rejected requests by error code.",
            unit="short",
            custom={"stacking": {"mode": "normal"}, "fillOpacity": 30, "lineWidth": 1},
            options=ts_opts,
        ),
        _panel(
            "bargauge",
            "Last batch evaluation",
            [_target(f"vishield_batch_metric{{{sel}}}", "{{metric}}", instant=True)],
            (16, 24, 8, 8),
            ds,
            "Accuracy / precision / recall / F1 / ROC-AUC from the most recent labelled batch. Tiny fictional data.",
            unit="percentunit",
            min_=0,
            max_=1,
            thresholds=[(RED, None), (AMBER, 0.7), (GREEN, 0.9)],
            options={
                "orientation": "horizontal",
                "displayMode": "lcd",
                "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            },
        ),
    ]

    # ---------- Row 5: service health
    panels.append(_row("Service health", 32))
    panels += [
        _panel(
            "timeseries",
            "HTTP requests per minute by route",
            [
                _target(
                    f"sum by (route) (rate(vishield_http_requests_total{{{sel}}}[$__rate_interval])) * 60",
                    "{{route}}",
                )
            ],
            (0, 33, 8, 8),
            ds,
            "",
            unit="short",
            custom={"fillOpacity": 15},
            options=ts_opts,
        ),
        _panel(
            "timeseries",
            "HTTP status mix",
            [
                _target(
                    f"sum by (status) (rate(vishield_http_requests_total{{{sel}}}[$__rate_interval])) * 60",
                    "{{status}}",
                )
            ],
            (8, 33, 8, 8),
            ds,
            "",
            unit="short",
            custom={"stacking": {"mode": "percent"}, "fillOpacity": 40, "lineWidth": 0},
            overrides=[
                {
                    "matcher": {"id": "byRegexp", "options": "2.."},
                    "properties": [
                        {"id": "color", "value": {"mode": "fixed", "fixedColor": GREEN}}
                    ],
                },
                {
                    "matcher": {"id": "byRegexp", "options": "4.."},
                    "properties": [
                        {"id": "color", "value": {"mode": "fixed", "fixedColor": AMBER}}
                    ],
                },
                {
                    "matcher": {"id": "byRegexp", "options": "5.."},
                    "properties": [{"id": "color", "value": {"mode": "fixed", "fixedColor": RED}}],
                },
            ],
            options=ts_opts,
        ),
        _panel(
            "timeseries",
            "Analysis latency p50 / p95 / p99",
            [
                _target(
                    f"histogram_quantile(0.5, sum by (le) (rate(vishield_processing_seconds_bucket{{{sel}}}[$__rate_interval])))",
                    "p50",
                    "A",
                ),
                _target(
                    f"histogram_quantile(0.95, sum by (le) (rate(vishield_processing_seconds_bucket{{{sel}}}[$__rate_interval])))",
                    "p95",
                    "B",
                ),
                _target(
                    f"histogram_quantile(0.99, sum by (le) (rate(vishield_processing_seconds_bucket{{{sel}}}[$__rate_interval])))",
                    "p99",
                    "C",
                ),
            ],
            (16, 33, 8, 8),
            ds,
            "",
            unit="s",
            custom={"lineWidth": 2, "fillOpacity": 5},
            options=ts_opts,
        ),
    ]

    return {
        "uid": DASHBOARD_UID,
        "title": "ViShield — Voice Phishing Detection Overview",
        "description": "Academic defensive prototype. All metrics are anonymised aggregates; no transcript text leaves the API.",
        "tags": ["vishield", "security-awareness", "academic"],
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "editable": True,
        "graphTooltip": 1,
        "time": {"from": "now-1h", "to": "now"},
        "refresh": "30s",
        "templating": {
            "list": [
                {
                    "name": "instance",
                    "label": "Instance",
                    "type": "query",
                    "datasource": _ds(ds),
                    "query": {
                        "query": 'label_values(vishield_analyses_total{job="vishield-api"}, instance)',
                        "refId": "var",
                    },
                    "refresh": 2,
                    "includeAll": True,
                    "multi": True,
                    "allValue": ".*",
                    "current": {"selected": True, "text": ["All"], "value": ["$__all"]},
                }
            ]
        },
        "links": [
            {
                "title": "ViShield API docs",
                "type": "link",
                "url": "http://localhost:8000/docs",
                "targetBlank": True,
            },
            {
                "title": "Dashboard",
                "type": "link",
                "url": "http://localhost:8501",
                "targetBlank": True,
            },
        ],
        "panels": panels,
    }


def push(dashboard: dict[str, Any], url: str, token: str) -> str:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    folders = requests.get(f"{url}/api/folders", headers=headers, timeout=20).json()
    folder = next((f for f in folders if f["title"] == FOLDER_TITLE), None)
    if folder is None:
        folder = requests.post(
            f"{url}/api/folders", headers=headers, json={"title": FOLDER_TITLE}, timeout=20
        ).json()
    payload = {
        "dashboard": dashboard,
        "folderUid": folder["uid"],
        "overwrite": True,
        "message": "pushed by scripts/push_grafana_dashboard.py",
    }
    r = requests.post(f"{url}/api/dashboards/db", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return f"{url}{r.json()['url']}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default="observability/.env", type=Path)
    parser.add_argument("--out", default="observability/grafana/vishield.json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load_env(args.env_file)
    ds = os.environ.get("GRAFANA_PROM_DS_UID", "grafanacloud-prom")
    dashboard = build(ds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    print(f"wrote {args.out} ({len(dashboard['panels'])} panels)")
    if args.dry_run:
        return
    url, token = os.environ.get("GRAFANA_URL"), os.environ.get("GRAFANA_SA_TOKEN")
    if not url or not token:
        raise SystemExit("GRAFANA_URL and GRAFANA_SA_TOKEN are required (or use --dry-run)")
    print("dashboard:", push(dashboard, url.rstrip("/"), token))


if __name__ == "__main__":
    main()
