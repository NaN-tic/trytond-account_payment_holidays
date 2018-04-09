# This file is part account_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from functools import wraps
from trytond.model import ModelView, ModelSQL
from trytond.transaction import Transaction

__all__ = ['Invoice']


def process_payment_holidays(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        holidays = None
        if self.type == 'out':
            holidays = []
            for period in self.party.payment_holidays:
                holidays.append((int(period.from_month), period.from_day,
                        int(period.thru_month), period.thru_day))
        with Transaction().set_context(account_payment_holidays=holidays):
            return func(self, *args, **kwargs)
    return wrapper


class Invoice(ModelSQL, ModelView):
    __name__ = 'account.invoice'

    @process_payment_holidays
    def create_move(self):
        # This method is called when not issuing invoice_speedup.patch
        # XXX: Remove when patch is commited in core and avoid decorator
        return super(Invoice, self).create_move()

    @process_payment_holidays
    def get_move(self):
        # This method is called when using invoice_speedup.patch
        return super(Invoice, self).get_move()
