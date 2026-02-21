from __future__ import annotations

import os
from dataclasses import dataclass


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _to_int(value: str | None, default: int, minimum: int = 1) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(minimum, parsed)


def _to_float(value: str | None, default: float, minimum: float = 0.01) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError:
        return default
    return max(minimum, parsed)


@dataclass(frozen=True)
class Settings:
    cache_enabled: bool
    cache_ttl_seconds: int
    cache_key_prices: str
    redis_url: str
    redis_connect_timeout_seconds: float
    redis_socket_timeout_seconds: float


settings = Settings(
    cache_enabled=_to_bool(os.getenv("CACHE_ENABLED"), True),
    cache_ttl_seconds=_to_int(os.getenv("CACHE_TTL_SECONDS"), 20),
    cache_key_prices=os.getenv("CACHE_KEY_PRICES", "estjt:prices"),
    redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    redis_connect_timeout_seconds=_to_float(os.getenv("REDIS_CONNECT_TIMEOUT_SECONDS"), 0.4),
    redis_socket_timeout_seconds=_to_float(os.getenv("REDIS_SOCKET_TIMEOUT_SECONDS"), 0.4),
)
