# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class AccountMakeSettlement(models.TransientModel):
    _name = "account.make.settlement"
    _description = "Wizard for settling pay to Gov in Journal Entry"

    date_to = fields.Date('Up to', required=True, default=fields.Date.today())

    @api.multi
    def action_settle(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}
