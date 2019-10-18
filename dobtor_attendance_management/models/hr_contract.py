# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    policy_id = fields.Many2one(
        string='Attendance Policy',
        comodel_name='hr.attendance.policies'
    )
