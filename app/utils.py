from __future__ import annotations

import math
import re
from typing import Optional, Union

Number = Union[int, float]

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_EN_DIGITS = "0123456789"

_DIGIT_TRANS = str.maketrans(
    {**{p: e for p, e in zip(_PERSIAN_DIGITS, _EN_DIGITS)}, **{a: e for a, e in zip(_ARABIC_DIGITS, _EN_DIGITS)}}
)

_DASH_VALUES = {"", "-", "—", "–", "―"}
_NUMERIC_RE = re.compile(r"[-+]?\d[\d,\.٫٬]*")


def normalize_digits(text: str) -> str:
    if text is None:
        return ""
    return text.translate(_DIGIT_TRANS)


def normalize_label(text: str) -> str:
    normalized = normalize_digits(text or "")
    normalized = normalized.replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def clean_text(text: str) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def is_dash_or_empty(text: str) -> bool:
    return clean_text(text) in _DASH_VALUES


def normalize_number_token(text: str) -> str:
    """
    Convert Persian/Arabic digits to English and remove thousands separators.
    Example: ۱۹٫۸۴۱٫۷۰۰ -> 19841700
    """
    token = normalize_digits(clean_text(text))
    token = token.replace("٫", "").replace("٬", "").replace(",", "")
    token = re.sub(r"[^0-9+\-]", "", token)
    return token


def parse_numeric_value(text: str) -> Optional[Number]:
    candidate = extract_numeric_token(text)
    if not candidate:
        return None

    standard = _standardize_numeric_token(candidate)
    if not standard:
        return None

    try:
        value = float(standard)
    except ValueError:
        return None

    if not math.isfinite(value):
        return None
    if value.is_integer():
        return int(value)
    return value


def extract_numeric_token(text: str) -> Optional[str]:
    normalized = normalize_digits(clean_text(text))
    normalized = normalized.replace("−", "-").replace("–", "-")
    match = _NUMERIC_RE.search(normalized)
    if not match:
        return None
    return match.group(0)


def extract_currency_and_value(text: str) -> tuple[Optional[Number], Optional[str]]:
    raw = clean_text(text)
    normalized = normalize_digits(raw)
    match = _NUMERIC_RE.search(normalized)
    if not match:
        return None, None

    token = match.group(0)
    value = parse_numeric_value(token)
    currency = clean_text(normalized[: match.start()] + normalized[match.end() :])
    if currency in _DASH_VALUES:
        currency = None
    return value, currency or None


def parse_change_text(raw_text: str, direction_hint: str = "none") -> dict:
    raw = clean_text(raw_text)
    if is_dash_or_empty(raw):
        return {"value": None, "percent": None, "direction": "none", "raw": raw}

    normalized = normalize_digits(raw)
    percent = None
    value_part = normalized

    percent_match = re.search(r"\(([^)]*)\)", normalized)
    if percent_match:
        percent_value = parse_numeric_value(percent_match.group(1))
        percent = float(percent_value) if percent_value is not None else None
        value_part = normalized[: percent_match.start()]

    value = parse_numeric_value(value_part)
    direction = direction_hint if direction_hint in {"asc", "desc"} else "none"
    if direction == "none":
        if value is None or value == 0:
            direction = "none"
        elif value > 0:
            direction = "asc"
        else:
            direction = "desc"
    elif value is not None:
        if direction == "desc" and value > 0:
            value = -value
        elif direction == "asc" and value < 0:
            value = abs(value)

    return {"value": value, "percent": percent, "direction": direction, "raw": raw}


def _standardize_numeric_token(token: str) -> Optional[str]:
    token = normalize_digits(token or "")
    token = token.replace("٬", ",").replace("٫", ".")
    token = re.sub(r"[^0-9,.\-+]", "", token)
    if not token or token in {"-", "+", ".", ",", "-.", "+.", "-,", "+,"}:
        return None

    sign = ""
    if token[0] in "+-":
        sign = token[0]
        token = token[1:]

    sep_count = token.count(".") + token.count(",")
    if sep_count == 0:
        digits = re.sub(r"[^0-9]", "", token)
        return f"{sign}{digits}" if digits else None

    if sep_count == 1:
        sep = "." if "." in token else ","
        left, right = token.split(sep, 1)
        left_digits = re.sub(r"[^0-9]", "", left)
        right_digits = re.sub(r"[^0-9]", "", right)
        if not left_digits and not right_digits:
            return None
        if right_digits and len(right_digits) <= 2:
            return f"{sign}{left_digits or '0'}.{right_digits}"
        return f"{sign}{left_digits}{right_digits}" or None

    last_dot = token.rfind(".")
    last_comma = token.rfind(",")
    last_sep_index = max(last_dot, last_comma)
    left_part = token[:last_sep_index]
    right_part = token[last_sep_index + 1 :]
    left_digits = re.sub(r"[^0-9]", "", left_part)
    right_digits = re.sub(r"[^0-9]", "", right_part)
    if right_digits and len(right_digits) <= 2 and left_digits:
        return f"{sign}{left_digits}.{right_digits}"
    all_digits = re.sub(r"[^0-9]", "", token)
    return f"{sign}{all_digits}" if all_digits else None
