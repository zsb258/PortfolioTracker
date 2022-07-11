"""Module containing custom exceptions
that might raised when handling trade event.
"""

from api.models import EventExceptionLog

class TradeException(Exception):
    """Base class for trade exceptions."""
    name: str = ''

class CashBalanceException(TradeException):
    """Exception raised when cash balance is insufficient for `Buy` event."""
    name: str = EventExceptionLog.TradeExceptionEnum.INSUFFICIENT_CASH
    def __init__(self, event_id: int):
        message = f'Cash balance insufficient for event {event_id}'
        super().__init__(message)

class BondNotFoundException(TradeException):
    """Exception raised when bond is not found for `Sell` event."""
    name: str = EventExceptionLog.TradeExceptionEnum.BOND_NOT_FOUND
    def __init__(self, event_id: int):
        message = f'Bond not found for event {event_id}'
        super().__init__(message)
