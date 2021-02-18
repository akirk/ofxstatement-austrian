#!/usr/bin/env python3
# This file is part of ofxstatement-austrian.
# See README.rst for more information.

import datetime
from decimal import Decimal
import os
import unittest
from ofxstatement.statement import generate_transaction_id

from ofxstatement.plugins.raiffeisen import RaiffeisenCsvParser


class TestRaiffeisenCsvParser(unittest.TestCase):
    """Unit tests for RaiffeisenCsvParser."""

    def setUp(self):
        csvfile = os.path.join(
            os.path.dirname(__file__), 'samples', 'raiffeisen.csv')
        with open(csvfile, 'r', encoding='cp1252') as fin:
            self.statement = RaiffeisenCsvParser(fin).parse()

    def test_statement_properties(self):
        self.assertEqual(len(self.statement.lines), 7)
        self.assertEqual(self.statement.start_balance, 0.0)
        self.assertAlmostEqual(self.statement.end_balance, Decimal('-157.89'))
        self.assertEqual(self.statement.currency, "EUR")
        self.assertEqual(
            self.statement.start_date, datetime.datetime(2013, 6, 28, 0, 0))
        self.assertEqual(
            self.statement.end_date, datetime.datetime(2013, 7, 4, 0, 0))

    def test_line0_interest_earned(self):
        line = self.statement.lines[0]
        self.assertEqual(line.amount, Decimal('0.58'))
        self.assertEqual(line.memo, "0,125 % p.a. Habenzinsen ab 01.04.13")
        self.assertEqual(line.trntype, "CREDIT")
        self.assertEqual(line.date, datetime.datetime(2013, 6, 28, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line1_interest_paid(self):
        line = self.statement.lines[1]
        self.assertEqual(line.amount, Decimal('-0.15'))
        self.assertEqual(line.memo, "Kapitalertragsteuer")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2013, 6, 28, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line2_service_fee_print_statement(self):
        line = self.statement.lines[2]
        self.assertEqual(line.amount, Decimal('-0.11'))
        self.assertEqual(line.memo, "Entgelt Kontoauszug")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2013, 6, 28, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line3_service_fee(self):
        line = self.statement.lines[3]
        self.assertEqual(line.amount, Decimal('-6.65'))
        self.assertEqual(line.memo, "Entgelt Kontoführung")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2013, 6, 28, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line4_elba_payment(self):
        line = self.statement.lines[4]
        self.assertEqual(line.amount, Decimal('-175.16'))
        self.assertEqual(line.memo, "Invoice number 10")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2013, 7, 1, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line5_debit(self):
        line = self.statement.lines[5]
        self.assertEqual(line.amount, Decimal('-100'))
        self.assertEqual(line.memo, "reason")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2013, 7, 1, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line6_credit(self):
        line = self.statement.lines[6]
        self.assertEqual(line.amount, Decimal('123.60'))
        self.assertEqual(line.memo, "reason")
        self.assertEqual(line.trntype, "CREDIT")
        self.assertEqual(line.date, datetime.datetime(2013, 7, 4, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

class TestRaiffeisenMeinElbaCsvParser(unittest.TestCase):
    """Unit tests for RaiffeisenCsvParser for Mein ELBA."""

    def setUp(self):
        csvfile = os.path.join(
            os.path.dirname(__file__), 'samples', 'raiffeisen-meinelba.csv')
        with open(csvfile, 'r', encoding='utf8-sig') as fin:
            self.statement = RaiffeisenCsvParser(fin).parse()

    def test_statement_properties(self):
        self.assertEqual(len(self.statement.lines), 4)
        self.assertEqual(self.statement.start_balance, 0.0)
        self.assertAlmostEqual(self.statement.end_balance, Decimal('-414.15'))
        self.assertEqual(self.statement.currency, "EUR")
        self.assertEqual(
            self.statement.start_date, datetime.datetime(2020, 8, 1, 0, 0))
        self.assertEqual(
            self.statement.end_date, datetime.datetime(2020, 8, 13, 0, 0))

    def test_line0_payment(self):
        line = self.statement.lines[0]
        self.assertEqual(line.amount, Decimal('-12.84'))
        self.assertEqual(line.memo, "123")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2020, 8, 1, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line0_interest_paid(self):
        line = self.statement.lines[1]
        self.assertEqual(line.amount, Decimal('-121.31'))
        self.assertEqual(line.memo, "UEB Rate/Zinsen")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2020, 8, 5, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line1_online_banking_payment(self):
        line = self.statement.lines[2]
        self.assertEqual(line.amount, Decimal('-400.00'))
        self.assertEqual(line.memo, "Übertrag")
        self.assertEqual(line.trntype, "DEBIT")
        self.assertEqual(line.date, datetime.datetime(2020, 8, 5, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))

    def test_line2_incoming(self):
        line = self.statement.lines[3]
        self.assertEqual(line.amount, Decimal('120'))
        self.assertEqual(line.memo, "Gutschrifts Nr. 123 vom 01.08.2020")
        self.assertEqual(line.trntype, "CREDIT")
        self.assertEqual(line.date, datetime.datetime(2020, 8, 13, 0, 0))
        self.assertEqual(line.id, generate_transaction_id(line))


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 smartindent autoindent
