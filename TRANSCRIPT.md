# Build log — btc-race-24h-20261117-0603 entry

Session: 17 Nov 2026, ~13:34–14:30 WIB. Builder: Muse (Meta AI agent,
working for Andi / @Bradestudio). No submission was made in this session;
the entry was built and graded locally only. A GitHub repository (public,
created by Andi after the competition opened) and Andi's confirmation are
still needed before any submit.

## Bounty (from make.fun API list snapshot, 17 Nov 2026 13:34 WIB)

- Slug: btc-race-24h-20261117-0603 — "Race a BTC trading bot live for 24 hours"
- Free (entry fee $0), prize pool $250 (1st $60, 2nd $40, 3rd $30, 4th $25,
  5th $20, 6th–10th $15 each), escrow funded on Solana.
- Deadline: 17 Nov 2026 19:03 WIB (12:03 UTC). Race: 17 Nov 19:18 WIB –
  18 Nov 19:18 WIB (24h, 1,440 one-minute bars).
- Bot trades cbBTC/USDC (Orca Whirlpool) with $1,000 paper money, long
  only. Dev gate: net PnL > $0 on the frozen 24h dev window. Race
  guardrails: ≥1 trade, max drawdown ≤25%.
- Note: GET /api/competitions/btc-race-24h-20261117-0603 returned 404 even
  though the slug is in the list endpoint; the kit was downloaded from
  https://make.fun/c/btc-race-24h-20261117-0603/kit instead.

## Kit

- Downloaded to ~/workspace/makefun/btc-race-24h-20261117-0603-kit/
  (7.28 MB tarball, kit format agent-fun/kit/v1, harness bars-replay/v1).
- Read RULES.txt (81,931 bytes), the Python SDK shim
  (sdk/makefun_bars.py), the six baseline bots, and the harness source
  (sim/bars/engine.ts) for the exact fill/decision math.
- Captured the exact wire format with a spy bot through the official
  grade-local (process driver): hello (no warmup_bars), batches seq
  0–1439, done seq 1440.

## Official baseline grades (kit grade-local, --driver process)

Dev window, 1,440 bars, 16 Nov 06:04 UTC – 17 Nov 06:03 UTC
(price $64,461 → $64,776, +0.49%; range $63,874–$65,466):

| Baseline | Net PnL | Trades | Max DD | Fees |
| --- | --- | --- | --- | --- |
| buy-and-hold | +$1.07 | 1 | 2.12% | $0.80 |
| momentum (house) | +$2.45 | 1 | 2.12% | $0.80 |
| hold-cash | $0.00 | 0 | 0% | $0 |
| ema-cross | −$106.22 | 68 | 10.96% | $25.74 |
| rsi-bollinger | −$24.25 | 11 | 2.79% | $4.75 |
| adx-momentum | −$32.66 | 26 | 3.60% | $10.26 |

## Simulator validation

A Python replica of the engine (exact integer fill math from engine.ts:
fee 4 bps, slippage 2 bps, constant-product impact vs o_depth, max
slippage vs latest close, decision checks, end flatten) reproduced all
four graded baselines EXACTLY (PnL to the cent, trades, max drawdown,
fees). Docker is not installed on this machine, so the official
grade-local --driver docker could not be run for the Python bot; the
replica + a protocol-driver test of the real main.py (below) is the
verification used instead.

## Strategy search

- Data: dev window (kit) + 13 out-of-sample 24h windows of Binance
  BTC/USDT 1-minute klines, 9–16 Nov 2026 (a down week: BTC fell ~10%).
  OOS fills used the dev window's pool depths, cycled.
- ~2,600 parameter combinations across families: Donchian breakout,
  EMA cross, RSI/Bollinger mean reversion, dip-buy in uptrend, momentum
  threshold, volatility breakout, rally ignition, early entry + exits.
- Findings:
  - 1-minute signals whipsaw: EMA-cross and RSI/Bollinger lose heavily.
  - Breakouts (Donchian) lose on the down week (0/13 positive windows).
  - Re-entry hurts: in a down week every re-entry is another stopped-out
    loss (median −$15 to −$20 vs −$6.43 one-shot).
  - One-shot early entry + tight take-profit/stop/trailing-stop is the
    robust shape: worst out-of-sample loss ≈ −$8, max drawdown ≈ 1%,
    vs −$77 for buy-and-hold on the worst window.
  - Final parameters sit in a flat plateau (entry bar 6–18, TP 70–90 bps,
    stop 50–80 bps, trail 60 bps all pass the dev gate similarly).

## Final bot (main.py)

- Buy all cash on batch 12 (retry to batch 60 if rejected).
- Sell all when value ≥ cost × 1.0090 (TP +0.90%), or ≤ cost × 0.9940
  (stop −0.60%), or ≤ peak × 0.9940 (trail −0.60%). Then stay in cash.
- Integer arithmetic only; deterministic; max_slippage_bps 100 (largest
  1-minute open-vs-close gap seen across dev + OOS data is 16.3 bps).

## Local grade of the final bot

- Simulator (exact replica): dev net PnL +$7.54, 2 trades (buy filled
  bar 13 @ $64,379.06, sell filled bar 113 @ $64,916.37 on the +0.90% TP),
  max drawdown 0.50%, fees $0.80. Dev gate PASSED.
- Protocol-driver test of the real main.py as a subprocess over NDJSON
  (exact hello/batches from the kit): same +$7.54, replies byte-identical
  across two runs (deterministic).
- Official grade-local cross-check: a TypeScript port of the same
  strategy, same constants, graded with the kit's own
  `grade-local --kit . --bot <port> --driver process`: net PnL +$7.539,
  2 trades, max drawdown 0.55%, fees $0.803, status finished, no error.
  (Docker is not installed on this machine, so the Python bot itself
  could not be run through --driver docker; the port + the exact-match
  simulator + the protocol test together are the verification.)
- Out-of-sample (13 windows): median −$6.43, mean −$4.57, worst −$8.23,
  2/13 positive, max drawdown ≤1.1%.

## Status

READY to submit once Andi creates the public GitHub repo and confirms.
Do NOT submit from this session: no repo exists yet, no submit was run.
