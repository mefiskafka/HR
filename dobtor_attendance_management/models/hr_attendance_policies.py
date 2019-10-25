# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRAttendancePolicies(models.Model):
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
    diff_rule_id = fields.Many2one(
        string="Difference Time Rule",
        comodel_name="hr.attendance.diff.rule",
        required=True,
    )
    absence_rule_id = fields.Many2one(
        string="Absence Rule",
        comodel_name="hr.attendance.absence.rule",
    )
    overtime_rule_ids = fields.Many2many(
        string="Overtime Rules",
        comodel_name="hr.attendance.overtime.rule",
        relation="hr_attendance_overtime_rule_policy_rel",
        column1="policy_id",
        column2="rule_id"
    )
