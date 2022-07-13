"""Module containing custom exceptions that might raised when handling trade event."""

from api.models import EventExceptionLog

class TradeException(Exception):
    """Base class for trade exceptions."""
    name: str = ''

class NoMarketPriceException(TradeException):
    """Bond market price is not available for `buy` event."""
    name: str = EventExceptionLog.TradeExceptionEnum.NO_MARKET_PRICE
    def __init__(self, event_id: int):
        message = f'Bond price not available for event {event_id}'
        super().__init__(message)

class CashOverlimitException(TradeException):
    """Cash balance is insufficient for `buy` event."""
    name: str = EventExceptionLog.TradeExceptionEnum.CASH_OVERLIMIT
    def __init__(self, event_id: int):
        message = f'Cash balance insufficient for event {event_id}'
        super().__init__(message)

class QuantityOverlimitException(TradeException):
    """Bond quantity is insufficient for `sell` event."""
    name: str = EventExceptionLog.TradeExceptionEnum.QUANTITY_OVERLIMIT
    def __init__(self, event_id: int):
        message = f'Bond quantity insufficient for event {event_id}'
        super().__init__(message)
