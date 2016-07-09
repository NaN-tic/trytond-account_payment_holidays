# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .invoice import *
from .party import *
from .payment_term import *

def register():
    Pool.register(
        Party,
        PaymentHolidays,
        Invoice,
        PaymentTermLine,
        module='account_payment_holidays', type_='model')
