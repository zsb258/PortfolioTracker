from pathlib import Path
import json
from typing import Deque, Generator, List, Union, Tuple
from collections import deque
import asyncio
import time
import random

from util.common_types import Event, MarketEvent, TradeEvent
from util.singleton import Singleton

class _DataProducer:
    _queue: Deque[Event] = None

    def __init__(self, events: Deque[Event]):
        self._queue = events

    def _add_delay(self) -> None:
        """Helper function to add delay."""
        time.sleep(random.randint(1, 5))

    # API functions
    def has_next(self) -> bool:
        """Check if there is next event in queue."""
        return len(self._queue) > 0

    def publish(self) -> Union[Event, None]:
        """Publish next event from queue."""
        if self.has_next():
            # self._add_delay()
            return self._queue.popleft()
        return None

    def _publish_immediate(self, to_print=True) -> Union[Event, None]:
        """Helper for testing."""
        if self.has_next():
            temp = self._queue.popleft()
            if to_print:
                print(temp)
            return temp
        return None

    def start(self) -> Generator[Event, None, None]:
        """Start producing events."""
        while self.has_next():
            # yield self.publish()
            yield self._publish_immediate()

    async def _async_delay(self) -> None:
        """Helper function to add delay."""
        asyncio.sleep(random.randint(1, 5))

    async def produce(self) -> Generator[Event, None, None]:
        """Async produce events."""
        while self.has_next():
            await self._async_delay()
            yield self._publish_immediate()

class MarketDataProducer(_DataProducer):
    def __init__(self, events: Deque[MarketEvent]):
        super().__init__(events)

class TradeEventProducer(_DataProducer):
    def __init__(self, events: Deque[TradeEvent]):
        super().__init__(events)


class EventGenerator(object, metaclass=Singleton):
    """Class to read events from json file."""

    DATA_DIR = Path(__file__).absolute().parent.parent / 'data'

    # Class variables
    _market_data_producer: MarketDataProducer = None
    _trade_event_producer: TradeEventProducer = None

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
                    raise ValueError(f'Unknown event type: {event["EventType"]}')
        self._market_data_producer = MarketDataProducer(_market_data_queue)
        self._trade_event_producer = TradeEventProducer(_trade_event_queue)

    def get_data_producers(self) -> Tuple[MarketDataProducer, TradeEventProducer]:
        """Helper function to get producers."""
        return self._market_data_producer, self._trade_event_producer

    def publish_next_market_data(self) -> Union[MarketEvent, None]:
        """Helper function to get next market data."""
        return self._market_data_producer.publish()

    def publish_next_trade_event(self) -> Union[TradeEvent, None]:
        """Helper function to get next trade event."""
        return self._trade_event_producer.publish()
