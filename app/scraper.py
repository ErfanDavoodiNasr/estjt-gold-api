from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

import requests
from bs4 import BeautifulSoup, FeatureNotFound
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.models import CoinItem, GoldItem, PricesResult, SourceInfo
from app.utils import (
    clean_text,
    extract_currency_and_value,
    normalize_label,
    parse_change_text,
    parse_numeric_value,
)

TARGET_URL = "https://www.estjt.ir/price/"

GOLD_TYPES = ["انس طلا", "مظنه تهران", "طلای ۱۸ عیار", "طلای ۲۴ عیار"]
COIN_TYPES = ["سکه طرح قدیم", "سکه طرح جدید", "نیم سکه", "ربع سکه", "سکه یک گرمی"]

GOLD_KEYS = {normalize_label(name) for name in GOLD_TYPES}
COIN_KEYS = {normalize_label(name) for name in COIN_TYPES}


@dataclass
class ScraperError(Exception):
    code: int
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class NetworkError(ScraperError):
    def __init__(self, message: str = "خطا در دریافت اطلاعات از منبع.") -> None:
        super().__init__(1001, message)


class ParseError(ScraperError):
    def __init__(self, message: str = "خطا در پردازش داده‌ها.") -> None:
        super().__init__(1002, message)


class UpstreamChangedError(ScraperError):
    def __init__(self, message: str = "ساختار صفحه منبع تغییر کرده است.") -> None:
        super().__init__(1003, message)

