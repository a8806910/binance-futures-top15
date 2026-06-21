import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from binance_top15 import render_markdown, select_top_gainers


class BinanceTop15Tests(unittest.TestCase):
    def test_filters_and_sorts_contracts(self):
        exchange_info = {
            "symbols": [
                {"symbol": "AAAUSDT", "status": "TRADING", "contractType": "PERPETUAL", "quoteAsset": "USDT", "marginAsset": "USDT"},
                {"symbol": "BBBUSDT", "status": "TRADING", "contractType": "PERPETUAL", "quoteAsset": "USDT", "marginAsset": "USDT"},
                {"symbol": "EXPIREDUSDT", "status": "BREAK", "contractType": "PERPETUAL", "quoteAsset": "USDT", "marginAsset": "USDT"},
                {"symbol": "QUARTERUSDT", "status": "TRADING", "contractType": "CURRENT_QUARTER", "quoteAsset": "USDT", "marginAsset": "USDT"},
                {"symbol": "COINUSDT", "status": "TRADING", "contractType": "PERPETUAL", "quoteAsset": "USDT", "marginAsset": "BTC"},
            ]
        }
        tickers = [
            {"symbol": "AAAUSDT", "priceChangePercent": "1.25"},
            {"symbol": "BBBUSDT", "priceChangePercent": "9.50"},
            {"symbol": "EXPIREDUSDT", "priceChangePercent": "99.00"},
            {"symbol": "QUARTERUSDT", "priceChangePercent": "88.00"},
            {"symbol": "COINUSDT", "priceChangePercent": "77.00"},
        ]

        self.assertEqual(
            select_top_gainers(exchange_info, tickers),
            [
                {"symbol": "BBBUSDT", "priceChangePercent": 9.5},
                {"symbol": "AAAUSDT", "priceChangePercent": 1.25},
            ],
        )

    def test_markdown_format(self):
        now = datetime(2026, 6, 21, 9, 7, tzinfo=timezone(timedelta(hours=8)))
        report = render_markdown([{"symbol": "AAAUSDT", "priceChangePercent": 1.2}], now)
        self.assertIn("北京时间：2026-06-21 09:07", report)
        self.assertIn("| 1 | AAAUSDT | 1.20% |", report)


if __name__ == "__main__":
    unittest.main()
