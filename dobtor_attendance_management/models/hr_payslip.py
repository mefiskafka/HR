# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    policy_id = fields.Many2one(
        string='Attendance Policy',
        comodel_name='hr.attendance.policies'
    )


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    policy_id = fields.Many2one(
        string='Attendance Policy',
        comodel_name='hr.attendance.policies'
    )

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super().get_worked_day_lines(contracts, date_from, date_to)
        for item in res:
            leave_type = self.env['hr.leave.type'].search([('name', '=', item['code'])], limit=1)
            item['code'] = leave_type.code or item['code'] 
        return res

