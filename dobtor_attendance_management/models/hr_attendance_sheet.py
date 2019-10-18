# -*- coding: utf-8 -*-
import pytz
import babel
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, tools, fields, api, _
from odoo.exceptions import UserError, ValidationError
from operator import itemgetter


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
        compute="_compute_attendance_info",
        readonly=True,
        store=True
    )
    num_late = fields.Integer(
        string="Number of Lates",
        compute="_compute_attendance_info",
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

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        ttyme = datetime.fromtimestamp(time.mktime(
            time.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang', 'en_US')
        self.name = _('{} sheet : {}'.format(employee.name,
            tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))
        ))

        contract_ids = elf.env['hr.payslip'].get_contract(
            employee, date_from, date_to)
        if not contract_ids:
            return
        contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not contract_id.att_policy_id:
            return
        self.policy_id = contract_id.policy_id

    @api.multi
    def _compute_attendance_info(self):
        late=0
        num_late=0
        for sheet in self:
            for line in sheet.sheet_line_ids:
                if line.late_in > 0:
                    late += line.late_in
                    num_late += 1
            values={
                'total_late': late,
                'num_late': num_late
            }
            sheet.write(values)

    def get_timezone(self):
        if not self.env.user.tz:
            return pytz.timezone(self._context.get('tz') or 'UTC')
        return pytz.timezone(self.env.user.tz)

    def convert_time_tz_2_utc(self, date):
        """ We have to convert the time because the time of the database is UTC """
        timezone_info = self.get_timezone()
        return timezone_info.localize(date.replace(tzinfo=None)) \
            .astimezone(pytz.utc) \
            .replace(tzinfo=None)

    def get_resource_calendar_id(self, employee):
        if employee.contract_id and employee.contract_id.resource_calendar_id:
            return employee.contract_id.resource_calendar_id
        else:
            raise ValidationError(_(
                'You must add the work hours in the %s contract.' % employee.name))
            return

    def get_attendance_policy(self, sheet, employee):
        if sheet.policy_id:
            return sheet.policy_id
        else:
            raise ValidationError(_(
                "You must define the attendance policies in %s's contract" % employee.name))
            return

    def get_work_intervals(self, calender, day_start, day_end):
        tz = self.get_timezone()
        working_intervals = []
        start_dt = day_start.replace(
            hour = 0, minute = 0, second = 0, tzinfo = pytz.UTC)
        end_dt=day_end.replace(tzinfo = pytz.UTC)

        for intervals in calender._work_intervals(start_dt, end_dt):
            working_intervals.append((
                self.convert_time_tz_2_utc(intervals[0]),
                self.convert_time_tz_2_utc(intervals[1]),
            ))
        return working_intervals

    def get_attendance_intervals(self, employee_id, day_start, day_end):
        attendance_intervals=[]
        attendance=self.env['hr.attendance']

        attendances=attendance.search([
            ('employee_id.id', '=', employee_id.id),
            ('check_in', '>=', self.convert_time_tz_2_utc(day_start)),
            ('check_out', '<', self.convert_time_tz_2_utc(day_end))
        ], order = "check_in")

        for att in attendances:
            attendance_intervals.append(
                (att.check_in, att.check_out, att.worked_hours))
        return attendance_intervals

    def _get_float_from_time(self, time):
        time_type=datetime.strftime(time, "%H:%M")
        signOnP=[int(n) for n in time_type.split(":")]
        signOnH=signOnP[0] + signOnP[1] / 60.0
        return signOnH

    @api.multi
    def compute_attendances(self):
        for sheet in self:
            sheet.sheet_line_ids.unlink()
            sheet_line=self.env['hr.attendance.sheet.line']

            date_from=datetime.combine(sheet.date_from, datetime.min.time())
            date_to=datetime.combine(sheet.date_to, datetime.min.time())
            employee_id=sheet.employee_id

            timezone=self.get_timezone()
            calender_id=self.get_resource_calendar_id(employee_id)
            policy_id=self.get_attendance_policy(sheet, employee_id)
            # print('timezone.info : ', timezone.tzinfo)

            all_dates=[(date_from + relativedelta(days=x))
                         for x in range((date_to - date_from).days + 1)]
            abs_cnt = 0
            for day in all_dates:
                day_end = day.replace(hour=23, minute=59,
                                      second = 59, microsecond = 999999)
                work_intervals=self.get_work_intervals(
                    calender_id, day, day_end)
                attendance_intervals = self.get_attendance_intervals(
                    policy_id, day, day_end)

                for i, work_interval in enumerate(work_intervals):
                    att_work_intervals = []
                    for j, att_interval in enumerate(attendance_intervals):
                        print('work[0]', work_interval[0])
                        print('att[0]', att_interval[0])
                        print('max:', max(work_interval[0], att_interval[0]))
                        print('work[1]', work_interval[1])
                        print('att[1]', att_interval[1])
                        print('min:', min(work_interval[1], att_interval[1]))
                        att_work_intervals.append(att_interval)

                    pl_sign_in = self._get_float_from_time(
                        pytz.utc.localize(work_interval[0]).astimezone(timezone))
                    pl_sign_out = self._get_float_from_time(
                        pytz.utc.localize(work_interval[1]).astimezone(timezone))
                    ac_sign_in = 0
                    ac_sign_out = 0
                    worked_hours = 0
                    if att_work_intervals:
                        if len(att_work_intervals) > 1:
                            ac_sign_in = self._get_float_from_time(
                                pytz.utc.localize(att_work_intervals[0][0]).astimezone(timezone))
                            ac_sign_out = self._get_float_from_time(
                                pytz.utc.localize(att_work_intervals[-1][1]).astimezone(timezone))
                            worked_hours = ac_sign_out - ac_sign_in
                        else:
                            ac_sign_in = self._get_float_from_time(
                                pytz.utc.localize(att_work_intervals[0][0]).astimezone(timezone))
                            ac_sign_out = self._get_float_from_time(
                                pytz.utc.localize(att_work_intervals[0][1]).astimezone(timezone))
                            worked_hours = ac_sign_out - ac_sign_in

                    values = {
                        'date': day.strftime('%Y-%m-%d'),
                        'day': day.strftime('%A'),
                        'plan_sign_in': pl_sign_in,
                        'plan_sign_out': pl_sign_out,
                        'actual_sign_in': ac_sign_in,
                        'actual_sign_out': ac_sign_out,
                        # 'late_in': policy_late,
                        # 'status': status,
                        'worked_hours': worked_hours,
                        'sheet_id': self.id
                    }
                    sheet_line.create(values)


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

    late_in = fields.Float("Late In", readonly=True)
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
