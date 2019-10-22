# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRAttendanceDiffRule(models.Model):
    _name = 'hr.attendance.diff.rule'
    _description = 'Difference Rule'

    name = fields.Char(
        string='name',
        required=True,
        translate=True,
    )
    real_time_ok = fields.Boolean(
        string='Use Real Time',
        default=False
    )
    line_ids = fields.One2many(
        string='Difference Section',
        comodel_name='hr.attendance.diff.rule.line',
        inverse_name='rule_id',
    )


class HRAttendanceDiffRuleLine(models.Model):
    _name = 'hr.attendance.diff.rule.line'
    _description = 'Difference Rule Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    rule_id = fields.Many2one(
        string='Difference Rule',
        comodel_name='hr.attendance.diff.rule',
        ondelete='cascade',
    )
    time = fields.Float(
        string='Difference Time',
    )
    deduction_time = fields.Float(string='Deduction time')
