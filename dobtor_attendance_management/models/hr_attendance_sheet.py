# -*- coding: utf-8 -*-

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class HRAttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'

    name = fields.Char(string="name")
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        required=True
    )
    date_from = fields.Date(
        string="From",
        required=True,
        default=lambda self: fields.Date.to_string(
            date.today().replace(day=1)),
    )
    date_to = fields.Date(
        string="To",
        required=True,
        default=lambda self: fields.Date.to_string(
            (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
    )
    sheet_line_ids = fields.One2many(
        string='Attendances',
        comodel_name='hr.attendance.sheet.line',
        readonly=True,
        inverse_name='sheet_id'
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('done', 'Approved')
        ],
        default='draft',
        track_visibility='onchange',
        required=True,
        readonly=True,
        index=True,
        help=' * The \'Draft\' status is used when a HR user is creating a new  attendance sheet. '
             '\n* The \'Confirmed\' status is used when  attendance sheet is confirmed by HR user.'
             '\n* The \'Approved\' status is used when  attendance sheet is accepted by the HR Manager.')

    total_late = fields.Float(
        string="Total Late In",
        compute="compute_attendance_info",
        readonly=True,
        store=True
    )
    num_late = fields.Integer(
        string="Number of Lates",
        compute="compute_attendance_info",
        readonly=True,
        store=True
    )
    policy_id = fields.Many2one(
        string="Attendance Policy ",
        comodel_name='hr.attendance.policies',
        required=True
    )
    payslip_id = fields.Many2one(
        string='PaySlip',
        comodel_name='hr.payslip',
    )

    @api.multi
    def compute_attendance_info(self):
        late = 0
        num_late = 0
        for sheet in self:
            for line in sheet.sheet_line_ids:
                if line.late_in > 0:
                    late += line.late_in
                    num_late += 1
            values = {
                'total_late': late,
                'num_late': num_late
            }
            sheet.write(values)


class AttendanceSheetLine(models.Model):
    _name = 'hr.attendance.sheet.line'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('done', 'Approved')
        ],
        default='draft',
        readonly=True
    )
    date = fields.Date(string="Date", readonly=True)
    day = fields.Char(string="Day", readonly=True)
    sheet_id = fields.Many2one(
        string='Attendance Sheet',
        comodel_name='attendance.sheet',
        readonly=True
    )
    plan_sign_in = fields.Float("Planned sign in", readonly=True)
    plan_sign_out = fields.Float("Planned sign out", readonly=True)
    actual_sign_in = fields.Float("Actual sign in", readonly=True)
    actual_sign_out = fields.Float("Actual sign out", readonly=True)

    late_in = fields.Float("Late In",readonly=True)
    worked_hours = fields.Float("Worked Hours", readonly=True)
    note = fields.Text(string="Note")
    status = fields.Selection(
        string="Status",
        selection=[
            ('absence', 'Absence'),
            ('weekend', 'Week End'),
            ('leave', 'Leave')
        ],
        required=False,
        readonly=True
    )
