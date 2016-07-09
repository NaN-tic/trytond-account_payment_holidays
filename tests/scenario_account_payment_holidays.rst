=================================
Account Payment Holidays Scenario
=================================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from.trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_invoice::

    >>> Module = Model.get('ir.module')
    >>> account_invoice_module, = Module.find(
    ...     [('name', '=', 'account_payment_holidays')])
    >>> account_invoice_module.click('install')
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']

Create party::

    >>> Party = Model.get('party.party')
    >>> PaymentHolidays = Model.get('party.payment.holidays')
    >>> party = Party(name='Party')
    >>> holidays = PaymentHolidays(
    ...    from_month='08',
    ...    from_day=1,
    ...    thru_month='08',
    ...    thru_day=31,
    ...    )
    >>> party.payment_holidays.append(holidays)
    >>> holidays = PaymentHolidays(
    ...    from_month='12',
    ...    from_day=25,
    ...    thru_month='12',
    ...    thru_day=31,
    ...    )
    >>> party.payment_holidays.append(holidays)
    >>> holidays = PaymentHolidays(
    ...    from_month='01',
    ...    from_day=1,
    ...    thru_month='01',
    ...    thru_day=6,
    ...    )
    >>> party.payment_holidays.append(holidays)
    >>> party.save()

Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> payment_term = PaymentTerm(name='Term')
    >>> line = payment_term.lines.new(type='remainder')
    >>> delta = line.relativedeltas.new(months=1)
    >>> payment_term.save()

Create invoice with due date in the middle of the payment holidays::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = datetime.date(2016, 7, 15)
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.account = revenue
    >>> line.description = 'Line'
    >>> line.quantity = 10
    >>> line.unit_price = Decimal('40')
    >>> invoice.untaxed_amount
    Decimal('400.00')
    >>> invoice.total_amount
    Decimal('400.00')
    >>> invoice.click('post')
    >>> invoice.state
    u'posted'
    >>> line = [x for x in invoice.move.lines if x.account == receivable][0]
    >>> line.maturity_date == datetime.date(2016, 9, 1)
    True

Create invoice with due date after the payment holidays::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = datetime.date(2016, 8, 15)
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.account = revenue
    >>> line.description = 'Line'
    >>> line.quantity = 10
    >>> line.unit_price = Decimal('40')
    >>> invoice.untaxed_amount
    Decimal('400.00')
    >>> invoice.total_amount
    Decimal('400.00')
    >>> invoice.click('post')
    >>> invoice.state
    u'posted'
    >>> line = [x for x in invoice.move.lines if x.account == receivable][0]
    >>> line.maturity_date == datetime.date(2016, 9, 15)
    True

Create invoice with due date on end-year payment holidays::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = datetime.date(2016, 11, 25)
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.account = revenue
    >>> line.description = 'Line'
    >>> line.quantity = 10
    >>> line.unit_price = Decimal('40')
    >>> invoice.untaxed_amount
    Decimal('400.00')
    >>> invoice.total_amount
    Decimal('400.00')
    >>> invoice.click('post')
    >>> invoice.state
    u'posted'
    >>> line = [x for x in invoice.move.lines if x.account == receivable][0]
    >>> line.maturity_date == datetime.date(2017, 1, 7)
    True
