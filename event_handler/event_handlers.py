"""Module to process new events."""

from decimal import Decimal
from collections import defaultdict, deque
from typing import Deque, Dict

from api.models import (
    FX, Bond, Desk, Trader, Book, BondRecord, EventLog, EventExceptionLog
)
from event_generator.event_generator import EventGenerator
from util.common_types import Event, TradeEvent, PriceEvent, FXEvent
from util.trade_exceptions import (
    TradeException, CashBalanceException, BondNotFoundException
)
from util.singleton import Singleton


class EventHandler(metaclass=Singleton):
    """Class to handle events."""
    _latest_event_id: int = 0

    # Contains events that are withheld because the bond price is not yet known
    # Implemented with a dict of `deque`s, where the key is the bond_id
    _withheld_buy_orders: Dict[str, Deque[TradeEvent]] = None

    def __init__(self):
        self._withheld_buy_orders = defaultdict(lambda: deque(maxlen=None))
        self.market_data_producer, self.trade_event_producer = \
            EventGenerator().get_data_producers()

    def _process_fx_event(self, event: FXEvent) -> None:
        """Helper function to process FX event."""
        fx: FX = FX.objects.get(currency=event['ccy'])
        fx.rate = Decimal(event['rate'])
        fx.updated = event['EventID']
        fx.save()
        self._update_id(event)

    def _process_price_event(self, event: PriceEvent) -> None:
        """Helper function to process price event."""
        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        bond.price = Decimal(event['MarketPrice'])
        bond.updated = event['EventID']
        bond.save()
        self._update_id(event)
        self._handle_withheld_buy_orders(bond.bond_id)

    def _handle_withheld_buy_orders(self, bond_id: str) -> None:
        """Helper function to process withheld buy orders
        where the bond price is now known from a recent price event.

        @param `bond_id`: The bond_id of the bond whose price is now known.
        """
        if self._withheld_buy_orders[bond_id]:
            for event in self._withheld_buy_orders[bond_id]:
                self._process_buy(event)
            del self._withheld_buy_orders[bond_id]  # queue is no longer needed

    def _process_trade_event(self, event: TradeEvent) -> None:
        """Helper function to process trade event."""
        if event['BuySell'] == 'buy':
            try:
                self._process_buy(event)
            except CashBalanceException as e:
                self._log_trade_event_exception(event, e)
                print(e)
        elif event['BuySell'] == 'sell':
            try:
                self._process_sell(event)
            except BondNotFoundException as e:
                self._log_trade_event_exception(event, e)
                print(e)
        else:
            raise ValueError(f'Unknown buy/sell: {event["BuySell"]}')

    def _process_buy(self, event: TradeEvent) -> None:
        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        fx: FX = bond.currency
        if not bond.price:
            # No price yet, so withhold buy order
            self._withheld_buy_orders[bond.bond_id].append(event)
            return

        desk: Desk = Desk.objects.get(desk_id=event['Desk'])
        cash_required = Decimal(event['Quantity']) * bond.price / fx.rate
        # print(cash_required, desk.cash)
        if desk.cash.compare(cash_required) < 0:
            raise CashBalanceException(event['EventID'])

        desk.cash -= cash_required
        desk.updated = event['EventID']
        desk.save()

        self._update_id(event)
        self._log_processed_trade_event(event, trade_value=cash_required)

    def _process_sell(self, event: TradeEvent) -> None:
        """Helper function to process sell event."""
        bond_record_exists: bool = BondRecord.objects.filter(
            trader_id=event['Trader'],
            book_id=event['Book'],
            bond_id=event['BondID'],
        ).exists()
        if not bond_record_exists:
            raise BondNotFoundException(event['EventID'])

        bond: Bond = Bond.objects.get(bond_id=event['BondID'])
        fx: FX = bond.currency
        desk: Desk = Desk.objects.get(desk_id=event['Desk'])
        trade_value = Decimal(event['Quantity']) * bond.price / fx.rate

        # print(trade_value, desk.cash)
        desk.cash += trade_value
        desk.updated = event['EventID']
        desk.save()

        self._update_id(event)
        self._log_processed_trade_event(event, trade_value=trade_value)

    def _log_processed_trade_event(
        self, event: TradeEvent, trade_value: Decimal
    ) -> None:
        """Helper function to log trade events."""
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
        bond_record: BondRecord = BondRecord.objects.get_or_create(
                trader_id=trader,
                book_id=book,
                bond_id=bond,
        )[0]
        if event['BuySell'] == 'buy':
            bond_record.position += event['Quantity']
        elif event['BuySell'] == 'sell':
            bond_record.position -= event['Quantity']
        bond_record.save()

        EventLog.objects.create(
            event_id=event['EventID'],
            desk_id=desk,
            trader_id=trader,
            book_id=book,
            buy_sell='B' if event['BuySell'] == 'buy' else 'S',
            quantity=event['Quantity'],
            bond_id=bond,
            position=bond_record.position,
            price=bond.price,
            fx_rate=fx.rate,
            value=trade_value,
            cash=desk.cash,
        )

    def _log_trade_event_exception(
        self, event: TradeEvent, exception: TradeException
    ) -> None:
        """Helper function to log trade event exception."""
        EventExceptionLog.objects.create(
            event_id=event['EventID'],
            exception_name=exception.name,
        )

    def _process_event(self, event: Event) -> None:
        """Helper function to process event."""
        if 'EventType' in event:
            if event['EventType'] == 'FXEvent':
                self._process_fx_event(event)
            elif event['EventType'] == 'PriceEvent':
                self._process_price_event(event)
            elif event['EventType'] == 'TradeEvent':
                self._process_trade_event(event)
            else:
                raise ValueError(f'Unknown event type: {event["EventType"]}')
        else:
            raise ValueError(f'Unknown event: {event}')

    def _update_id(self, event: Event) -> None:
        """Helper function to latest event id."""
        if event['EventID'] > self._latest_event_id:
            self._latest_event_id = event['EventID']

    def get_latest_event_id(self) -> int:
        """API function to get id of the latest event that has been processed.
        Mainly for use in report generator.
        """
        return self._latest_event_id

    def handle_event(self, event: Event) -> None:
        """API function to handle event."""
        self._process_event(event)

    # def start(self) -> None:
    #     """Helper function to process events.
    #     Alternates between getting an event from the market data producer and
    #     getting an event from the trade event producer.
    #     Then calls API to process the event.
    #     """
    #     MARKET: bool = True
    #     TRADE: bool = not MARKET
    #     while self.market_data_producer.has_next() or \
    #             self.trade_event_producer.has_next():
    #         if MARKET and self.market_data_producer.has_next():
    #             event = self.market_data_producer.publish()
    #         elif TRADE and self.trade_event_producer.has_next():
    #             event = self.trade_event_producer.publish()
    #         self._process_event(event)
    #         MARKET, TRADE = not MARKET, not TRADE
