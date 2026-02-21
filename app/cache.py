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
        self._stale_key = f"{self._key}:stale"
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

        return self._get_by_key(self._key)

    def get_stale(self) -> PricesResult | None:
        if not self._client:
            return None

        return self._get_by_key(self._stale_key)

    def _get_by_key(self, key: str) -> PricesResult | None:
        if not self._client:
            return None

        try:
            payload = self._client.get(key)
        except RedisError:
            logger.warning("Redis read failed for key '%s'.", key, exc_info=True)
            return None

        if not payload:
            return None

        try:
            return PricesResult.model_validate_json(payload)
        except Exception:
            logger.warning("Cached payload for key '%s' was invalid and ignored.", key, exc_info=True)
            return None

    def set(self, prices: PricesResult) -> None:
        if not self._client:
            return

        try:
            payload = prices.model_dump_json()
            with self._client.pipeline() as pipe:
                pipe.setex(self._key, self._ttl, payload)
                pipe.set(self._stale_key, payload)
                pipe.execute()
        except RedisError:
            logger.warning("Redis write failed; continuing without cache.", exc_info=True)

    def close(self) -> None:
        if not self._client:
            return

        try:
            self._client.close()
        except RedisError:
            logger.warning("Redis connection close failed.", exc_info=True)
