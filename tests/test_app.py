import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

import pytest  # noqa: E402

import app as appmod  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    calls = []

    def fake_fetch(symbol):
        calls.append(symbol)
        return 77.456 if symbol == "ABUK.CA" else None

    monkeypatch.setattr(appmod, "fetch_stock_data_with_suffix", fake_fetch)
    monkeypatch.setattr(appmod, "fetch_tradingview_price", lambda t: None)
    monkeypatch.setattr(appmod, "find_cairo_ticker_via_yf_search", lambda q: None)
    appmod.cache.clear()
    c = appmod.app.test_client()
    c.calls = calls
    return c


def test_valid_ticker_returns_rounded_price(client):
    r = client.get("/EGX/abuk")
    assert r.status_code == 200
    assert r.get_data(as_text=True) == "77.46"


def test_unknown_ticker_is_404_and_cached(client):
    assert client.get("/EGX/KORA").status_code == 404
    assert client.get("/EGX/KORA").status_code == 404
    assert client.calls == ["KORA.CA"]  # second call served from the cache


@pytest.mark.parametrize("bad", ["A" * 13, "AB-CD", "AB.CD", "AB%20CD", "a_b", "%00"])
def test_invalid_ticker_never_reaches_upstream(client, bad):
    r = client.get("/EGX/" + bad)
    assert r.status_code == 404
    assert client.calls == []


def test_tradingview_price_preferred_over_yahoo(client, monkeypatch):
    monkeypatch.setattr(appmod, "fetch_tradingview_price", lambda t: 128.224)
    r = client.get("/EGX/COMI")
    assert r.get_data(as_text=True) == "128.22"
    assert client.calls == []  # Yahoo not consulted


def test_falls_back_to_yahoo_when_tradingview_fails(client):
    r = client.get("/EGX/ABUK")
    assert r.get_data(as_text=True) == "77.46"
    assert client.calls == ["ABUK.CA"]
