from django.test import TestCase

from api.populate_db import _read_csv

class ReadCSVTestCase(TestCase):
    def test_read_csv(self):
        data = _read_csv('initial_fx.csv')
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[0][0], str)
        self.assertIsInstance(data[0][1], str)
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0][0], 'HKX')
        self.assertEqual(data[0][1], '7.85')
        self.assertEqual(data[1][0], 'AUZ')
        self.assertEqual(data[1][1], '1.48')
        self.assertEqual(data[-1][0], 'USX')
        self.assertEqual(data[-1][1], '1')

        data = _read_csv('bond_details.csv')
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[0][0], str)
        self.assertIsInstance(data[0][1], str)
        self.assertEqual(len(data), 30)
        self.assertEqual(data[0][0], 'B06888')
        self.assertEqual(data[0][1], 'JPX')
        self.assertEqual(data[1][0], 'B07010')
        self.assertEqual(data[1][1], 'CNX')
        self.assertEqual(data[-1][0], 'B47923')
        self.assertEqual(data[-1][1], 'USX')

        data = _read_csv('initial_cash.csv')
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[0][0], str)
        self.assertIsInstance(data[0][1], str)
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0][0], 'NY')
        self.assertEqual(data[0][1], '100000000')
        self.assertEqual(data[1][0], 'LON')
        self.assertEqual(data[1][1], '100000000')
        self.assertEqual(data[-1][0], 'SYD')
        self.assertEqual(data[-1][1], '100000000')
