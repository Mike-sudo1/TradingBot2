import math

from bot.symbols import SymbolCache, SymbolFilters


def test_format_qty_and_validate():
    cache = SymbolCache({
        "BTCUSDT": SymbolFilters(tick_size=0.01, step_size=0.001, min_qty=0.001, min_notional=10)
    })
    assert math.isclose(cache.format_qty("BTCUSDT", 0.00123), 0.001, rel_tol=1e-9)
    assert cache.validate("BTCUSDT", 0.001, 20000)
