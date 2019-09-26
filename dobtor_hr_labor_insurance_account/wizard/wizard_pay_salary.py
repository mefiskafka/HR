# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class AccountPaySalary(models.TransientModel):
    _name = "account.pay.salary"
    _description = "Wizard for settling Salary in Journal Entry"

    date_to = fields.Date('Up to', required=True, default=fields.Date.today())


    def _reconcile_payments(self, payslips):
        for payslip in payslips:
            aml = payslip.move_id.line_ids
            aml = aml.filtered(lambda r: not r.reconciled and r.account_id.internal_type == 'payable')
                            #    'payable' and r.partner_id == payslip.partner_id.commercial_partner_id)
            try:
                aml.reconcile()
            except Exception:
                _logger.exception(
                    'Reconciliation did not work for payslip %s ', payslip.name)



    @api.multi
    def action_pay(self):
        self.ensure_one()
        payslip = self.env['hr.payslip']
        for slip in payslip:
            partner_id = slip.employee_id.address_home_id.id or slip_id.employee_id.user_id.partner_id.id

            name = _('Payslip of %s') % (slip.employee_id.name)
            move_dict = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': self.date_to,
            }

        return {'type': 'ir.actions.act_window_close'}
