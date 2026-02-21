from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field

Number = Union[int, float]
Direction = Literal["asc", "desc", "none"]


class SourceInfo(BaseModel):
    name: str = "estjt"
    url: str = "https://www.estjt.ir/price/"
    fetchedAt: str


class PriceCell(BaseModel):
    value: Optional[Number] = None
    raw: str


class PriceCellWithCurrency(PriceCell):
    currency: Optional[str] = None


class ChangeCell(BaseModel):
    value: Optional[Number] = None
    percent: Optional[float] = None
    direction: Direction = "none"
    raw: str


class GoldItem(BaseModel):
    type: str
    current: PriceCellWithCurrency
    high: PriceCell
    low: PriceCell
    yesterdayAvg: PriceCellWithCurrency
    change: ChangeCell


class CoinItem(BaseModel):
    type: str
    current: PriceCell
    high: PriceCell
    low: PriceCell
    yesterdayAvg: PriceCell
    change: ChangeCell


class PricesResult(BaseModel):
    source: SourceInfo
    gold: list[GoldItem] = Field(default_factory=list)
    coin: list[CoinItem] = Field(default_factory=list)


class GoldResult(BaseModel):
    source: SourceInfo
    gold: list[GoldItem] = Field(default_factory=list)


class CoinResult(BaseModel):
    source: SourceInfo
    coin: list[CoinItem] = Field(default_factory=list)


class BaseResponse(BaseModel):
    code: int
    message: str
    referenceId: str
    result: Optional[Any] = None

