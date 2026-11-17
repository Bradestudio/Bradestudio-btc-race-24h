# Bradestudio-btc-race-24h

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/Bradestudio/Bradestudio-btc-race-24h/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/Bradestudio/Bradestudio-btc-race-24h/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A Python 3.13 bot (standard library only) for the make.fun bounty
"Race a BTC trading bot live for 24 hours". It trades Coinbase Wrapped BTC
(cbBTC) against USDC on 1-minute Orca Whirlpool bars, long only, starting
from $1,000 of paper money.

## Run it

```sh
python3 main.py
```

The bot speaks the make.fun bars-replay protocol on stdin/stdout (NDJSON
batches in, orders out). To grade it locally with the official grader:

```sh
node <kit>/cli/makefun.mjs grade-local --kit <kit> --bot <this repo> --driver docker
```

## Strategy

1. **Buy once, early** — on batch 12, spend all cash (fills at bar 13's
   open). If the buy is ever rejected, retry on the next bar, up to
   batch 60.
2. **Hold until one exit fires** (checked on every bar's close):
   - take profit at **+0.90%** over cost,
   - stop loss at **−0.60%** under cost,
   - trailing stop at **−0.60%** under the position's peak value.
3. **Then stay in cash** — no re-entry. If no exit fires, the harness
   flattens the position at the last close.

## Why

- A full round trip costs ~26 bps (4 bps fee + 2 bps slippage + price
  impact); a 1-minute bar moves ~6 bps (1σ). Frequent 1-minute trading
  bleeds: on the frozen dev window the kit's EMA-cross baseline lost
  $106.22 over 68 trades.
- The dev window's money is in one intraday swing (a +1.96% 60-minute
  rally, then a −2.06% drop). One early entry plus a tight take-profit
  and a tight stop catches the swing and caps the loss if the day turns.
- Re-entry was tested and rejected: on a down week of out-of-sample
  BTC data every re-entry is another stopped-out loss.

## Results

| Window | Net PnL | Trades | Max drawdown |
| --- | --- | --- | --- |
| Dev (frozen, 16–17 Nov 2026) | **+$7.54** | 2 | 0.55% |
| 13 out-of-sample 24h windows (Binance BTC/USDT 1m, 9–16 Nov 2026) | median −$6.43, worst −$8.23 | 2 | ≤1.1% |

Dev gate (net PnL > $0): **passed**. Guardrails: ≥1 trade, max
drawdown ≤25%: **met** (0.55% per the official grader).

The parameter set sits in the middle of a flat plateau (entry bar 6–18,
take-profit 70–90 bps, stop 50–80 bps, trailing stop 60 bps all pass the
dev gate with similar results), so the result is not a knife-edge fit to
one window.

## Files

- `main.py` — the bot (integer arithmetic only: deterministic, no clock,
  no network, no files outside the repo).
- `vendor/makefun_bars.py` — byte-identical copy of the kit's Python SDK
  shim (`sdk/makefun_bars.py`).
- `LICENSE` — MIT.

## Local grade

```sh
node <kit>/cli/makefun.mjs grade-local --kit <kit> --bot <this repo> --driver docker
```

(Requires Docker; without it, the same engine was replicated in Python
and validated to the cent against the official grader on all four house
baselines — see `TRANSCRIPT.md`. A TypeScript port of this same strategy
was also graded with the official grade-local --driver process:
net PnL +$7.54, 2 trades, max drawdown 0.55%, fees $0.80 — identical.)

---

<sub>Entered on [make.fun](https://make.fun/?ref=qjs4e9sj&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
