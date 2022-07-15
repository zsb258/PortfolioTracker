"""Module to generate reports."""


from pathlib import Path
import csv
from decimal import Decimal
from typing import Callable, Dict, List, Tuple, Union
from itertools import groupby

from django.http import HttpResponse

from api.models import (
    FX, Bond, Desk, BondRecord, EventLog, EventExceptionLog, FxEventLog, PriceEventLog,
)
from util.singleton import Singleton
from util import common_fns


class ReportGenerator(metaclass=Singleton):
    """Class to generate reports."""
    OUT_DIR = Path(__file__).absolute().parent.parent / 'out'

    # Stores states of data at event_id = `_state_id`
    # Singleton implementation means only 1 state is stored at a time
    _state_id: int = 0

    # Maps (desk_id, trader_id, book_id, bond_id) to position
    _state_data: Dict[Tuple[str, str, str, str], Decimal] = {}

    # Maps currency to rate
    _fx: Dict[str, Decimal] = {}

    # Maps desk_id to cash
    _desks: Dict[str, Decimal] = {}

    # Maps bond_id to a dict with keys 'currency', 'price'
    _bonds: Dict[str, Dict[str, Union[str, Decimal]]] = {}

    def __init__(self):
        pass

    def _get_curr_bonds_fx_desk_records(self) -> None:
        fx_s: List[FX] = FX.objects.all()
        for fx in fx_s:
            self._fx[fx.currency_id] = fx.rate

        bonds: List[Bond] = Bond.objects.all()
        for bond in bonds:
            self._bonds[bond.bond_id] = {
                'currency': bond.currency.currency_id,
                'price': bond.price,
            }

        desks: List[Desk] = Desk.objects.all()
        for desk in desks:
            self._desks[desk.desk_id] = desk.cash

    def _get_curr_bond_records(self) -> None:
        """Helper function to get and reformat current bond records."""
        curr_bond_records: List[BondRecord] = BondRecord.objects.all().order_by('trader', 'book')

        # Unpacking current bond records for further manipulation
        records: Dict[Tuple[str, str, str, str], Decimal]= {}
        for record in curr_bond_records:
            bond: Bond = record.bond
            desk: Desk = record.trader.desk

            desk_id = desk.desk_id
            trader_id = record.trader.trader_id
            book_id = record.book.book_id
            bond_id = bond.bond_id
            key: Tuple[str, str, str, str] = (
                desk_id, trader_id, book_id, bond_id,
            )

            value: Decimal = record.position

            records[key] = value

        self._state_data = records

    def _reset_states(self) -> None:
        """Helper function to reset current data."""
        self._state_id = 0
        self._state_data = {}
        self._fx = {}
        self._bonds = {}
        self._desks = {}

    def _set_up(self) -> None:
        """Helper function to set up data for report generation."""
        if self._state_id <= 0:
            self._get_curr_bonds_fx_desk_records()
            self._get_curr_bond_records()
            self._state_id = common_fns.get_largest_event_id()

    def _move_to_target_state(self, target_id: int) -> None:
        """Helper function to move to target state."""
        if self._state_id == target_id:
            return

        self._set_up()
        if self._state_id < target_id:
            self._advance_events(target_id)
        elif self._state_id > target_id:
            self._backtrack_events(target_id)

        self._move_fx_bonds_states(target_id)
        self._state_id = target_id

    def _advance_events(self, target_id: int) -> None:
        """Query DB for logs of events strictly after state_id
        and before target_id (inclusive), and apply them.
        """

        # Logs are ordered from oldest to newest
        logs: List[EventLog] = (
            EventLog.objects
            .filter(event_id__range=(self._state_id + 1, target_id))
            .order_by('event_id')
        )

        if logs.exists():
            for log in logs:
                key = (
                    log.desk.desk_id,
                    log.trader.trader_id,
                    log.book.book_id,
                    log.bond.bond_id,
                )
                if key not in self._state_data:
                    # Can safely set position to 0 because current log is a buy event
                    self._state_data[key] = 0

                # Applying value changes from buy/sell trade events
                if log.buy_sell == 'buy':
                    self._desks[log.desk.desk_id] -= log.value
                    self._state_data[key] += log.quantity
                elif log.buy_sell == 'sell':
                    self._desks[log.desk.desk_id] += log.value
                    self._state_data[key] -= log.quantity

    def _backtrack_events(self, target_id: int) -> None:
        """Query DB for logs of events strictly after target_id, and reverse them."""

        # Logs are ordered from newest to oldest
        logs: List[EventLog] = (
            EventLog.objects
            .filter(event_id__range=(target_id + 1, self._state_id))
            .order_by('-event_id')
        )

        if logs.exists():
        # Logs are ordered from newest to oldest
            for log in logs:
                key = (
                    log.desk.desk_id,
                    log.trader.trader_id,
                    log.book.book_id,
                    log.bond.bond_id,
                )

                # Undoing value changes from buy/sell trade events
                if log.buy_sell == 'buy':
                    self._desks[log.desk.desk_id] += log.value
                    self._state_data[key] -= log.quantity
                elif log.buy_sell == 'sell':
                    self._desks[log.desk.desk_id] -= log.value
                    self._state_data[key] += log.quantity

    def _move_fx_bonds_states(self, target_id: int) -> None:
        """Helper function to update fx and bonds state."""
        # Iterate to update any unreflected fx changes
        for currency_id, _ in self._fx.items():
            # Retrieve latest fx change for `currency_id` that happened on or before `target_id`
            fx_log = (
                FxEventLog.objects
                .filter(currency__currency_id=currency_id)
                .filter(event_id__lte=target_id)
                .order_by('-event_id')
            )
            if fx_log.exists():
                self._fx[currency_id] = fx_log.first().rate
            else:
                # No fx change for `currency_id` happened on or before `target_id`
                self._fx[currency_id] = FX.objects.get(currency_id=currency_id).initial

        # Iterate to update any unreflected price changes
        for bond_id, fields in self._bonds.items():
            # Retrieve latest price change for `bond_id` that happened on or before `target_id`
            price_log = (
                PriceEventLog.objects
                .filter(bond__bond_id=bond_id)
                .filter(event_id__lte=target_id)
                .order_by('-event_id')
            )
            if price_log.exists():
                fields['price'] = price_log.first().price
                self._bonds[bond_id] = fields
            else:
                # No price change for `bond_id` happened on or before `target_id`
                self._bonds[bond_id]['price'] = Bond.objects.get(bond_id=bond_id).initial_price


    def _write_cash_level_data(self, destination, target_id):
        """Helper to write cash level data to file or stream. Then return the same object.
        @ignored_param:` target_id`
        """

        writer = csv.writer(destination)
        writer.writerow([
            'Desk',
            'Cash',
        ])
        for desk_id, cash in self._desks.items():
            writer.writerow([
                desk_id,
                f'{cash:.2f}',
            ])
        return destination

    def _write_position_level_data(self, destination, target_id):
        """Helper to write position level data to file or stream. Then return the same object.
        @ignored_param:` target_id`
        """

        # Sort before groupby
        sorted_items = sorted(self._state_data.items(), key=lambda x: x[0])

        temp = []
        # Group by [desk, trader, book] and storing the groups in temp for further manipulation
        for key, group in groupby(sorted_items, key=lambda x: x[0][0:3]):
            temp.append((key, list(group)))

        data = []
        for key, group in temp:
            position = sum(x[1] for x in group)
            NV = sum(
                Decimal(x[1]) * self._bonds[x[0][3]]['price'] \
                    / self._fx[self._bonds[x[0][3]]['currency']] for x in group
            )
            data.append((key, position, NV))

        writer = csv.writer(destination)
        writer.writerow([
            'Desk',
            'Trader',
            'Book',
            'Position',
            'Value',
        ])
        for key, position, NV in data:
            if position > 0:
                writer.writerow([
                    key[0],
                    key[1],
                    key[2],
                    position,
                    f'{NV:.2f}',
                ])
        return destination

    def _write_bond_level_data(self, destination, target_id):
        """Helper to write bond level data to file or stream. Then return the same object.
        @ignored_param:` target_id`
        """

        # Sort before groupby
        sorted_items = sorted(self._state_data.items(), key=lambda x: x[0])

        temp = []
        # Group by [desk, trader, book, bond] and store the groups in temp for further manipulation
        for key, group in groupby(sorted_items, key=lambda x: x[0]):
            temp.append((key, list(group)))

        data = []
        for key, group in temp:
            position = sum(x[1] for x in group)
            NV = sum(
                Decimal(x[1]) * self._bonds[x[0][3]]['price'] \
                    / self._fx[self._bonds[x[0][3]]['currency']] for x in group
            )
            data.append((key, position, NV))

        writer = csv.writer(destination)
        writer.writerow([
            'Desk',
            'Trader',
            'Book',
            'BondID',
            'Position',
            'Value',
        ])
        for key, position, NV in data:
            if position > 0:
                writer.writerow([
                    key[0],
                    key[1],
                    key[2],
                    key[3],
                    position,
                    f'{NV:.2f}',
                ])
        return destination

    def _write_currency_level_data(self, destination, target_id):
        """Helper to write currency level data to file or stream. Then return the same object.
        @ignored_param:` target_id`
        """

        def get_key(x):
            # x is a tuple-like of ((desk_id, trader_id, book_id, bond_id), position)
            desk_id = x[0][0]
            ccy_id = self._bonds[x[0][3]]['currency']
            return (desk_id, ccy_id)

        # Sort before groupby
        sorted_items = sorted(self._state_data.items(), key=get_key)

        temp = []
        # Group by [desk, currency] and storing the groups in temp for further manipulation
        for key, group in groupby(sorted_items, key=get_key):
            temp.append((key, list(group)))

        data = []
        for key, group in temp:
            position = sum(x[1] for x in group)
            NV = sum(
                Decimal(x[1]) * self._bonds[x[0][3]]['price'] \
                    / self._fx[self._bonds[x[0][3]]['currency']] for x in group
            )
            data.append((key, position, NV))

        writer = csv.writer(destination)
        writer.writerow([
            'Desk',
            'Currency',
            'Position',
            'Value',
        ])
        for key, position, NV in data:
            if position > 0:
                writer.writerow([
                    key[0],
                    key[1],
                    position,
                    f'{NV:.2f}',
                ])
        return destination

    def _write_exclusion_data(self, destination, target_id: int):
        """Helper to write exclusion data to file or stream. Then return the same object.
        Data required for exclusions output are read from DB and not from state_data.
        """
        exclusions: List[EventExceptionLog] = (
            EventExceptionLog.objects.filter(event_id__lte=target_id)
        )
        writer = csv.writer(destination)
        writer.writerow([
            'EventID',
            'Desk',
            'Trader',
            'Book',
            'BuySell',
            'Quantity',
            'BondID',
            'Price',
            'ExclusionType',
        ])
        for exclusion in exclusions:
            price = f'{exclusion.price:.2f}' if exclusion.price else ''
            writer.writerow([
                exclusion.event_id,
                exclusion.desk.desk_id,
                exclusion.trader.trader_id,
                exclusion.book.book_id,
                exclusion.buy_sell,
                exclusion.quantity,
                exclusion.bond.bond_id,
                price,
                exclusion.exclusion_type,
            ])
        return destination

    def generate_report(
        self, target_id: int, report_type: str, to_http_response=False
    ) -> Union[None, HttpResponse]:
        """Generate reports.
        @param to_http_response: return HttpResponse with csv data if True,
        otherwise write to file and return None.
        """
        type_to_fn_mapping: Dict[str, Callable] = {
            'cash_level_portfolio': self._write_cash_level_data,
            'position_level_portfolio': self._write_position_level_data,
            'bond_level_portfolio': self._write_bond_level_data,
            'currency_level_portfolio': self._write_currency_level_data,
            'exclusions': self._write_exclusion_data,
        }
        if report_type not in type_to_fn_mapping:
            raise ValueError(f'Unknown report type: {report_type}')

        # Ensure data is at the state of event `target_id`
        self._move_to_target_state(target_id)

        if to_http_response:
            # Write to HttpResponse and return the response
            csv_filename = f'{report_type}_{target_id}.csv'
            response = HttpResponse(
                content_type='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename={csv_filename}'
                },
            )
            return type_to_fn_mapping[report_type](destination=response, target_id=target_id)

        # Else write to file and return None
        filename = self.OUT_DIR / f'output_{target_id}' / f'{report_type}_{target_id}.csv'
        filename.parent.mkdir(exist_ok=True, parents=True)
        with open(filename, 'w', encoding='UTF-8') as file:
            type_to_fn_mapping[report_type](destination=file, target_id=target_id)
        return None

    def output_reports(self, target_id: int):
        """Output the 5 types of reports to files."""
        report_types = [
            'cash_level_portfolio',
            'position_level_portfolio',
            'bond_level_portfolio',
            'currency_level_portfolio',
            'exclusions',
        ]
        for report_type in report_types:
            self.generate_report(target_id, report_type, to_http_response=False)
