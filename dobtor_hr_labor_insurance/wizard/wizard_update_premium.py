# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class Hr_Update_premium(models.TransientModel):
    _name = "hr.update.insurance.premium"
    _description = "Wizard for batch update insurance premium"

    contract_ids = fields.Many2many(
        string="Contract",
        comodel_name='hr.contract',
        domain=[('state', 'not in', ('close', 'cancel'))]
    )

    @api.multi
    def action_update_premium(self):
        self.ensure_one()
        if not self.contract_ids:
            self.contract_ids = self.env['hr.contract'].search(
                [('state', 'not in', ('close', 'cancel'))])
        for contact in self.contract_ids:
            contact.action_update_premium()

        return {'type': 'ir.actions.act_window_close'}
