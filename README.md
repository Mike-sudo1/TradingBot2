# Fabio Trading Bot

A lightweight day-trading bot prototype implementing the "Fabio" strategy on Binance.
This project demonstrates a production style structure with modular components and
basic indicator and scoring logic. **Use at your own risk.**

## Features
- Async websocket price feed (`bookTicker`)
- Technical indicators: RSI, MACD, moving averages, VWAP
- Simplified Fabio scoring and trade selection
- Risk management with trailing stops and daily drawdown limits
- Optional Telegram notifications
- CSV trade logging
- Minimal backtesting on CSV tick data

## Installation

```bash
pip install python-binance websockets numpy pandas python-dotenv tenacity aiohttp loguru pytest
```

## Configuration

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

Important variables:
- `BINANCE_API_KEY`, `BINANCE_API_SECRET`
- `LIVE` – set `true` to send real orders
- `WATCHLIST` – comma separated symbols, e.g. `BTCUSDT,ETHUSDT`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` for notifications (optional)
- `ENTRY_MIN_GRADE` – minimum Fabio grade to allow entries (`A`>`B`>`C`)
- `ENTRY_MIN_SCORE` – minimum numerical score override (default 0)
- `RISK_UNIT` – `bps` or `usdt` for risk printouts


## Running

Paper trading mode (default):

```bash
python -m bot.main --live false --debug true
```

Backtest on CSV ticks:

```bash
python -m bot.backtest data.csv BTCUSDT
```

## Tests

```bash
pytest -q
```

## Disclaimer

This code is for educational purposes only and is **not** financial advice. Trading
cryptocurrencies involves significant risk.
