=================================
Account Payment Holidays Scenario
=================================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences
    >>> from trytond.exceptions import UserWarning

Define today as 1/1 of next year so that we don't get dates in the past which
would make Tryton to complain about maturity dates in the past and also to make
the scenario easier::

    >>> year = datetime.date.today().year
    >>> today = datetime.date(year + 1, 1, 1)

Activate account_invoice::

    >>> config = activate_modules('account_payment_holidays')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company, today=today))
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
    >>> invoice.invoice_date = (today + relativedelta(months=1)).replace(day=15)
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
    >>> try:
    ...     invoice.click('post')
    ... except UserWarning as warning:
    ...     _, (key, *_) = warning.args
    ...     raise  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InvoiceFutureWarning: ...
    >>> Model.get('res.user.warning')(user=config.user,
    ...     name=key, always=True).save()
    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> line = [x for x in invoice.move.lines if x.account == receivable][0]
    >>> line.maturity_date == invoice.invoice_date + relativedelta(months=1)
    True

Create invoice with due date after the payment holidays::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = (today + relativedelta(months=2)).replace(day=15)
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
    >>> try:
    ...     invoice.click('post')
    ... except UserWarning as warning:
    ...     _, (key, *_) = warning.args
    ...     raise  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InvoiceFutureWarning: ...
    >>> Model.get('res.user.warning')(user=config.user,
    ...     name=key, always=True).save()
    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> line = [x for x in invoice.move.lines if x.account == receivable][0]
    >>> line.maturity_date == invoice.invoice_date + relativedelta(months=1)
    True

Create invoice with due date on end-year payment holidays::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = (today + relativedelta(months=4)).replace(day=25)
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
    >>> try:
    ...     invoice.click('post')
    ... except UserWarning as warning:
    ...     _, (key, *_) = warning.args
    ...     raise  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InvoiceFutureWarning: ...
    >>> Model.get('res.user.warning')(user=config.user,
    ...     name=key, always=True).save()
    >>> invoice.click('post')
    >>> invoice.state
    'posted'
    >>> line = [x for x in invoice.move.lines if x.account == receivable][0]
    >>> line.maturity_date == invoice.invoice_date + relativedelta(months=1)
    True
