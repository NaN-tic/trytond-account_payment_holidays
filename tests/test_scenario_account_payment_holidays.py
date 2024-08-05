import datetime
import unittest
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from proteus import Model
from trytond.exceptions import UserWarning
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.account_invoice.exceptions import InvoiceFutureWarning
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Define today as 1/1 of next year so that we don't get dates in the past which
        # would make Tryton to complain about maturity dates in the past and also to make
        # the scenario easier
        year = datetime.date.today().year
        today = datetime.date(year + 1, 1, 1)

        # Activate account_invoice
        config = activate_modules('account_payment_holidays')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company, today=today))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        receivable = accounts['receivable']
        revenue = accounts['revenue']

        # Create party
        Party = Model.get('party.party')
        PaymentHolidays = Model.get('party.payment.holidays')
        party = Party(name='Party')
        holidays = PaymentHolidays(
            from_month='08',
            from_day=1,
            thru_month='08',
            thru_day=31,
        )
        party.payment_holidays.append(holidays)
        holidays = PaymentHolidays(
            from_month='12',
            from_day=25,
            thru_month='12',
            thru_day=31,
        )
        party.payment_holidays.append(holidays)
        holidays = PaymentHolidays(
            from_month='01',
            from_day=1,
            thru_month='01',
            thru_day=6,
        )
        party.payment_holidays.append(holidays)
        party.save()

        # Create payment term
        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term = PaymentTerm(name='Term')
        line = payment_term.lines.new(type='remainder')
        line.relativedeltas.new(months=1)
        payment_term.save()

        # Create invoice with due date in the middle of the payment holidays
        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice()
        invoice.party = party
        invoice.payment_term = payment_term
        invoice.invoice_date = (today + relativedelta(months=1)).replace(day=15)
        line = InvoiceLine()
        invoice.lines.append(line)
        line.account = revenue
        line.description = 'Line'
        line.quantity = 10
        line.unit_price = Decimal('40')
        self.assertEqual(invoice.untaxed_amount, Decimal('400.00'))
        self.assertEqual(invoice.total_amount, Decimal('400.00'))

        with self.assertRaises(InvoiceFutureWarning):
            try:
                invoice.click('post')
            except UserWarning as warning:
                _, (key, *_) = warning.args
                raise

        Model.get('res.user.warning')(user=config.user, name=key,
                                      always=True).save()
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        line = [x for x in invoice.move.lines if x.account == receivable][0]
        self.assertEqual(line.maturity_date,
                         invoice.invoice_date + relativedelta(months=1))

        # Create invoice with due date after the payment holidays
        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice()
        invoice.party = party
        invoice.payment_term = payment_term
        invoice.invoice_date = (today + relativedelta(months=2)).replace(day=15)
        line = InvoiceLine()
        invoice.lines.append(line)
        line.account = revenue
        line.description = 'Line'
        line.quantity = 10
        line.unit_price = Decimal('40')
        self.assertEqual(invoice.untaxed_amount, Decimal('400.00'))
        self.assertEqual(invoice.total_amount, Decimal('400.00'))

        with self.assertRaises(InvoiceFutureWarning):
            try:
                invoice.click('post')
            except UserWarning as warning:
                _, (key, *_) = warning.args
                raise

        Model.get('res.user.warning')(user=config.user, name=key,
                                      always=True).save()
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        line = [x for x in invoice.move.lines if x.account == receivable][0]
        self.assertEqual(line.maturity_date,
                         invoice.invoice_date + relativedelta(months=1))

        # Create invoice with due date on end-year payment holidays
        Invoice = Model.get('account.invoice')
        InvoiceLine = Model.get('account.invoice.line')
        invoice = Invoice()
        invoice.party = party
        invoice.payment_term = payment_term
        invoice.invoice_date = (today + relativedelta(months=4)).replace(day=25)
        line = InvoiceLine()
        invoice.lines.append(line)
        line.account = revenue
        line.description = 'Line'
        line.quantity = 10
        line.unit_price = Decimal('40')
        self.assertEqual(invoice.untaxed_amount, Decimal('400.00'))
        self.assertEqual(invoice.total_amount, Decimal('400.00'))

        with self.assertRaises(InvoiceFutureWarning):
            try:
                invoice.click('post')
            except UserWarning as warning:
                _, (key, *_) = warning.args
                raise

        Model.get('res.user.warning')(user=config.user, name=key,
                                      always=True).save()
        invoice.click('post')
        self.assertEqual(invoice.state, 'posted')
        line = [x for x in invoice.move.lines if x.account == receivable][0]
        self.assertEqual(line.maturity_date,
                         invoice.invoice_date + relativedelta(months=1))
