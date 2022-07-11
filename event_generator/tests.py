from django.test import TestCase

from event_generator.event_generator import EventGenerator
from util.common_types import Event, MarketEvent, TradeEvent, PriceEvent, FXEvent

class EventTypesTestCase(TestCase):
    def setUp(self):
        self.trade_event: TradeEvent = {
            "EventID": 2,
            "EventType": "TradeEvent",
            "Desk": "NY",
            "Trader": "T1784214",
            "Book": "NY02",
            "BuySell": "buy",
            "Quantity": 533,
        "BondID": "B33152"
        }
        self.price_event: PriceEvent = {
            "EventID": 1,
            "EventType": "PriceEvent",
            "BondID": "B47374",
            "MarketPrice": 1996.52
        }
        self.fx_event: FXEvent = {
            "EventID": 13,
            "EventType": "FXEvent",
            "ccy": "SGX",
            "rate": 1.57
        }
        self.events = [self.trade_event, self.price_event, self.fx_event]

    def test_trade_event_should_be_typed_trade_event(self):
        self.assertEqual(self.trade_event["EventType"], "TradeEvent")

class EventGeneratorTestCase(TestCase):
    def setUp(self) -> None:
        self.generator_a = EventGenerator()
        self.generator_b = EventGenerator()

    def test_event_generator_is_singleton(self):
        self.assertEqual(self.generator_a, self.generator_b)

    def test_market_data_producer(self):
        sample_market_event1: MarketEvent = {
            "EventID": 1,
            "EventType": "PriceEvent",
            "BondID": "B47374",
            "MarketPrice": 1996.52
        }
        sample_market_event2: MarketEvent = {
            "EventID": 3,
            "EventType": "PriceEvent",
            "BondID": "B29512",
            "MarketPrice": 1281.68
        }
        sample_market_event_last: MarketEvent = {
            "EventID": 1000,
            "EventType": "PriceEvent",
            "BondID": "B41686",
            "MarketPrice": 5926.62
        }
        
        self.assertEqual(self.generator_a._market_data_producer.has_next(), True)
        self.assertDictEqual(
            self.generator_a.publish_next_market_data(), sample_market_event1
        )

        self.assertEqual(self.generator_b._market_data_producer.has_next(), True)
        self.assertDictEqual(
            self.generator_b.publish_next_market_data(), sample_market_event2
        )

        while (self.generator_a._market_data_producer.has_next()):
            curr = self.generator_a._market_data_producer._publish_immediate(False)
        self.assertDictEqual(curr, sample_market_event_last)

    def test_trade_event_producer(self):
        sample_trade_event1: TradeEvent = {
            "EventID": 2,
            "EventType": "TradeEvent",
            "Desk": "NY",
            "Trader": "T1784214",
            "Book": "NY02",
            "BuySell": "buy",
            "Quantity": 533,
            "BondID": "B33152"
        }
        sample_trade_event2: TradeEvent = {
            "EventID": 4,
            "EventType": "TradeEvent",
            "Desk": "SYD",
            "Trader": "T5021908",
            "Book": "SYD00",
            "BuySell": "buy",
            "Quantity": 555,
            "BondID": "B12794"
        }
        sample_trade_event_last: TradeEvent = {
            "EventID": 999,
            "EventType": "TradeEvent",
            "Desk": "TOK",
            "Trader": "T6583742",
            "Book": "TOK10",
            "BuySell": "sell",
            "Quantity": 339,
            "BondID": "B05627"
        }

        self.assertEqual(self.generator_a._trade_event_producer.has_next(), True)
        self.assertDictEqual(
            self.generator_a.publish_next_trade_event(), sample_trade_event1
        )

        self.assertEqual(self.generator_a._trade_event_producer.has_next(), True)
        self.assertDictEqual(
            self.generator_b.publish_next_trade_event(), sample_trade_event2
        )

        while (self.generator_a._trade_event_producer.has_next()):
            curr = self.generator_a._trade_event_producer._publish_immediate(False)
        self.assertDictEqual(curr, sample_trade_event_last)
