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
        comodel_name='hr.attendance.rule.line.mixin',
        inverse_name='rule_id',
    )
    # TODO : flexible working hours
    flexible_ok = fields.Boolean(
        string='Flexible working hours',
    )
    work_time = fields.Float(
        string='Work hour',
    )
    allow_time = fields.Float(
        string='allow hour',
    )

class HRAttendanceRuleLine(models.AbstractModel):
    _name = 'hr.attendance.rule.line.mixin'
    _description = 'Rule Line mixin'

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    rule_id = fields.Many2one(
        string='Rule',
        comodel_name='hr.attendance.rule.mixin',
        ondelete='cascade',
    )
    time = fields.Float(
        string='Time',
    )
    deduction_time = fields.Float(string='Deduction time')


class HRAttendanceLateRule(models.Model):
    _name = 'hr.attendance.late.rule'
    _inherit = 'hr.attendance.rule.mixin'
    _description = 'Late Rule'

    line_ids = fields.One2many(
        comodel_name='hr.attendance.late.rule.line',
    )

class HRAttendanceLateRuleLine(models.Model):
    _name = 'hr.attendance.late.rule.line'
    _inherit = 'hr.attendance.rule.line.mixin'
    _description = 'Late Rule Line'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        comodel_name='hr.attendance.late.rule',
    )

class HRAttendanceDiffRule(models.Model):
    _name = 'hr.attendance.diff.rule'
    _inherit = 'hr.attendance.rule.mixin'
    _description = 'Difference Rule'

    line_ids = fields.One2many(
        comodel_name='hr.attendance.diff.rule.line',
    )

class HRAttendanceDiffRuleLine(models.Model):
    _name = 'hr.attendance.diff.rule.line'
    _inherit = 'hr.attendance.rule.line.mixin'
    _description = 'Difference Rule Line'
    _order = 'sequence, id'

    rule_id = fields.Many2one(
        comodel_name='hr.attendance.diff.rule',
    )

class HRAttendanceAbsenceRule(models.Model):
    _name = 'hr.attendance.absence.rule'
    _inherit = 'hr.attendance.rule.mixin'
    _description = 'Absence Rule'


# class HRAttendanceAbsenceRuleLine(models.Model):
#     _name = 'hr.attendance.absence.rule.line'
#     _inherit = 'hr.attendance.rule.line.mixin'
#     _description = 'Absence Rule Line'
#     _order = 'sequence, id'


class HRAttendanceOvertimeRule(models.Model):
    _name = 'hr.attendance.overtime.rule'
    _description = 'Overtime Rule'

    name = fields.Char(string="name", translate=True)
    type = fields.Selection(selection=[
        ('workday', 'Working Day'),
        ('official', 'Weekly Official Holidays'),
        ('vacation', 'Vacation day'),
        ('public', 'Public Holiday')
    ], string="Type", default='workday')
    line_ids = fields.One2many(
        string='Overtime Section',
        comodel_name='hr.attendance.overtime.rule.line',
        inverse_name='rule_id',
    )
    need_post = fields.Boolean(
        string='need Post',
        default=False
    )

class HRAttendanceOvertimeLine(models.Model):
    _name = 'hr.attendance.overtime.rule.line'
    _description = 'Overtime Rule Line'
    _order = 'sequence, id'

    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    time = fields.Float(
        string='Time',
    )
    rule_id = fields.Many2one(
        comodel_name='hr.attendance.overtime.rule',
    )
    type = fields.Selection(
        related='rule_id.type',
        readonly=True,
        store=True
    )
    pattern = fields.Selection(selection=[
        ('1', '1'),
        ('2', '1.34'),
        ('3', '1.67'),
        ('4', '2'),
        ('5', '2.67'),
    ], string="pattern")
