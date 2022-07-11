"""Module containing common type definitions."""

from typing import TypedDict, Union

# Type definitions
class _BaseEvent(TypedDict):
    """Base event type."""
    EventID: int
    EventType: str

class PriceEvent(_BaseEvent):
    """TypedDict definition for PriceEvent"""
    BondID: str
    MarketPrice: float

class TradeEvent(_BaseEvent):
    """TypedDict definition for TradeEvent"""
    Desk: str
    Trader: str
    Book: str
    BuySell: str
    Quantity: int
    BondID: str

class FXEvent(_BaseEvent):
    """TypedDict definition for FXEvent"""
    ccy: str
    rate: float

Event = Union[PriceEvent, TradeEvent, FXEvent]
MarketEvent = Union[PriceEvent, FXEvent]
