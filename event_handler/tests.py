from decimal import Decimal

from django.test import TestCase
from django.forms.models import model_to_dict

from api.populate_db import _read_csv
from api.models import (
    FX, Bond, Desk, Trader, Book, BondRecord, EventLog, EventExceptionLog
)
from event_handler.event_handlers import EventHandler
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

        # Clear all tables from auto-populate on start up
        # See `api/apps.py` for more details
        FX.objects.all().delete()
        Bond.objects.all().delete()
        Desk.objects.all().delete()

        data = _read_csv(csv_filename='example/example_initial_fx.csv')
        for row in data:
            FX.objects.get_or_create(currency=row[0], rate=row[1])

        data = _read_csv(csv_filename='example/example_bond_details.csv')
        for row in data:
            Bond.objects.get_or_create(
                bond_id=row[0], currency=FX.objects.get(currency=row[1])
            )

        data = _read_csv(csv_filename='example/example_initial_cash.csv')
        for row in data:
            Desk.objects.get_or_create(desk_id=row[0], cash=row[1])

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
        self.event_handler.handle_event(sample_market_data[0])
        
        #2
        event = sample_trade_events[0]
        self.event_handler.handle_event(event)

        bond = Bond.objects.get(bond_id=event['BondID'])
        val = round(Decimal(533 * 10_000) / Decimal(136.14), 5)
        self.assertDictEqual(
            model_to_dict(EventLog.objects.get(event_id=event['EventID'])),
            {
                'event_id': 2,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'buy',
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
        self.event_handler.handle_event(sample_market_data[1])

        #4
        event = sample_trade_events[1]
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
                'buy_sell': 'sell',
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
        # bond price is unavailable
        trade_event = sample_trade_events[0]
        self.event_handler.handle_event(trade_event)

        self.assertDictEqual(
            model_to_dict(
                Desk.objects.get(desk_id=trade_event['Desk'])
            ),
            {
                'desk_id': 'NY',
                'cash': Decimal(1_000_000),
                'updated': 0,
            },
            msg='Desk cash should not be changed'
        )

        self.assertDictEqual(
            model_to_dict(
                EventExceptionLog.objects.get(event_id=trade_event['EventID'])
            ),
            {
                'event_id': 2,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'buy',
                'quantity': 533,
                'bond_id': "B34678",
                'price': None,
                'exclusion_type': 'NO_MARKET_PRICE',
            }
        )

    def test_event_handler_handles_trade_event_cash_overlimit(self):
        self.setUp()
        # publish bond price
        self.event_handler.handle_event(sample_market_data[0])

        trade_event = {
            "EventID": 2,
            "EventType": "TradeEvent",
            "Desk": "NY",
            "Trader": "T6899554",
            "Book": "NY00",
            "BuySell": "buy",
            "Quantity": 53300,
            "BondID": "B34678",
        }
        self.event_handler.handle_event(trade_event)

        self.assertDictEqual(
            model_to_dict(
                Desk.objects.get(desk_id=trade_event['Desk'])
            ),
            {
                'desk_id': 'NY',
                'cash': Decimal(1_000_000),
                'updated': 0,
            },
            msg='Desk cash should not be changed'
        )

        self.assertDictEqual(
            model_to_dict(
                EventExceptionLog.objects.get(event_id=trade_event['EventID'])
            ),
            {
                'event_id': 2,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'buy',
                'quantity': 53300,
                'bond_id': "B34678",
                'price': round(Decimal(10_000), 5),
                'exclusion_type': 'CASH_OVERLIMIT',
            }
        )

    def test_event_handler_handles_trade_event_quantity_overlimit(self):
        self.setUp()
        # publish bond price
        self.event_handler.handle_event(sample_market_data[0])

        # attempt to sell more bonds than available
        trade_event = {
            "EventID": 2,
            "EventType": "TradeEvent",
            "Desk": "NY",
            "Trader": "T6899554",
            "Book": "NY00",
            "BuySell": "sell",
            "Quantity": 533,
            "BondID": "B34678",
        }
        self.event_handler.handle_event(trade_event)

        self.assertDictEqual(
            model_to_dict(
                Desk.objects.get(desk_id=trade_event['Desk'])
            ),
            {
                'desk_id': 'NY',
                'cash': Decimal(1_000_000),
                'updated': 0,
            },
            msg='Desk cash should not be changed'
        )

        self.assertDictEqual(
            model_to_dict(
                EventExceptionLog.objects.get(event_id=trade_event['EventID'])
            ),
            {
                'event_id': 2,
                'desk_id': "NY",
                'trader_id': "T6899554",
                'book_id': "NY00",
                'buy_sell': 'sell',
                'quantity': 533,
                'bond_id': "B34678",
                'price': round(Decimal(10_000), 5),
                'exclusion_type': 'QUANTITY_OVERLIMIT',
            }
        )

    def test_event_handler_handles_unordered_events(self):
        self.setUp()
        
        # Event 1
        self.event_handler.handle_event(sample_market_data[0])
        self.assertEqual(self.event_handler.get_latest_event_id(), 1)
        self.assertEqual(EventHandler()._queue, [])

        # Event 3
        self.event_handler.handle_event(sample_market_data[1])
        self.assertEqual(self.event_handler.get_latest_event_id(), 1)
        self.assertEqual(EventHandler()._queue, [
            (3, sample_market_data[1]),
        ])

        # Event 2
        self.event_handler.handle_event(sample_trade_events[0])
        self.assertEqual(self.event_handler.get_latest_event_id(), 3)
        self.assertEqual(EventHandler()._queue, [])

        # Event 6
        self.event_handler.handle_event(sample_market_data[3])
        self.assertEqual(self.event_handler.get_latest_event_id(), 3)
        self.assertEqual(EventHandler()._queue, [
            (6, sample_market_data[3]),
        ])

        # Event 5
        self.event_handler.handle_event(sample_market_data[2])
        self.assertEqual(EventHandler().get_latest_event_id(), 3)
        self.assertEqual(EventHandler()._queue, [
            (5, sample_market_data[2]),
            (6, sample_market_data[3]),
        ])

        # Event 4
        self.event_handler.handle_event(sample_trade_events[1])
        self.assertEqual(self.event_handler.get_latest_event_id(), 6)
        self.assertEqual(EventHandler._queue, [])
        print(EventHandler().get_latest_event_id())
        print(EventHandler()._latest_event_id)



