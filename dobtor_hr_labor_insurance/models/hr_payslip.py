# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    nhi_2nd_amount = fields.Float(
        string='2nd Generation NHI amount'
    )

    # handle 2nd Generation NHI
    # TODO : need check salary rule in salary hr_salary_structure
    @api.multi
    def after_handle_inputs(self):
        input_obj = self.env['hr.payslip.input']
        payslip_obj = self.env['hr.payslip']

        for payslip in self:
            aunnal = date(month=1, year=payslip.date_from.year, day=1)
            old_payslip_ids = payslip_obj.search([
                ('employee_id', '=', payslip.employee_id.id),
                ('date_from', '<', payslip.date_from),
                ('date_from', '>=', aunnal),
                ('state', '=', 'done'),
            ])
            # This Contract quadruple amount
            quadruple_amount = 0.0
            if payslip.contract_id:
                quadruple_amount = 4.0 * payslip.contract_id.health_insure_wage
            # Compute aunnal amount
            aunnal_amount = 0.0
            for old_payslip in old_payslip_ids:
                aunnal_amount += sum(
                    [pline.amount for pline in old_payslip.input_line_ids])

            # This Time commission
            insurance_amount = 0.0
            for line in payslip.input_line_ids:
                base_amount = 0.0
                # Over amount
                aunnal_amount += line.amount
                over_amount = aunnal_amount - quadruple_amount
                over_amount = over_amount if over_amount > 0 else 0.0
                base_amount = min(line.amount, over_amount)
                # condition 10,000,000 limit
                insurance_amount += min(base_amount, 10000000)
            payslip.nhi_2nd_amount = insurance_amount
        return True
