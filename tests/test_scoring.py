from bot.scoring import fabio_score


def test_scoring_grade_a():
    res = fabio_score(
        "BTCUSDT",
        trend=True,
        macd_hist=1.0,
        rsi=40,
        vwap_prox=0.001,
        spread=0.001,
        volume=1.0,
    )
    assert res.grade == "A"
