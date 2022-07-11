from decimal import Decimal

from django.test import TestCase
from django.forms.models import model_to_dict

from event_handler.event_handlers import EventHandler
import api.populate_db as populate_db
from api.models import (
    FX, Bond, Desk, Trader, Book, BondRecord, EventLog, EventExceptionLog
)
from event_generator.event_generator import EventGenerator

sample_market_data = [
    {
        "EventID": 1,
        "EventType": "PriceEvent",
        "BondID": "B34678",
        "MarketPrice": 10000
    },
    {
        "EventID": 3,
        "EventType": "PriceEvent",
        "BondID": "B34678",
        "MarketPrice": 10090
    },
    {
        "EventID": 5,
        "EventType": "FXEvent",
        "ccy": "JPX",
        "rate": 135
    },
    {
        "EventID": 6,
        "EventType": "PriceEvent",
        "BondID": "B34678",
        "MarketPrice": 10100
    },
]

sample_trade_events = [
    {
        "EventID": 2,
        "EventType": "TradeEvent",
        "Desk": "NY",
        "Trader": "T6899554",
        "Book": "NY00",
        "BuySell": "buy",
        "Quantity": 533,
        "BondID": "B34678"
    },
    {
        "EventID": 4,
        "EventType": "TradeEvent",
        "Desk": "NY",
        "Trader": "T6899554",
        "Book": "NY00",
        "BuySell": "sell",
        "Quantity": 33,
        "BondID": "B34678"
    },
]

class EventHandlerTestCase(TestCase):
    def setUp(self) -> None:
        self.event_handler = EventHandler()
        self.event_generator = EventGenerator()
        self.event_generator._reset_for_unittest()

        populate_db._add_fx(filename='example/example_initial_fx.csv')
        populate_db._add_bonds(filename='example/example_bond_details.csv')
        populate_db._add_desks(filename='example/example_initial_cash.csv')

    def test_event_handler_is_singleton(self):
        ins_a = EventHandler()
        ins_b = EventHandler()
        # print(ins_a, ins_b)
        self.assertEqual(ins_a == ins_b, True)

    def test_event_handler_handles_market_data(self):
        self.setUp()
        #1
        event = self.event_generator.publish_next_market_data()
        print(event)
        self.assertDictEqual(event, sample_market_data[0])
        self.event_handler.handle_event(event)
        self.assertEqual(
            Bond.objects.get(bond_id=event['BondID']).price,
            event['MarketPrice'],
        )

        #3
        event = self.event_generator.publish_next_market_data()
        print(event)
        self.assertDictEqual(event, sample_market_data[1])
        self.event_handler.handle_event(event)
        self.assertEqual(
            Bond.objects.get(bond_id=event['BondID']).price,
            event['MarketPrice'],
        )

        #5
        event = self.event_generator.publish_next_market_data()
        print(event)
        self.assertDictEqual(event, sample_market_data[2])
        self.event_handler.handle_event(event)
        self.assertEqual(
            FX.objects.get(currency=event['ccy']).rate,
            event['rate'],
        )

    def test_event_handler_handles_trade_event(self):
        self.setUp()
        #1
        event = self.event_generator.publish_next_market_data()
        self.event_handler.handle_event(event)
        
        #2
        event = self.event_generator.publish_next_trade_event()
        print(event['EventID'])
        self.assertDictEqual(event, sample_trade_events[0])
        self.event_handler.handle_event(event)

        bond = Bond.objects.get(bond_id=event['BondID'])
        val = round(Decimal(event['Quantity']) * bond.price / bond.currency.rate, 5)
        self.assertDictEqual(
            model_to_dict(EventLog.objects.get(event_id=event['EventID'])),
            {
                'event_id': 2,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'B',
                'quantity': 533,
                'bond_id': "B34678",
                'position': 533,
                'price': round(Decimal(10_000), 5),
                'fx_rate': round(Decimal(136.14), 5),
                'value': val,
                'cash': round(Decimal(1_000_000) - val, 5),
            }
        )

        #3
        event = self.event_generator.publish_next_market_data()
        self.event_handler.handle_event(event)

        #4
        event = self.event_generator.publish_next_trade_event()
        print(event['EventID'])
        self.assertDictEqual(event, sample_trade_events[1])
        self.event_handler.handle_event(event)

        bond = Bond.objects.get(bond_id=event['BondID'])
        val = round(Decimal(event['Quantity']) * bond.price / bond.currency.rate, 5)
        print(model_to_dict(EventLog.objects.get(event_id=event['EventID'])))
        self.assertDictEqual(
            model_to_dict(EventLog.objects.get(event_id=event['EventID'])),
            {
                'event_id': 4,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'S',
                'quantity': 33,
                'bond_id': "B34678",
                'position': 500,
                'price': round(Decimal(10_090), 5),
                'fx_rate': round(Decimal(136.14), 5),
                'value': val,
                'cash': round(Decimal(960849.12590) + val, 5),
            }
        )

    def test_event_handler_handles_trade_event_without_price(self):
        self.setUp()
        # bond price is unavailable at first
        trade_event = self.event_generator.publish_next_trade_event()
        print(trade_event)
        self.assertDictEqual(trade_event, sample_trade_events[0])
        self.event_handler.handle_event(trade_event)
        self.assertDictEqual(
            self.event_handler._withheld_buy_orders[trade_event['BondID']][0],
            trade_event
        )

        # bond price is available now after market data
        market_event = self.event_generator.publish_next_market_data()
        self.event_handler.handle_event(market_event)

        bond = Bond.objects.get(bond_id=trade_event['BondID'])
        val = round(Decimal(trade_event['Quantity']) * bond.price / bond.currency.rate, 5)
        self.assertDictEqual(
            model_to_dict(EventLog.objects.get(event_id=trade_event['EventID'])),
            {
                'event_id': 2,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'B',
                'quantity': 533,
                'bond_id': "B34678",
                'position': 533,
                'price': round(Decimal(10_000), 5),
                'fx_rate': round(Decimal(136.14), 5),
                'value': val,
                'cash': round(Decimal(1_000_000) - val, 5),
            }
        )



