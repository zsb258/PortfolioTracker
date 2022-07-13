"""Module to process new events."""

from decimal import Decimal
from typing import Callable, Dict

from api.models import FX, Bond, Desk, BondRecord
from .cash_adjuster import CashAdjuster
from util.common_types import Event, TradeEvent, PriceEvent, FXEvent
from util.trade_exceptions import (
    NoMarketPriceException,
    CashOverlimitException,
    QuantityOverlimitException,
)
from util.singleton import Singleton


class EventHandler(metaclass=Singleton):
    """Class to handle events."""
    _latest_event_id: int = 0

    def __init__(self):
        pass

    def _process_fx_event(self, event: FXEvent) -> None:
        """Helper function to process FX event."""
        fx: FX = FX.objects.get(currency=event['ccy'])
        fx.rate = Decimal(event['rate'])
        fx.updated = int(event['EventID'])
        fx.save()
        self._update_id(event)

    def _process_price_event(self, event: PriceEvent) -> None:
        """Helper function to process price event."""
        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        bond.price = Decimal(event['MarketPrice'])
        bond.updated = int(event['EventID'])
        bond.save()
        self._update_id(event)

    def _process_trade_event(self, event: TradeEvent) -> None:
        """Helper function to process trade event."""
        if event['BuySell'] == 'buy':
            try:
                self._process_buy(event)
            except (CashOverlimitException, NoMarketPriceException) as e:
                CashAdjuster().log_event_with_exception(event, exception=e)
        elif event['BuySell'] == 'sell':
            try:
                self._process_sell(event)
            except QuantityOverlimitException as e:
                CashAdjuster().log_event_with_exception(event, exception=e)
        else:
            raise ValueError(f'Unknown buy/sell: {event["BuySell"]}')

    def _process_buy(self, event: TradeEvent) -> None:
        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        if not bond.price:
            raise NoMarketPriceException(int(event['EventID']))

        fx: FX = bond.currency
        desk: Desk = Desk.objects.get(desk_id=event['Desk'])
        cash_required = Decimal(event['Quantity']) * bond.price / fx.rate
        if desk.cash.compare(cash_required) < 0:
            raise CashOverlimitException(event['EventID'])

        CashAdjuster().adjust_cash_and_log_event(value=cash_required, event=event)
        self._update_id(event)

    def _process_sell(self, event: TradeEvent) -> None:
        """Helper function to process sell event."""
        bond_record_exists: bool = BondRecord.objects.filter(
            trader_id=event['Trader'],
            book_id=event['Book'],
            bond_id=event['BondID'],
        ).exists()
        if not bond_record_exists:
            raise QuantityOverlimitException(event['EventID'])

        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        fx: FX = bond.currency
        trade_value = Decimal(event['Quantity']) * bond.price / fx.rate

        CashAdjuster().adjust_cash_and_log_event(value=trade_value, event=event)
        self._update_id(event)

    def _process_event(self, event: Event) -> None:
        """Helper function to process event according to event type."""
        event_to_function_map: Dict[str, Callable] = {
            'FXEvent': self._process_fx_event,
            'PriceEvent': self._process_price_event,
            'TradeEvent': self._process_trade_event,
        }
        if event['EventType'] in event_to_function_map:
            event_to_function_map[event['EventType']](event)
        else:
            raise ValueError(f'Unknown event: {event}')

    def _update_id(self, event: Event) -> None:
        """Helper function to update latest event id."""
        if int(event['EventID']) > self._latest_event_id:
            self._latest_event_id = int(event['EventID'])

    def get_latest_event_id(self) -> int:
        """API function to get id of the latest event that has been processed.
        Mainly for use in report generator.
        """
        return self._latest_event_id

    def handle_event(self, event: Event) -> None:
        """API function to handle event."""
        self._process_event(event)

