"""Module to generate reports."""

from decimal import Decimal
from typing import List

from django.http import HttpResponse

from api.models import (
    FX, Bond, Desk, Trader, Book, BondRecord, EventLog, EventExceptionLog
)
from event_handler.event_handlers import EventHandler
from util.common_types import Event, TradeEvent, PriceEvent, FXEvent
from util.trade_exceptions import (
    TradeException,
    NoMarketPriceException,
    CashOverlimitException,
    QuantityOverlimitException,
)
from util.singleton import Singleton


class ReportGenerator(metaclass=Singleton):
    """Class to generate reports."""
    _latest_event_id: int = 0

    def __init__(self):
        pass

    def _process_report(self, event_id: int) -> None:
        """Helper function to process report."""
        pass

    def _update_event_id(self) -> None:
        """Helper function to update event ID."""
        self._latest_event_id = EventHandler().get_latest_event_id()

    def _generate_csv_data(self) -> int:
        pass

    def _write_csv_to_response(
        self, response: HttpResponse, csv_data: List[EventLog]
    ) -> HttpResponse:
        """Middleware function to write CSV to response."""
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        return response
