"""Module containing common type definitions."""

from typing import TypedDict, Union

# Type definitions
class _BaseEvent(TypedDict):
    """Base event type."""
    EventID: int
    EventType: str

class PriceEvent(_BaseEvent):
    """TypedDict definition for PriceEvent
    EventID: int
    EventType: str
    BondID: str
    MarketPrice: float
    """
    BondID: str
    MarketPrice: float

class TradeEvent(_BaseEvent):
    """TypedDict definition for TradeEvent
    EventID: int
    EventType: str
    Desk: str
    Trader: str
    Book: str
    BuySell: str
    Quantity: int
    BondID: str
    """
    Desk: str
    Trader: str
    Book: str
    BuySell: str
    Quantity: int
    BondID: str

class FXEvent(_BaseEvent):
    """TypedDict definition for FXEvent
    EventID: int
    EventType: str
    ccy: str
    rate: float
    """
    ccy: str
    rate: float

Event = Union[PriceEvent, TradeEvent, FXEvent]
MarketEvent = Union[PriceEvent, FXEvent]
