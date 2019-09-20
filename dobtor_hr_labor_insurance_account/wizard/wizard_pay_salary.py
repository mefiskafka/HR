# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class AccountPaySalary(models.TransientModel):
    _name = "account.pay.salary"
    _description = "Wizard for settling Salary in Journal Entry"

    date_to = fields.Date('Up to', required=True, default=fields.Date.today())

    @api.multi
    def action_pay(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}
