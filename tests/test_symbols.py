import math

from bot.symbols import SymbolCache, SymbolFilters
from bot.executor import format_qty


def test_format_qty_and_min_qty():
    cache = SymbolCache({
        "BTCUSDT": SymbolFilters(tick_size=0.01, step_size=0.001, min_qty=0.001, min_notional=10)
    })
    assert math.isclose(format_qty("BTCUSDT", 0.00123, cache.filters), 0.001, rel_tol=1e-9)
    assert cache.min_qty("BTCUSDT") == 0.001
