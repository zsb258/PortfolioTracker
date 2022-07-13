"""Event generator module."""

from pathlib import Path
import json
from typing import Deque, List, Union
from collections import deque

from util.common_types import Event, MarketEvent, TradeEvent
from util.singleton import Singleton

class _DataProducer:
    _queue: Deque[Event] = None

    def __init__(self, events: Deque[Event]):
        self._queue = events

    # API functions
    def has_next(self) -> bool:
        """Check if there is next event in queue."""
        return len(self._queue) > 0

    def send_next(self) -> Union[Event, None]:
        """Publish next event from queue."""
        if self.has_next():
            return self._queue.popleft()
        return None

class _MarketDataProducer(_DataProducer):
    def __init__(self, events: Deque[MarketEvent]):
        super().__init__(events)

class _TradeEventProducer(_DataProducer):
    def __init__(self, events: Deque[TradeEvent]):
        super().__init__(events)


class EventGenerator(metaclass=Singleton):
    """Class to read events from json file.
    Has API to send next events.
    """

    DATA_DIR = Path(__file__).absolute().parent.parent / 'data'

    # Class variables
    _market_data_producer: _MarketDataProducer = None
    _trade_event_producer: _TradeEventProducer = None

    def __init__(self, json_filename: str = 'events.json'):
        events = self._read_json(json_filename)
        self._enqueue_events(events)

    def _reset_for_unittest(self) -> None:
        """Helper function to reset for testing purposes."""
        self._market_data_producer = None
        self._trade_event_producer = None
        json_filename = 'example/example_events.json'
        events = self._read_json(json_filename)
        self._enqueue_events(events)

    # Helper functions
    def _read_json(self, json_filename: str) -> Union[List[Event], str]:
        """Helper function to read json file and
        return a list containing each event as dict.
        """
        filepath = self.DATA_DIR / json_filename
        try:
            with open(filepath, 'r', encoding='UTF-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return f'File {filepath} not found.'

    def _enqueue_events(self, events: List[Event]):
        """Helper function to enqueue events."""
        _market_data_queue: Deque[MarketEvent] = deque(maxlen=None)
        _trade_event_queue: Deque[TradeEvent] = deque(maxlen=None)
        for event in events:
            if 'EventType' in event:
                if event['EventType'] == 'PriceEvent' or event['EventType'] == 'FXEvent':
                    _market_data_queue.append(event)
                elif event['EventType'] == 'TradeEvent':
                    _trade_event_queue.append(event)
                else:
                    raise ValueError(f'Unknown event: {event["EventType"]}')
        self._market_data_producer = _MarketDataProducer(_market_data_queue)
        self._trade_event_producer = _TradeEventProducer(_trade_event_queue)

    def send_next_market_data(self) -> Union[MarketEvent, None]:
        """Helper function to get next market data."""
        return self._market_data_producer.send_next()

    def send_next_trade_event(self) -> Union[TradeEvent, None]:
        """Helper function to get next trade event."""
        return self._trade_event_producer.send_next()
