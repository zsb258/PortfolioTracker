"""Module to process new events."""

from decimal import Decimal
import heapq
from typing import Callable, Dict, List, Tuple

from django.db.models import QuerySet

from api.models import FX, Bond, Desk, BondRecord, FxEventLog, PriceEventLog
from util.common_types import Event, TradeEvent, PriceEvent, FXEvent
from util.trade_exceptions import (
    NoMarketPriceException,
    CashOverlimitException,
    QuantityOverlimitException,
)
from util.singleton import Singleton
from .cash_adjuster import CashAdjuster
from util import common_fns


class EventHandler(metaclass=Singleton):
    """Class to handle events."""
    _queue: List[Tuple[int, Event]] = []

    def __init__(self):
        heapq.heapify(self._queue)

    def _process_fx_event(self, event: FXEvent) -> None:
        """Helper function to process FX event."""
        fx: FX = FX.objects.get(currency_id=event['ccy'])
        fx.rate = Decimal(event['rate'])
        fx.save()
        CashAdjuster().log_market_event(event=event)

    def _process_price_event(self, event: PriceEvent) -> None:
        """Helper function to process price event."""
        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        bond.price = Decimal(event['MarketPrice'])
        if bond.initial_price is None:
            bond.initial_price = bond.price
        bond.save()
        CashAdjuster().log_market_event(event=event)

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

    def _process_sell(self, event: TradeEvent) -> None:
        """Helper function to process sell event."""
        bond_records: QuerySet = BondRecord.objects.filter(
            trader=event['Trader'],
            book=event['Book'],
            bond=event['BondID'],
        )
        if not bond_records.exists():
            raise QuantityOverlimitException(event['EventID'])
        bond_record: BondRecord = bond_records[0]
        if bond_record.position < Decimal(event['Quantity']):
            raise QuantityOverlimitException(event['EventID'])

        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        fx: FX = bond.currency
        trade_value = Decimal(event['Quantity']) * bond.price / fx.rate

        CashAdjuster().adjust_cash_and_log_event(value=trade_value, event=event)

    def _process_event(self, event: Event) -> None:
        """Helper function to process event according to event type.
        Called only after the event sequence has been validated.
        """
        event_to_function_map: Dict[str, Callable] = {
            'FXEvent': self._process_fx_event,
            'PriceEvent': self._process_price_event,
            'TradeEvent': self._process_trade_event,
        }
        if event['EventType'] in event_to_function_map:
            event_to_function_map[event['EventType']](event)
        else:
            raise ValueError(f'Unknown event: {event}')

    def _validate_event_sequence(self, event: Event) -> None:
        if int(event['EventID']) ==  common_fns.get_largest_event_id() + 1:
            self._process_event(event)
        else:
            heapq.heappush(self._queue, (int(event['EventID']), event))

    def _validate_queue(self) -> None:
        """Helper function to process first event in queue."""
        if len(self._queue) > 0:
            while len(self._queue) > 0 and self._queue[0][0] <= common_fns.get_largest_event_id():
                # Pop and discard old events that could be sent in from duplicate requests
                heapq.heappop(self._queue)
        if len(self._queue) > 0:
            while len(self._queue) > 0 and self._queue[0][0] == common_fns.get_largest_event_id() + 1:
                event_id, event = heapq.heappop(self._queue)
                self._process_event(event)

    def handle_event(self, event: Event) -> None:
        """API function to handle event."""
        self._validate_event_sequence(event)
        self._validate_queue()


