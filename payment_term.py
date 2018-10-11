#This file is part account_payment_days module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
import datetime
from dateutil.relativedelta import relativedelta
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = ['PaymentTermLine']


class PaymentTermLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.payment_term.line'

    def next_working_day(self, date):
        Date = Pool().get('ir.date')
        year = Date.today().year
        holidays = Transaction().context.get('account_payment_holidays')
        if holidays:
            assert isinstance(holidays, list)
            holidays = sorted(holidays)
            exit = False
            while not exit:
                exit = True
                for from_month, from_day, thru_month, thru_day in holidays:
                    from_ = datetime.date(year, from_month, from_day)
                    thru = datetime.date(year, thru_month, thru_day)
                    if date >= from_ and date <= thru:
                        date = thru + relativedelta(days=1)
                        exit = False
                year += 1
        return date

    def get_date(self, date):
        '''
        Override function from account_invoice module but check for the
        'account_payment_party' key in context and check if the party has
        any payment holidays period.
        '''
        return self.next_working_day(
            super(PaymentTermLine, self).get_date(date))
