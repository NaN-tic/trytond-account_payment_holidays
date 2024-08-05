import unittest

from proteus import Model, Wizard
from trytond.modules.account.tests.tools import create_chart, create_fiscalyear
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

        # Install account_payment_holidays
        activate_modules('account_payment_holidays')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)

        # Create party
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.save()
        party2 = Party(name='Party')
        party2.save()

        # Create a gateway
        PaymentHolidays = Model.get('party.payment.holidays')
        payholiday = PaymentHolidays()
        payholiday.party = party
        payholiday.from_month = '01'
        payholiday.from_day = 1
        payholiday.thru_month = '12'
        payholiday.thru_day = 31
        payholiday.save()

        # Try replace active party
        replace = Wizard('party.replace', models=[party])
        replace.form.source = party
        replace.form.destination = party2
        replace.execute('replace')

        # Check fields have been replaced
        payholiday.reload()
        self.assertEqual(payholiday.party, party2)
