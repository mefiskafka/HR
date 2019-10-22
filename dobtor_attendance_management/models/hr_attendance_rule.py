# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRAttendanceRule(models.AbstractModel):
    _name = 'hr.attendance.rule.mixin'
    _description = 'Rule mixin'

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
        string='Late Section',
        comodel_name='hr.attendance.late.rule.line',
        inverse_name='rule_id',
    )


class HRAttendanceRuleLine(models.AbstractModel):
    _name = 'hr.attendance.rule.line.mixin'
    _description = 'Rule Line mixin'

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    rule_id = fields.Many2one(
        string='Late Rule',
        comodel_name='hr.attendance.late.rule',
        ondelete='cascade',
    )
    time = fields.Float(
        string='Late Time',
    )
    deduction_time = fields.Float(string='Deduction time')


class HRAttendanceLateRule(models.Model):
    _name = 'hr.attendance.late.rule'
    _inherit = 'hr.attendance.rule.mixin'
    _description = 'Late Rule'


class HRAttendanceLateRuleLine(models.Model):
    _name = 'hr.attendance.late.rule.line'
    _inherit = 'hr.attendance.rule.line.mixin'
    _description = 'Late Rule Line'
    _order = 'sequence, id'


class HRAttendanceDiffRule(models.Model):
    _name = 'hr.attendance.diff.rule'
    _inherit = 'hr.attendance.rule.mixin'
    _description = 'Difference Rule'


class HRAttendanceDiffRuleLine(models.Model):
    _name = 'hr.attendance.diff.rule.line'
    _inherit = 'hr.attendance.rule.line.mixin'
    _description = 'Difference Rule Line'
    _order = 'sequence, id'
