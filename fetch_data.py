#!/usr/bin/env python3
"""Fetch daily price history for the Momentum Lab and write docs/data/prices.json.

Uses Yahoo Finance's public chart endpoint (no key). Run before build.py.
Keeps about two years so 200-day averages are ready for the last year shown.
"""
import datetime
import json
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "docs" / "data" / "prices.json"

TICKERS = [
    ("SPY", "S&P 500 ETF"), ("QQQ", "Nasdaq 100 ETF"),
    ("NVDA", "Nvidia"), ("AMD", "AMD"), ("AVGO", "Broadcom"), ("TSM", "TSMC"),
    ("MU", "Micron"), ("SKHY", "SK Hynix (US shares)"), ("000660.KS", "SK Hynix (Seoul, KRW)"),
    ("IREN", "IREN"), ("CRWV", "CoreWeave"), ("VST", "Vistra"), ("CEG", "Constellation"), ("GEV", "GE Vernova"),
    ("MSFT", "Microsoft"), ("GOOGL", "Alphabet"), ("AMZN", "Amazon"), ("META", "Meta"), ("AAPL", "Apple"),
    ("ORCL", "Oracle"), ("ASML", "ASML"), ("ARM", "Arm"), ("MRVL", "Marvell"), ("INTC", "Intel"), ("QCOM", "Qualcomm"),
    ("NBIS", "Nebius"), ("VRT", "Vertiv"),
    ("TSLA", "Tesla"), ("RBLX", "Roblox"), ("TTWO", "Take-Two"), ("U", "Unity"), ("SONY", "Sony"), ("NTDOY", "Nintendo (US shares)"),
    ("PLTR", "Palantir"),
    ("BTC-USD", "Bitcoin"), ("ETH-USD", "Ethereum"),
]


def fetch(symbol: str) -> dict:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2y&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    rows = {}
    for i, t in enumerate(res["timestamp"]):
        o, h, l, c, v = (q[k][i] for k in ("open", "high", "low", "close", "volume"))
        if None in (o, h, l, c):
            continue
        day = datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
        rows[day] = (o, h, l, c, v or 0)  # later entries for the same day win
    days = sorted(rows)
    def rnd(x):
        return float(f"{x:.6g}")
    return {
        "currency": res["meta"].get("currency", "USD"),
        "d": days,
        "o": [rnd(rows[d][0]) for d in days],
        "h": [rnd(rows[d][1]) for d in days],
        "l": [rnd(rows[d][2]) for d in days],
        "c": [rnd(rows[d][3]) for d in days],
        "v": [int(rows[d][4]) for d in days],
    }


def main() -> None:
    out = {"updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), "tickers": {}}
    for sym, name in TICKERS:
        try:
            data = fetch(sym)
            data["name"] = name
            out["tickers"][sym] = data
            print(f"{sym}: {len(data['d'])} days, last {data['d'][-1]} close {data['c'][-1]}")
        except Exception as e:  # keep going; one bad symbol shouldn't stop the rest
            print(f"{sym}: failed ({e})")
        time.sleep(0.4)
    if not out["tickers"]:
        raise SystemExit("no data fetched")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