class EstjtScraper:
    def __init__(self, url: str = TARGET_URL, timeout: tuple[int, int] = (3, 6), retries: int = 0) -> None:
        self.url = url
        self.timeout = timeout
        self.session = self._build_session(retries)

    @staticmethod
    def _build_session(retries: int) -> requests.Session:
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_prices(self) -> PricesResult:
        fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        html = self.fetch_html()
        parsed = self.parse_html(html, fetched_at=fetched_at)
        return parsed

    def fetch_html(self) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.estjt.ir/",
            "Connection": "keep-alive",
        }

        try:
            response = self.session.get(self.url, headers=headers, timeout=self.timeout)
        except requests.Timeout as exc:
            raise NetworkError("زمان دریافت اطلاعات از منبع به پایان رسید.") from exc
        except requests.RequestException as exc:
            raise NetworkError("ارتباط با منبع برقرار نشد.") from exc

        if response.status_code in {403, 429}:
            raise NetworkError("دسترسی به منبع محدود شده است.")
        if response.status_code >= 400:
            raise NetworkError("منبع قیمت‌ها در دسترس نیست.")

        html = response.text or ""
        if not html.strip():
            raise ParseError("پاسخ منبع خالی است.")
        if self._looks_like_block_page(html):
            raise NetworkError("منبع درخواست را مسدود کرده است.")
        return html

    @staticmethod
    def _looks_like_block_page(html: str) -> bool:
        body = html.lower()
        patterns = [
            "captcha",
            "cloudflare",
            "access denied",
            "security check",
            "attention required",
        ]
        return any(pattern in body for pattern in patterns)

    def parse_html(self, html: str, fetched_at: str | None = None) -> PricesResult:
        soup = self._build_soup(html)
        tables = soup.find_all("table")
        if not tables:
            raise UpstreamChangedError()

        gold_table, coin_table = self._locate_target_tables(tables)
        if not gold_table or not coin_table:
            raise UpstreamChangedError()

        gold_rows = self._extract_table_rows(gold_table, is_gold=True)
        coin_rows = self._extract_table_rows(coin_table, is_gold=False)

        ordered_gold = self._build_ordered_rows(gold_rows, GOLD_TYPES, "طلا")
        ordered_coin = self._build_ordered_rows(coin_rows, COIN_TYPES, "سکه")

        source = SourceInfo(
            name="estjt",
            url=self.url,
            fetchedAt=fetched_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        return PricesResult(source=source, gold=ordered_gold, coin=ordered_coin)

    @staticmethod
    def _build_soup(html: str) -> BeautifulSoup:
        try:
            return BeautifulSoup(html, "lxml")
        except FeatureNotFound:
            return BeautifulSoup(html, "html.parser")
        except Exception as exc:
            raise ParseError() from exc

    def _locate_target_tables(self, tables: Iterable[Any]) -> tuple[Any | None, Any | None]:
        gold_table = None
        coin_table = None

        for table in tables:
            headers = [normalize_label(th.get_text(" ", strip=True)) for th in table.find_all("th")]
            if not headers:
                continue
            first_header = headers[0]
            if "نوع طلا" in first_header:
                gold_table = table
            elif "نوع سکه" in first_header:
                coin_table = table

        if gold_table and coin_table:
            return gold_table, coin_table

        table_scores: list[tuple[int, int, Any]] = []
        for table in tables:
            types = []
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if not cells:
                    continue
                row_type = normalize_label(cells[0].get_text(" ", strip=True))
                if row_type:
                    types.append(row_type)
            if not types:
                continue
            gold_hits = len(set(types) & GOLD_KEYS)
            coin_hits = len(set(types) & COIN_KEYS)
            table_scores.append((gold_hits, coin_hits, table))

        if not gold_table:
            candidates = [item for item in table_scores if item[0] > 0]
            gold_table = max(candidates, key=lambda x: x[0])[2] if candidates else None
        if not coin_table:
            candidates = [item for item in table_scores if item[1] > 0]
            coin_table = max(candidates, key=lambda x: x[1])[2] if candidates else None

        return gold_table, coin_table

    def _extract_table_rows(self, table: Any, *, is_gold: bool) -> dict[str, GoldItem | CoinItem]:
        rows: dict[str, GoldItem | CoinItem] = {}
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 6:
                continue

            row_type = clean_text(cells[0].get_text(" ", strip=True))
            row_key = normalize_label(row_type)
            if not row_key:
                continue

            current_raw = clean_text(cells[1].get_text(" ", strip=True))
            high_raw = clean_text(cells[2].get_text(" ", strip=True))
            low_raw = clean_text(cells[3].get_text(" ", strip=True))
            yesterday_raw = clean_text(cells[4].get_text(" ", strip=True))
            change_raw = clean_text(cells[5].get_text(" ", strip=True))
            direction = self._extract_direction(cells[5], change_raw)
            change_data = parse_change_text(change_raw, direction_hint=direction)

            if is_gold:
                current_value, current_currency = extract_currency_and_value(current_raw)
                yesterday_value, yesterday_currency = extract_currency_and_value(yesterday_raw)
                row_item: GoldItem | CoinItem = GoldItem(
                    type=row_type,
                    current={"value": current_value, "raw": current_raw, "currency": current_currency},
                    high={"value": parse_numeric_value(high_raw), "raw": high_raw},
                    low={"value": parse_numeric_value(low_raw), "raw": low_raw},
                    yesterdayAvg={
                        "value": yesterday_value,
                        "raw": yesterday_raw,
                        "currency": yesterday_currency,
                    },
                    change=change_data,
                )
            else:
                row_item = CoinItem(
                    type=row_type,
                    current={"value": parse_numeric_value(current_raw), "raw": current_raw},
                    high={"value": parse_numeric_value(high_raw), "raw": high_raw},
                    low={"value": parse_numeric_value(low_raw), "raw": low_raw},
                    yesterdayAvg={"value": parse_numeric_value(yesterday_raw), "raw": yesterday_raw},
                    change=change_data,
                )

            rows[row_key] = row_item

        return rows

    @staticmethod
    def _extract_direction(cell: Any, fallback_raw: str) -> str:
        for element in [cell] + cell.find_all(True):
            classes = element.get("class", [])
            if not classes:
                continue
            if "asc" in classes:
                return "asc"
            if "desc" in classes:
                return "desc"

        raw = clean_text(fallback_raw)
        if raw.startswith("-"):
            return "desc"
        if raw.startswith("+"):
            return "asc"
        return "none"

    def _build_ordered_rows(
        self,
        rows: dict[str, GoldItem | CoinItem],
        expected_types: list[str],
        table_title: str,
    ) -> list[GoldItem | CoinItem]:
        ordered: list[GoldItem | CoinItem] = []
        missing: list[str] = []
        for expected in expected_types:
            key = normalize_label(expected)
            row = rows.get(key)
            if row is None:
                missing.append(expected)
                continue
            ordered.append(row)

        if missing:
            raise UpstreamChangedError(f"ساختار جدول {table_title} تغییر کرده است.")
        return ordered
