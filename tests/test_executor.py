import math

from bot.executor import _quantize, size_position
from bot.symbols import SymbolFilters
from bot.config import Config


def test_quantize_floor():
    assert math.isclose(_quantize(1.2345, 0.01), 1.23)


def test_size_position_respects_filters():
    cfg = Config()
    filters = {
        "BTCUSDT": SymbolFilters(
            tick_size=0.01, step_size=0.00001, min_qty=0.00001, min_notional=5.0
        )
    }
    qty, reason = size_position("BTCUSDT", 20000, cfg, filters)
    assert reason == ""
    assert qty > 0
