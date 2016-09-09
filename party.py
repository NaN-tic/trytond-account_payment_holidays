from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, If, Bool

__all__ = ['Party', 'PaymentHolidays']

MONTHS = [
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
    ]

class Party:
    __name__ = 'party.party'
    __metaclass__ = PoolMeta
    payment_holidays = fields.One2Many('party.payment.holidays', 'party',
        'Payment Holidays')


class PaymentHolidays(ModelSQL, ModelView):
    'Payment Holidays'
    __name__ = 'party.payment.holidays'
    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    from_month = fields.Selection(MONTHS, 'From Month', required=True, domain=[
            If(Bool(Eval('thru_month')),
                ('from_month', '<=', Eval('thru_month')), ()),
            ], depends=['thru_month'], sort=False)
    from_day = fields.Integer('From Day', required=True, domain=[
            ('from_day', '>=', 1),
            ('from_day', '<=', 31),
            ])
    thru_month = fields.Selection(MONTHS, 'Thru Month', required=True, domain=[
            If(Bool(Eval('from_month')),
                ('thru_month', '>=', Eval('from_month')), ()),
            ], depends=['from_month'], sort=False)
    thru_day = fields.Integer('Thru Day', required=True, domain=[
            ('thru_day', '>=', 1),
            ('thru_day', '<=', 31),
            ])

    def get_rec_name(self, name):
        return '%s %02d-%s  -  %02d-%s' % (self.party.rec_name, self.from_day,
            self.from_month, self.thru_day, self.thru_month)

    @classmethod
    def __setup__(cls):
        super(PaymentHolidays, cls).__setup__()
        cls._error_messages.update({
                'invalid_period': 'Payment holidays period "%s" is not valid.',
                })

    @classmethod
    def validate(cls, holidays):
        for holiday in holidays:
            holiday.check_period()

    def check_period(self):
        if self.from_month < self.thru_month:
            return
        if (self.from_month == self.thru_month
                and self.from_day <= self.thru_day):
            return
        self.raise_user_error('invalid_period', self.rec_name)