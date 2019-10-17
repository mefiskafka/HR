# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_attendance_policies(models.Model):
    _name = 'hr.attendance.policies'
    _description = 'HR Attendance Policies'

    name = fields.Char(
        string="Name",
        required=True,
    )
    late_rule_id = fields.Many2one(
        string="Late In Rule",
        comodel_name="hr.attendance.late.rule",
        required=True,
    )
