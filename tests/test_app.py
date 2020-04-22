import unittest
from unittest.mock import patch

from farmer_market import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    def tearDown(self):
        pass

    def test_products_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_cart_scenario_BOJO(self):
        with self.app as client:
            self.app.post('/add', data={'code': 'CF1', 'quantity': 2})
            with client.session_transaction() as session:
                self.assertEqual(
                    session['all_total_price'],
                    11.23
                )
                self.assertEqual(
                    session['all_total_quantity'],
                    2
                )
                self.assertEqual(
                    session['cart_item'][1]['code'],
                    'BOGO'
                )
                self.assertEqual(
                    session['cart_item'][1]['total_price'],
                    -11.23
                )

    def test_cart_scenario_CHMK(self):
        with self.app as client:
            self.app.post('/add', data={'code': 'CH1', 'quantity': 1})
            self.app.post('/add', data={'code': 'AP1', 'quantity': 1})
            self.app.post('/add', data={'code': 'CF1', 'quantity': 1})
            self.app.post('/add', data={'code': 'MK1', 'quantity': 1})
            with client.session_transaction() as session:
                self.assertEqual(
                    session['all_total_price'],
                    20.34
                )
                self.assertEqual(
                    session['all_total_quantity'],
                    4
                )

    def test_cart_scenario_happy_path(self):
        with self.app as client:
            self.app.post('/add', data={'code': 'MK1', 'quantity': 1})
            self.app.post('/add', data={'code': 'AP1', 'quantity': 1})
            with client.session_transaction() as session:
                self.assertEqual(
                    session['all_total_price'],
                    10.75
                )
                self.assertEqual(
                    session['all_total_quantity'],
                    2
                )

    def test_cart_scenario_APPL(self):
        with self.app as client:
            self.app.post('/add', data={'code': 'CH1', 'quantity': 1})
            self.app.post('/add', data={'code': 'AP1', 'quantity': 1})
            self.app.post('/add', data={'code': 'AP1', 'quantity': 1})
            self.app.post('/add', data={'code': 'AP1', 'quantity': 1})
            with client.session_transaction() as session:
                self.assertEqual(
                    session['all_total_price'],
                    16.61
                )
                self.assertEqual(
                    session['all_total_quantity'],
                    4
                )

    def test_cart_scenario_OM1(self):
        with self.app as client:
            self.app.post('/add', data={'code': 'AP1', 'quantity': 1})
            self.app.post('/add', data={'code': 'OM1', 'quantity': 1})
            with client.session_transaction() as session:
                self.assertEqual(
                    session['all_total_price'],
                    6.69
                )
                self.assertEqual(
                    session['all_total_quantity'],
                    2
                )
