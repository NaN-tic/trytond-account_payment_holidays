# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import party
from . import payment_term


def register():
    Pool.register(
        party.Party,
        party.PaymentHolidays,
        invoice.Invoice,
        payment_term.PaymentTermLine,
        module='account_payment_holidays', type_='model')
    Pool.register(
        party.PartyReplace,
        module='account_payment_holidays', type_='wizard')
