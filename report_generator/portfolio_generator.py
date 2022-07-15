"""Module to generate portfolio data for client UI."""

from decimal import Decimal
from typing import Dict, List, Tuple, Union

from django.core import serializers
from django.db.models import QuerySet

from api.models import (
    FX, Bond, Desk, Trader, Book, BondRecord, EventLog, EventExceptionLog
)
from util.singleton import Singleton


class PortfolioGenerator(metaclass=Singleton):
    """Class to generate live portfolio data for client UI."""

    def __init__(self):
        pass
    
    # Generate newest data for live portfolio
    def generate_cash_level_data(self) -> List[Dict]:
        """Generate newest cash level portfolio data.
        Cash values are in 5 decimal places.
        """
        return serializers.serialize('json', Desk.objects.all())

    def generate_position_level_data(self) -> List[Dict]:
        """Generate newest position level portfolio data."""
        query_results = BondRecord.objects.raw(
            """
            SELECT
                id,
                api_desk.desk_id,
                api_trader.trader_id,
                api_book.book_id,
                sum(api_bondrecord.position) AS position,
                sum(api_bondrecord.position * api_bond.price / api_fx.rate) AS NV
            FROM api_bondrecord, api_bond, api_fx, api_desk, api_trader, api_book
            WHERE api_bondrecord.bond_id = api_bond.bond_id
            AND api_bondrecord.book_id = api_book.book_id
            AND api_bondrecord.trader_id = api_trader.trader_id
            AND api_trader.desk_id = api_desk.desk_id
            AND api_bond.currency_id = api_fx.currency_id
            GROUP BY api_desk.desk_id, api_trader.trader_id, api_book.book_id
            ORDER BY api_desk.desk_id, api_trader.trader_id, api_book.book_id;
            """
        )
        res: List = []
        for record in query_results:
            res.append({
                'desk': record.desk_id,
                'trader': record.trader_id,
                'book': record.book_id,
                'position': record.position,
                'NV': record.NV,
            })
        return res

    def generate_bond_level_data(self) -> List[Dict]:
        """Generate newest position level portfolio data."""
        bond_records: QuerySet = BondRecord.objects.all().order_by('trader', 'book', 'bond')
        res: List = []
        for record in bond_records:
            res.append({
                'desk': serializers.serialize('python', [record.trader.desk])[0],
                'trader': serializers.serialize('python', [record.trader])[0],
                'book': serializers.serialize('python', [record.book])[0],
                'bond': serializers.serialize('python', [record.bond])[0],
                'position': record.position,
                'NV': Decimal(record.position) * record.bond.price  / record.bond.currency.rate,
            })
        return res

    def generate_currency_level_data(self) -> List[Dict]:
        """Generate newest currency level portfolio data."""
        query_results = BondRecord.objects.raw(
            """
            SELECT
                id,
                api_desk.desk_id, api_fx.currency_id,
                sum(api_bondrecord.position) AS position,
                sum(api_bondrecord.position * api_bond.price / api_fx.rate) AS NV
            FROM api_bondrecord, api_bond, api_fx, api_desk, api_trader, api_book
            WHERE api_bondrecord.bond_id = api_bond.bond_id
            AND api_bondrecord.book_id = api_book.book_id
            AND api_bondrecord.trader_id = api_trader.trader_id
            AND api_trader.desk_id = api_desk.desk_id
            AND api_bond.currency_id = api_fx.currency_id
            GROUP BY api_desk.desk_id, api_fx.currency_id
            ORDER BY api_desk.desk_id, api_fx.currency_id;
            """
        )

        res: List = []
        for record in query_results:
            res.append({
                'desk': record.desk_id,
                'currency': record.currency_id,
                'position': record.position,
                'NV': record.NV,
            })
        return res

    def generate_exclusion_data(self) -> List[Dict]:
        """Generate newest exclusion data."""
        exclusions = EventExceptionLog.objects.all()
        return serializers.serialize('json', exclusions)


