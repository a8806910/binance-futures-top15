#!/usr/bin/env python3
"""Fetch Binance USD-M perpetual top gainers and render a Markdown report."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


BASE_URL = "https://fapi.binance.com"
EXCHANGE_INFO_PATH = "/fapi/v1/exchangeInfo"
TICKER_24H_PATH = "/fapi/v1/ticker/24hr"
BEIJING_TIME = timezone(timedelta(hours=8), name="Asia/Shanghai")


def fetch_json(url: str, attempts: int = 3) -> Any:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "binance-top15/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"Failed to fetch {url} after {attempts} attempts") from last_error


def select_top_gainers(exchange_info: dict[str, Any], tickers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = {
        symbol["symbol"]
        for symbol in exchange_info["symbols"]
        if symbol.get("status") == "TRADING"
        and symbol.get("contractType") == "PERPETUAL"
        and symbol.get("quoteAsset") == "USDT"
        and symbol.get("marginAsset") == "USDT"
    }

    ranked = [
        {"symbol": ticker["symbol"], "priceChangePercent": float(ticker["priceChangePercent"])}
        for ticker in tickers
        if ticker.get("symbol") in eligible
    ]
    ranked.sort(key=lambda row: row["priceChangePercent"], reverse=True)
    return ranked[:15]


def render_markdown(rows: list[dict[str, Any]], now: datetime | None = None) -> str:
    current = now or datetime.now(BEIJING_TIME)
    lines = [
        f"北京时间：{current:%Y-%m-%d %H:%M}",
        "",
        "口径：币安 U 本位永续合约 24 小时涨幅",
        "",
        "| 排名 | 合约币对 | 涨幅 |",
        "|---:|---|---:|",
    ]
    lines.extend(
        f"| {rank} | {row['symbol']} | {row['priceChangePercent']:.2f}% |"
        for rank, row in enumerate(rows, start=1)
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="Write Markdown to this path; stdout if omitted")
    parser.add_argument("--base-url", default=BASE_URL, help=argparse.SUPPRESS)
    args = parser.parse_args()

    exchange_info = fetch_json(args.base_url + EXCHANGE_INFO_PATH)
    tickers = fetch_json(args.base_url + TICKER_24H_PATH)
    report = render_markdown(select_top_gainers(exchange_info, tickers))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")


if __name__ == "__main__":
    main()
