# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRAttendanceLateRule(models.Model):
    _name = 'hr.attendance.late.rule'
    _description = 'Late Rule'

    name = fields.Char(
        string='name',
        required=True,
        translate=True,
    )
    real_time_ok = fields.Boolean(
        string='Use Real Time',
        default=False
    )
    late_line_ids = fields.One2many(
        string='Late Section',
        comodel_name='hr.attendance.late.rule.line',
        inverse_name='late_id',
    )


class HRAttendanceLateRuleLine(models.Model):
    _name = 'hr.attendance.late.rule.line'
    _description = 'Late Rule Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    late_id = fields.Many2one(
        string='Late Rule',
        comodel_name='hr.late.rule',
    )
    late_time = fields.Float(
        string='Late Time',
    )
    deduction_time = fields.Float(string='Deduction time')
