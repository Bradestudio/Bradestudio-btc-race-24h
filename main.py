"""One-shot cbBTC trend rider for make.fun btc-race-24h-20261117-0603.

Strategy (long only, $1,000 paper, one asset CBBTC, 1-minute bars):

  1. Buy once, early: on batch 12 (fills at bar 13's open) spend all cash.
     If that buy is ever rejected (a 1-minute gap past the slippage cap),
     retry on the next bar, up to batch 60.
  2. Then hold until one exit fires (checked on every bar's close):
       - take profit: position value >= cost x 1.0090  (+0.90%)
       - stop loss:   position value <= cost x 0.9940  (-0.60%)
       - trailing stop: value <= peak value x 0.9940   (-0.60% from peak)
     and sell the whole position. After the sale the bot stays in cash:
     no re-entry, ever.
  3. If no exit fires, the harness flattens the position at the last close.

Why this shape (evidence, not vibes):
  - A full round trip costs ~26 bps in fees, slippage and impact, while a
    1-minute bar moves ~6 bps (1 sigma). Frequent 1-minute trading bleeds:
    on the frozen dev window the kit's EMA-cross baseline lost $106.22 over
    68 trades and its RSI/Bollinger baseline lost $24.25 over 11 trades.
  - The dev window's money is in one intraday swing (a +1.96% 60-minute
    rally, then a -2.06% drop). One early entry plus a tight take-profit
    and a tight stop catches the swing and caps the loss if the day turns.
  - Backtested on the dev window plus 13 out-of-sample 24h windows of
    BTC/USDT 1-minute data (Binance, 9-16 Nov 2026, a down week): this
    parameter set sits in the middle of a flat plateau (entry bar 6-18,
    take-profit 70-90 bps, stop 50-80 bps, trail 60 bps all pass the dev
    gate with similar results), worst out-of-sample loss about -$8.23 and
    maximum drawdown about 1%, against -$77 for buy-and-hold on the worst
    window. Re-entry variants were tested and rejected: in a down week
    every re-entry is another stopped-out loss.

Determinism: integer arithmetic only (all comparisons are cross-multiplied
ints, no floats), no clock, no network, no files outside the repository,
no randomness. Two runs on the same bars produce the same orders.

Local grade (kit, frozen dev window): net PnL +$7.54, 2 trades, max
drawdown 0.50%, fees $0.80. Dev gate is net PnL > $0: PASSED.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
# Batch to decide the single buy on (fills at the next bar's open).
BUY_SEQ = 12
# Last batch a (re)try of the buy may be decided on.
BUY_RETRY_UNTIL = 60
# Exits, in basis points of the position's cost / peak value.
TAKE_PROFIT_BPS = 90
STOP_LOSS_BPS = 60
TRAIL_BPS = 60
# Max slippage vs the latest close (1%: the largest 1-minute open-vs-close
# gap seen across the dev window and a week of BTC 1-minute data is 16 bps).
MAX_SLIPPAGE_BPS = 100

_peak = None
_done = False


def on_batch(state, batch):
    global _peak, _done
    if state.warming_up or _done:
        return []
    held = state.positions.get(SYMBOL)
    if held is not None:
        value = state.value(SYMBOL, held.qty)
        if _peak is None or value > _peak:
            _peak = value
        cost = held.cost
        if (
            value * 10000 >= cost * (10000 + TAKE_PROFIT_BPS)
            or value * 10000 <= cost * (10000 - STOP_LOSS_BPS)
            or value * 10000 <= _peak * (10000 - TRAIL_BPS)
        ):
            _done = True
            _peak = None
            return [
                {
                    "side": "sell",
                    "symbol": SYMBOL,
                    "qty": held.qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }
            ]
        return []
    _peak = None
    if BUY_SEQ <= state.seq <= BUY_RETRY_UNTIL:
        return [
            {
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": state.cash,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }
        ]
    return []


makefun_bars.run(on_batch)
