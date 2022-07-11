"""Script to read csv files and populate database."""

from pathlib import Path
import csv
from typing import List, Union

from .models import Bond, Desk, FX

# directory containing csv files
DATA_DIR = Path(__file__).absolute().parent.parent / 'data'

def _read_csv(csv_filename: str) -> Union[List[List[str]], str]:
    """Helper function to read csv file and
    return a list containing each row as nested list.
    Headers are ignored.
    """

    filepath = DATA_DIR / csv_filename
    try:
        with open(filepath, 'r', encoding='UTF-8') as file:
            reader = csv.reader(file)
            return list(reader)[1:]
    except FileNotFoundError:
        return f'File {filepath} not found.'

def _add_fx(filename = 'initial_fx.csv'):
    data: List[List[str]] = _read_csv(filename)
    for row in data:
        FX.objects.get_or_create(currency=row[0], rate=row[1])

def _add_bonds(filename: str = 'bond_details.csv'):
    data: List[List[str]] = _read_csv(filename)
    for row in data:
        Bond.objects.get_or_create(
            bond_id=row[0], currency=FX.objects.get(currency=row[1])
        )

def _add_desks(filename: str = 'initial_cash.csv'):
    data: List[List[str]] = _read_csv(filename)
    for row in data:
        Desk.objects.get_or_create(desk_id=row[0], cash=row[1])


def populate():
    """Populate database with initial data."""
    _add_fx()
    _add_bonds()
    _add_desks()
