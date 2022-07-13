"""Cash Adjuster Module"""

from decimal import Decimal

from django.db import IntegrityError

from api.models import (
    FX, Bond, Desk, Trader, Book, BondRecord, EventLog, EventExceptionLog
)
from util.common_types import TradeEvent
from util.trade_exceptions import TradeException
from util.singleton import Singleton

class CashAdjuster(metaclass=Singleton):
    """Cash Adjuster class that handles cash adjustment and logging of events.
    Singleton implementation so the API functions work like static methods.
    """
    def __init__(self):
        pass

    def _adjust_cash(self, value: Decimal, desk: Desk, event: TradeEvent) -> None:
        if event['BuySell'] == 'buy':
            desk.cash -= value
        elif event['BuySell'] == 'sell':
            desk.cash += value
        desk.updated = int(event['EventID'])
        desk.save()

    def _log_exception(
        self,
        event: TradeEvent,
        desk: Desk,
        trader: Trader,
        book: Book,
        bond: Bond,
        exclusion_type: str,
    ) -> None:
        """Log excluded event by creating an entry in DB table `EventExceptionLog`."""
        try :
            EventExceptionLog.objects.create(
                event_id=int(event['EventID']),
                desk_id=desk,
                trader_id=trader,
                book_id=book,
                buy_sell=event['BuySell'],
                quantity=int(event['Quantity']),
                bond_id=bond,
                price=bond.price,  # None if bond does not have a price
                exclusion_type=exclusion_type,
            )
        except IntegrityError:
            # TODO: Implement handling of duplicate entries
            pass

    def _adjust_position(self, event: TradeEvent, bond_record: BondRecord) -> None:
        if event['BuySell'] == 'buy':
            bond_record.position += int(event['Quantity'])
        elif event['BuySell'] == 'sell':
            bond_record.position -= int(event['Quantity'])
        bond_record.save()

    def _log_successful_trade_event(
        self,
        event: TradeEvent,
        trade_value: Decimal,
        desk: Desk,
        trader: Trader,
        book: Book,
        bond: Bond,
        bond_record: BondRecord,
        fx: FX,
    ) -> None:
        """Log event by creating an entry in DB table `EventLog`."""
        try:
            EventLog.objects.create(
                event_id=int(event['EventID']),
                desk_id=desk,
                trader_id=trader,
                book_id=book,
                buy_sell=event['BuySell'],
                quantity=int(event['Quantity']),
                bond_id=bond,
                position=bond_record.position,
                price=bond.price,
                fx_rate=fx.rate,
                value=trade_value,
                cash=desk.cash,
            )
        except IntegrityError:
            # TODO: Implement handling of duplicate entries
            pass

    def _process_log_event(
        self,
        event: TradeEvent,
        trade_value: Decimal = None,
        exception: TradeException = None,
    ) -> None:
        """Helper function to first get necessary model entries,
        then log the trade events.
        """
        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        fx: FX = bond.currency
        desk: Desk = Desk.objects.get(desk_id=event['Desk'])
        trader: Trader = Trader.objects.get_or_create(
            trader_id=event['Trader'],
            desk_id=desk
        )[0]
        book: Book = Book.objects.get_or_create(
            book_id=event['Book'],
            trader_id=trader
        )[0]

        # Logging exception first to reduce the number of database queries
        if exception:
            self._log_exception(
                event=event,
                desk=desk,
                trader=trader,
                book=book,
                bond=bond,
                exclusion_type=exception.name,
            )
            return

        bond_record: BondRecord = BondRecord.objects.get_or_create(
                trader_id=trader,
                book_id=book,
                bond_id=bond,
        )[0]
        self._adjust_position(event=event, bond_record=bond_record)

        if trade_value:
            self._log_successful_trade_event(
                event=event,
                trade_value=trade_value,
                desk=desk,
                trader=trader,
                book=book,
                bond=bond,
                bond_record=bond_record,
                fx=fx,
            )

    def adjust_cash_and_log_event(self, event: TradeEvent, value: Decimal) -> None:
        """API function to adjust cash and log the event."""
        self._adjust_cash(
            value=value,
            desk=Desk.objects.get(desk_id=event['Desk']),
            event=event,
        )
        self._process_log_event(event=event, trade_value=value)

    def log_event_with_exception(self, event: TradeEvent, exception: TradeException) -> None:
        """API function to log event with an exception."""
        self._process_log_event(event=event, exception=exception)
