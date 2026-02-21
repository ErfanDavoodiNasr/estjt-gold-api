from __future__ import annotations

import logging

from redis import Redis
from redis.exceptions import RedisError

from app.models import PricesResult
from app.settings import settings

logger = logging.getLogger(__name__)


class PricesCache:
    def __init__(self) -> None:
        self._enabled = settings.cache_enabled
        self._ttl = settings.cache_ttl_seconds
        self._key = settings.cache_key_prices
        self._client: Redis | None = None

        if self._enabled:
            try:
                self._client = Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=settings.redis_connect_timeout_seconds,
                    socket_timeout=settings.redis_socket_timeout_seconds,
                )
            except (RedisError, ValueError):
                logger.warning("Redis client initialization failed; cache disabled.", exc_info=True)
                self._client = None

    def get(self) -> PricesResult | None:
        if not self._client:
            return None

        try:
            payload = self._client.get(self._key)
        except RedisError:
            logger.warning("Redis read failed; serving fresh data.", exc_info=True)
            return None

        if not payload:
            return None

        try:
            return PricesResult.model_validate_json(payload)
        except Exception:
            logger.warning("Cached payload was invalid and ignored.", exc_info=True)
            return None

    def set(self, prices: PricesResult) -> None:
        if not self._client:
            return

        try:
            self._client.setex(self._key, self._ttl, prices.model_dump_json())
        except RedisError:
            logger.warning("Redis write failed; continuing without cache.", exc_info=True)

    def close(self) -> None:
        if not self._client:
            return

        try:
            self._client.close()
        except RedisError:
            logger.warning("Redis connection close failed.", exc_info=True)
