from __future__ import annotations

import os
from dataclasses import dataclass


def _to_bool(value: str | None) -> bool:
    if value is None:
        raise ValueError("Missing required environment value.")
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def _to_int(value: str | None, minimum: int = 1) -> int:
    if value is None:
        raise ValueError("Missing required environment value.")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer value: {value!r}") from exc
    return max(minimum, parsed)


def _to_float(value: str | None, minimum: float = 0.01) -> float:
    if value is None:
        raise ValueError("Missing required environment value.")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid float value: {value!r}") from exc
    return max(minimum, parsed)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    cache_enabled: bool
    cache_ttl_seconds: int
    cache_key_prices: str
    redis_url: str
    redis_connect_timeout_seconds: float
    redis_socket_timeout_seconds: float


settings = Settings(
    cache_enabled=_to_bool(_require_env("CACHE_ENABLED")),
    cache_ttl_seconds=_to_int(_require_env("CACHE_TTL_SECONDS")),
    cache_key_prices=_require_env("CACHE_KEY_PRICES"),
    redis_url=_require_env("REDIS_URL"),
    redis_connect_timeout_seconds=_to_float(_require_env("REDIS_CONNECT_TIMEOUT_SECONDS")),
    redis_socket_timeout_seconds=_to_float(_require_env("REDIS_SOCKET_TIMEOUT_SECONDS"))
)
