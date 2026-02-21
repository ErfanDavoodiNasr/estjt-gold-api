from __future__ import annotations

from typing import Callable
from uuid import uuid4

from fastapi import FastAPI

from app.cache import PricesCache
from app.models import BaseResponse, CoinResult, GoldResult, PricesResult
from app.scraper import EstjtScraper, ScraperError

app = FastAPI(title="Tehran Gold & Coin Prices API", version="1.0.0")
scraper = EstjtScraper()
cache = PricesCache()


def _make_response(code: int, message: str, reference_id: str, result: object | None = None) -> BaseResponse:
    return BaseResponse(code=code, message=message, referenceId=reference_id, result=result)


def _handle_request(selector: Callable[[PricesResult], object]) -> BaseResponse:
    reference_id = str(uuid4())
    try:
        prices = _load_prices()
        payload = selector(prices)
        result = payload.model_dump() if hasattr(payload, "model_dump") else payload
        return _make_response(0, "عملیات موفق بود.", reference_id, result)
    except ScraperError as exc:
        return _make_response(exc.code, exc.message, reference_id, None)
    except Exception:
        return _make_response(1002, "خطای داخلی در پردازش درخواست.", reference_id, None)


def _load_prices() -> PricesResult:
    cached = cache.get()
    if cached is not None:
        return cached

    try:
        fresh = scraper.fetch_prices()
    except ScraperError:
        stale = cache.get_stale()
        if stale is not None:
            return stale
        raise

    cache.set(fresh)
    return fresh


@app.on_event("shutdown")
def shutdown_event() -> None:
    cache.close()


@app.get("/v1/prices", response_model=BaseResponse)
def get_prices() -> BaseResponse:
    return _handle_request(lambda prices: prices)


@app.get("/v1/prices/gold", response_model=BaseResponse)
def get_gold_prices() -> BaseResponse:
    return _handle_request(lambda prices: GoldResult(source=prices.source, gold=prices.gold))


@app.get("/v1/prices/coin", response_model=BaseResponse)
def get_coin_prices() -> BaseResponse:
    return _handle_request(lambda prices: CoinResult(source=prices.source, coin=prices.coin))
