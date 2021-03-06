# -*- coding: utf-8 -*-
import pytz
import babel
from itertools import groupby
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, tools, fields, api, _
from odoo.exceptions import UserError, ValidationError
from operator import itemgetter



class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.multi
    def write(self, vals):
        if vals.get('check_out', '') and str(vals.get('check_out', '')).split(" ", 1) == str(vals.get('check_in', '')).split(" ", 1):
            attendance_sheet_line = self.env['hr.attendance.sheet.line'].search(
                [('date', '=', str(vals.get('check_out')).split(" ", 1))])
            attendance_sheet_line.write({'is_processed' : False})
        return super().write(vals)

    @api.multi
    def unlink(self):
        for attendance in self:
            if attendance.check_out and attendance.check_out.strftime('%Y-%m-%d') == attendance.check_in.strftime('%Y-%m-%d'):
                attendance_sheet_line = self.env['hr.attendance.sheet.line'].search(
                    [('date', '=', attendance.check_out.strftime('%Y-%m-%d'))])
                attendance_sheet_line.write({'is_processed' : False})
        super().unlink()


class HRAttendanceSheet(models.Model):
    _name = 'hr.attendance.sheet'
    _inherit = 'mail.thread'
    
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
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    num_late = fields.Integer(
        string="Number of Lates",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    total_diff = fields.Float(
        string="Total Difference Time",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    num_diff = fields.Integer(
        string="Number of Difference",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    total_absence = fields.Float(
        string="Total Absence Time",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    num_absence = fields.Integer(
        string="Number of Absence",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    total_overtime = fields.Float(
        string="Total Workday Overtime",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    num_overtime = fields.Integer(
        string="Number of Workday Overtime",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    overtime_ids = fields.One2many(
        string='Overtime Sheet',
        comodel_name='hr.attendance.sheet.overtime',
        inverse_name='sheet_id',
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
        attendance = self.search([
            ('employee_id', '=', employee.id),
            '|', '|', '|',
            '&','&', ('date_from', '<=', date_from), ('date_to', '>=', date_from), ('date_to', '<=', date_to),
            '&','&', ('date_from', '<=', date_to), ('date_to', '>=', date_to), ('date_from', '>=', date_from),
            '&', ('date_from', '<=', date_from), ('date_to', '>=', date_to),
            '&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
        ], limit=1)
        if attendance:
            # other case (singularity)
            #  already date :         10/1|██████████████|10/31
            #  search date :             10/10|██████████████|11/10
            # or 
            #  already date :         10/1|██████████████|10/31
            #  search date :      9/20|██████████████|10/20
            # or 
            #  already date :         10/1|██████████████|10/31
            #  search date :            10/10|███████|10/20
            # or 
            #  already date :         10/1|██████████████|10/31
            #  search date :      9/20|███████████████████████|10/20
            if self.env.context.get('ir_cron', False):
                return
            raise ValidationError(_('in this case are already attendance sheet existing or singularity.\n employee : {}\n from : {}\n to : {}'.format(
            employee.name, attendance.date_from, attendance.date_to)))

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang', 'en_US')
        self.name = _('{} sheet : {}'.format(employee.name,
                                             tools.ustr(babel.dates.format_date(
                                                 date=ttyme, format='MMMM-y', locale=locale))
                                             ))

        contract_ids = self.env['hr.payslip'].get_contract(
            employee, date_from, date_to)
        if not contract_ids:
            return
        contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not contract_id.policy_id:
            return
        self.policy_id = contract_id.policy_id
    
    @api.multi
    def settlement_attendance_data(self):
        overtime = 0
        num_overtime = 0
        diff = 0
        num_diff = 0
        late = 0
        num_late = 0
        absence = 0
        num_absence = 0
        for sheet in self:
            for line in sheet.sheet_line_ids:
                if line.overtime > 0:
                    num_overtime += 1 
                    overtime += line.overtime
                if line.diff_time > 0:
                    if line.status == "absence":
                        num_absence += 1
                        absence += line.diff_time
                    else:
                        diff += line.diff_time
                        num_diff += 1
                if line.late_in > 0:
                    late += line.late_in
                    num_late += 1
            values = {
                'total_overtime': overtime,
                'num_overtime': num_overtime,
                'total_late': late,
                'num_late': num_late,
                'total_diff': diff,
                'num_diff': num_diff,
                'total_absence': absence,
                'num_absence': num_absence,
            }
            
            sheet.write(values)
            # TODO : Need to outside this function
            sheet.overtime_ids.unlink()
            sheet.settlement_overtime()


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
        # tz = self.get_timezone()
        start_dt = day_start.replace(
            hour=0, minute=0, second=0, tzinfo=pytz.UTC)
        end_dt = day_end.replace(tzinfo=pytz.UTC)

        return [(
                self.convert_time_tz_2_utc(intervals[0]),
                self.convert_time_tz_2_utc(intervals[1]),
                ) for intervals in calender._work_intervals(start_dt, end_dt)]

    def get_attendance_intervals(self, employee_id, day_start, day_end):
        attendance = self.env['hr.attendance']

        attendances = attendance.search([
            ('employee_id.id', '=', employee_id.id),
            ('check_in', '>=', self.convert_time_tz_2_utc(day_start)),
            ('check_out', '<', self.convert_time_tz_2_utc(day_end))
        ], order="check_in")

        return [(att.check_in, att.check_out, att.worked_hours) for att in attendances]

    def get_employee_leave_intervals(self, employee_id, day_start=None, day_end=None):
        leaves = []
        leave_obj = self.env['hr.leave']
        leave_ids = leave_obj.search([
            ('employee_id', '=', employee_id.id),
            ('state', 'in', ('validate', 'validate1'))
        ])
        for leave in leave_ids:
            if day_end and leave.date_from > day_end:
                continue
            if day_start and leave.date_to < day_start:
                continue
            leaves.append((leave.date_from, leave.date_to))
        return leaves

    @api.model
    def interval_without_leaves(self, interval, leave_intervals):
        """ Compute withou leaves late intervals.
        Arguments:
            interval {[Array]} -- [orgin late intervals, (planned and attendance)]
            leave_intervals {[Array]} -- [leave intervals]
        Returns:
            [Array] -- [after leaves we have new late intervals]
        """
        if not interval:
            return interval
        if leave_intervals is None:
            leave_intervals = []
        intervals = []
        # here should be clean repeat leave interval
        # now, I hope not an idiot to repeat the leaves
        # leave_intervals = self.interval_clean(leave_intervals)
        pl_sign_in = interval[0]
        att_sign_in = interval[1]
        # if late
        #  planned                ->|██████████████|
        #  attendance                 ->|██████████|
        interval_start = pl_sign_in
        for leave in leave_intervals:
            leave_start = leave[0]
            leave_end = leave[1]
            if leave_end <= pl_sign_in:
                # Skip odd leaves (Not related to Late).
                #  planned         ->|██████████████|
                #  leaves     |██|<-
                continue
            if leave_start >= att_sign_in:
                # Not related to Late.
                #  planned           |██████████████|
                #  attendance        ->|███████|
                #  leaves                    ->|████|
                break
            if pl_sign_in < leave_start < att_sign_in:
                # work interval inside leave.
                #  planned         ->|██████████████|
                #  attendance            ->|████████|
                #  leaves            ->|█|
                intervals.append((pl_sign_in, leave_start))
                interval_start = leave_end
            if pl_sign_in <= leave_end:
                # Normal leave.
                #  planned         ->|██████████████|
                #  leaves            |███|<-
                interval_start = leave_end
        if interval_start and leave_end < att_sign_in:
            # remove intervals moved outside base interval due to leaves
            #  planned               |██████████████|
            #  attendance                ->|████████|
            #  leaves                |███|<-
            intervals.append((interval_start, att_sign_in))
        return intervals

    @staticmethod
    def _get_float_from_time(time):
        time_type = datetime.strftime(time, "%H:%M")
        signOnP = [int(n) for n in time_type.split(":")]
        signOnH = signOnP[0] + signOnP[1] / 60.0
        return signOnH

    def _handle_late(self, late_in_interval, leaves):
        # if On time
        late_in = timedelta(hours=0, minutes=0, seconds=0)
        if late_in_interval:
            pl_sign_in = late_in_interval[0]
            att_sign_in = late_in_interval[1]
            if att_sign_in > pl_sign_in:
                if not leaves:
                    # Late
                    late_in = att_sign_in - pl_sign_in
                else:
                    # Check leaves interval, and get without leaves interval
                    late_intervals = self.interval_without_leaves(
                        late_in_interval, leaves)
                    for late in late_intervals:
                        late_in += late[1] - late[0]
        return late_in

    def _handle_diff(self, diff_intervals, leaves):
        # if normal sign out
        diff_time = timedelta(hours=00, minutes=00, seconds=00)
        if diff_intervals:
            for diff_in in diff_intervals:
                if leaves:
                    diff_intervals = self.interval_without_leaves(diff_in, leaves)
                    for diff in diff_intervals:
                        diff_time += diff[1] - diff[0]
                else:
                    diff_time += diff_in[1] - diff_in[0]
        return diff_time

    def get_policies_time(self, strategy, policy, period, worked_hours):
        res = period
        flag = False
        msg = ''
        if policy:
            __field = '{}_rule_id'.format(strategy)
            __rule_id = getattr(policy, __field)
            if __rule_id:
                if __rule_id.real_time_ok:
                    flag = True
                    res = period
                else:
                    time_ids =__rule_id.line_ids.sorted(
                        key=lambda r: r.time, reverse=True)
                    for line in time_ids:
                        if period >= line.time:
                            flag = True
                            res = line.deduction_time
                            break
                if not flag:
                    res = 0
                # TODO : flexible worktime hours
                if __rule_id.flexible_ok:
                    if res > 0 and worked_hours >= __rule_id.work_time and res <= __rule_id.allow_time:
                        res = 0
                        msg = _('flexible worktime hours')
        return (res, msg)

    def prepare_common_date(self, **data):
        return {
            'date': data.get('day').strftime('%Y-%m-%d'),
            'day': str(data.get('day').weekday()),
            'plan_sign_in': data.get('plan_sign_in'),
            'plan_sign_out': data.get('plan_sign_out'),
            'sheet_id': self.id,
        }

    def get_overtime_workday(self, policy, period):
        res = []
        val = period
        reduces = 0
        if policy:
            overtime_ids = policy.overtime_rule_ids
            wd_ot_id = policy.overtime_rule_ids.search([('type', '=', 'workday'),('id', 'in', overtime_ids.ids)], order='id', limit=1)
            time_ids = wd_ot_id.line_ids.sorted(key=lambda r: r.time, reverse=True)
            for line in time_ids:
                if period >= line.time:
                    if reduces > round(line.time):
                        val = reduces
                    else:
                        val = val - round(line.time)
                        reduces = round(line.time)
                    res.append((line.pattern, val))         
        return res

    @api.multi
    def settlement_overtime(self):
        overtime_ids = []
        ot_workday_ids = []
        ot_workday_data = []

        for sheet in self:
            if sheet.total_overtime > 0:
                for line in sheet.sheet_line_ids:
                    if line.overtime_type == 'workday':
                        ot_wd_id = self.get_overtime_workday(sheet.policy_id, 
                            line.overtime)
                        if ot_wd_id:
                            ot_workday_ids += ot_wd_id
                    # elif line.overtime_type == 'official':
                    #     TODO : official overtime 
                    # elif line.overtime_type == 'vacation':
                    #     TODO : vacation overtime 
                    # elif line.overtime_type == 'public':
                    #     TODO : public overtime 

            if len(ot_workday_ids) > 0:
                ot_workday_ids = sorted(ot_workday_ids, key=itemgetter(0))
                ot_wd_groups = groupby(ot_workday_ids, key=itemgetter(0))
                ot_wd_data = [{'pattern': k, 'overtime': [x[1] for x in v]}
                        for k, v in ot_wd_groups]
                for ot_wd in ot_wd_data:
                    ot_workday_data.append((0,0, {
                        'pattern': ot_wd['pattern'],
                        'num_overtime': len(ot_wd['overtime']),
                        'total_overtime': sum(ot_wd['overtime']),
                        'type': 'workday',
                        'sheet_id': sheet.id
                    }))
            overtime_ids += ot_workday_data
            sheet.write({
                'overtime_ids': overtime_ids,
            })


    # Action

    @api.multi
    def action_confirm(self):
        for records in self:
            records.write({'state': 'confirm'})
            for line in records.sheet_line_ids:
                line.write({'state': 'confirm'})
        return True

    @api.multi
    def action_approve(self):
        for records in self:
            records.settlement_attendance_data()
            
            records.write({'state': 'done'})
            for line in records.sheet_line_ids:
                line.write({'state': 'done'})
        return True

    @api.multi
    def action_draft(self):
        for records in self:
            records.write({'state': 'draft'})
            for line in records.sheet_line_ids:
                line.write({'state': 'draft'})
        return True

    def get_worked_days_line(self, strategy, contract, sheet, sequence):
        __num_day = 'num_{}'.format(strategy)
        __total_hour = 'total_{}'.format(strategy)
        return [{
            'name': strategy,
            'code': strategy.upper(),
            'contract_id': contract,
            'sequence': sequence,
            'number_of_days': getattr(sheet, __num_day),
            'number_of_hours': getattr(sheet, __total_hour),
        }]

    def get_overtime_line(self, name, strategy, contract, overtime_id, sequence):
        return [{
            'name': name,
            'code': strategy.upper(),
            'contract_id': contract,
            'sequence': sequence,
            'number_of_days': overtime_id.num_overtime,
            'number_of_hours': overtime_id.total_overtime,
        }]

    def prepare_payslip(self, sheet, contract_id, slip_data, worked_days_line_ids):
        return {
            'employee_id': sheet.employee_id.id,
            'name': slip_data['value'].get('name'),
            'struct_id': slip_data['value'].get('struct_id'),
            'contract_id': contract_id,
            'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
            'worked_days_line_ids': [(0, 0, x) for x in worked_days_line_ids],
            'date_from': sheet.date_from,
            'date_to': sheet.date_to,
        }

    @api.multi
    def action_create_payslip(self):
        payslips = self.env['hr.payslip']
        contract = self.env['hr.contract']
        for sheet in self:
            if sheet.payslip_id:
                payslip = sheet.payslip_id
                continue
            date_from = sheet.date_from
            date_to = sheet.date_to
            employee = sheet.employee_id
            slip_data = payslips.onchange_employee_id(
                date_from, date_to, employee.id, contract_id=False)
            contract_id = slip_data['value'].get('contract_id')
            if not contract_id:
                raise UserError(
                    'The %s contract does not cover the period for the attendance sheet' % employee.name)
            else:
                payslip = payslips.search([
                    ('date_from', '=', date_from),
                    ('date_to', '=', date_to),
                    ('employee_id', '=', employee.id),
                    ('contract_id', '=', contract_id),
                ], order='id', limit=1)
            worked_days_line_ids = slip_data['value'].get('worked_days_line_ids')
            absence = self.get_worked_days_line('absence', contract_id, sheet, 90)
            late = self.get_worked_days_line('late', contract_id, sheet, 91)
            diff = self.get_worked_days_line('diff', contract_id, sheet, 92)
            overtime_sheet = []
            for overtime_id in sheet.overtime_ids:
                name = overtime_id.type + ' overtime ' + overtime_id.pattern
                code = 'ot' + overtime_id.type + overtime_id.pattern
                overtime_sheet += self.get_overtime_line(
                    name, code, contract_id, overtime_id, 93)
                
            line_ids = absence + late + diff + overtime_sheet
            if payslip:
                payslip.worked_days_line_ids = [(0, 0, x) for x in line_ids]
            else:
                worked_days_line_ids += line_ids
                payslip_data = self.prepare_payslip(sheet, contract_id, slip_data, worked_days_line_ids)
                jounral_id = contract.browse(contract_id).journal_id
                payslip = payslips.sudo().with_context(
                    journal_id=jounral_id and jounral_id.id
                ).create(payslip_data)
            sheet.payslip_id = payslip

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': payslip.id,
            'views': [(False, 'form')],
        }

    def get_dayofweek_type(self, day, calender_id):
        overtime_type = 'workday'
        day_weekday = day.weekday()
        rest_day = calender_id.rest_day
        mandatory_day = calender_id.mandatory_day
        if calender_id.two_days_off:
            if day_weekday== rest_day:
                overtime_type = 'vacation'
            elif day_weekday == mandatory_day:
                overtime_type = 'official'
        return overtime_type

    @api.multi
    def unlink_unprocess(self, sheet):
        return sheet.sheet_line_ids.filtered(lambda r: not r.is_processed)

    @api.multi
    def compute_attendances(self):
        for sheet in self:
            # 
            unprocess = self.unlink_unprocess(sheet)
            unprocess.unlink()
            # sheet.sheet_line_ids.unlink()
            sheet_line = self.env['hr.attendance.sheet.line']
            timezone = self.get_timezone()
            # Get information related to employee_id
            employee_id = sheet.employee_id
            calender_id = self.get_resource_calendar_id(employee_id)
            policy_id = self.get_attendance_policy(sheet, employee_id)
            # Calculate all numbers between date_from and date_to
            date_from = datetime.combine(sheet.date_from, datetime.min.time())
            date_to = datetime.combine(sheet.date_to, datetime.min.time())
            all_dates = [(date_from + relativedelta(days=x))
                         for x in range((date_to - date_from).days + 1)]
            for day in all_dates:
                overtime_type = self.get_dayofweek_type(day, calender_id)
                day_end = day.replace(hour=23, minute=59,
                                      second=59, microsecond=999999)
                overtime = timedelta(hours=00, minutes=00, seconds=00)
                worked_hours = timedelta(hours=00, minutes=00, seconds=00)
                leaves = self.get_employee_leave_intervals(
                    employee_id, day, day_end)
                work_intervals = self.get_work_intervals(
                    calender_id, day, day_end)
                # TODO : Need to handle exceptions (No Sign out)
                attendance_intervals = self.get_attendance_intervals(
                    employee_id, day, day_end)
                note = ''
                is_continue = sheet.sheet_line_ids.filtered(
                    lambda r: r.is_processed and str(r.date) == day.strftime('%Y-%m-%d')
                )
                if len(is_continue):
                    continue

                for i, work_interval in enumerate(work_intervals):
                    pl_sign_in = work_interval[0]
                    pl_sign_out = work_interval[1]
                    plan_sign_in = self._get_float_from_time(
                        pytz.utc.localize(pl_sign_in).astimezone(timezone))
                    plan_sign_out = self._get_float_from_time(
                        pytz.utc.localize(pl_sign_out).astimezone(timezone))
                    values = self.prepare_common_date(**{
                        'day': day,
                        'plan_sign_in': plan_sign_in,
                        'plan_sign_out': plan_sign_out,
                    })
                    att_work_intervals = []
                    diff_intervals = []
                    late_in_interval = []
                    for j, att_interval in enumerate(attendance_intervals):
                        # print('work[0]', work_interval[0])
                        # print('att[0]', att_interval[0])
                        # print('max:', max(work_interval[0], att_interval[0]))
                        # print('work[1]', work_interval[1])
                        # print('att[1]', att_interval[1])
                        # print('min:', min(work_interval[1], att_interval[1]))
                        att_work_intervals.append(att_interval)
                    actual_sign_in = 0
                    actual_sign_out = 0
                    status = ""
                    is_processed = False
                    worked_hours = 0
                    if att_work_intervals:
                        # declare
                        att_sign_in = att_work_intervals[0][0]
                        att_sign_out = att_work_intervals[-1][1]
                        is_processed = True
                        # get late and overtime interval
                        # if late
                        #  planned                 ->|██████████████|
                        #  attendance                  ->|██████████|
                        late_in_interval = (pl_sign_in, att_sign_in)

                        # Overtime
                        if att_sign_out < pl_sign_out:
                            # excused
                            #  planned               |██████████████|<-
                            #  attendance            |██████████|<-
                            overtime = timedelta(hours=0, minutes=0, seconds=0)
                            diff_intervals.append((att_sign_out, pl_sign_out))
                        else:
                            # Work Overtime
                            #  planned               |██████████████|<-
                            #  attendance            |█████████████████|<-
                            if att_sign_in <= pl_sign_in:
                                # TODO : need to change this way (to ugly)
                                if policy_id:
                                    overtime_ids = policy_id.overtime_rule_ids
                                    wd_ot_id = policy_id.overtime_rule_ids.search([('type', '=', overtime_type),('id', 'in', overtime_ids.ids)], order='id', limit=1)
                                    if wd_ot_id.need_post:
                                        overtime = timedelta(hours=0, minutes=0, seconds=0)
                                    else:
                                        overtime = att_sign_out - pl_sign_out
                        # TODO : Need to check (multi sign in / multi sign out)
                        actual_sign_in = self._get_float_from_time(
                            pytz.utc.localize(att_sign_in).astimezone(timezone))
                        actual_sign_out = self._get_float_from_time(
                            pytz.utc.localize(att_sign_out).astimezone(timezone))
                        worked_hours = actual_sign_out - actual_sign_in
                        
                        if len(att_work_intervals) > 1:
                            # attendances for multiple sessions per day
                            #  planned                |██████████████|
                            #  attendance               |███|    |███|
                            diff_intervals = []  # recompute diff intervals
                            first_time_sign_out = attendance_intervals[0][1]
                            current_sign_out = first_time_sign_out
                            for att_work_interval in attendance_intervals:
                                current_time_sign_in = att_work_interval[0]
                                current_time_sign_out = att_work_interval[1]
                                if current_time_sign_out <= first_time_sign_out:
                                    # skip first time sign out (normal attendance).
                                    #  planned         |██████████████|
                                    #  attendance        |███|<-  |███|
                                    continue
                                if current_time_sign_in >= pl_sign_out:
                                    # other case, here no consider.
                                    #  planned         |██████████████|<-
                                    #  attendance                       ->|███|
                                    break
                                if current_sign_out < current_time_sign_in < pl_sign_out:
                                    # middle section.
                                    #  planned         |██████████████|<-
                                    #  attendance       |██|<- ->|███|
                                    diff_intervals.append((current_sign_out, current_time_sign_in))
                                    float_sign_in = self._get_float_from_time(
                                        pytz.utc.localize(current_time_sign_in).astimezone(timezone))
                                    float_sign_out = self._get_float_from_time(
                                        pytz.utc.localize(current_sign_out).astimezone(timezone))
                                    worked_hours -= (float_sign_in - float_sign_out)
                                    note = _('Leave midway')
                                    current_sign_out = current_time_sign_out
                                    
                            if current_sign_out and current_sign_out <= pl_sign_out:
                                # last time attendance diff time.
                                #  planned             |██████████████|<-
                                #  attendance             |██|  |███|<-
                                diff_intervals.append((current_sign_out, pl_sign_out))
                    else:
                        # Handle Absence Day
                        late_in_interval = []
                        diff_intervals.append((pl_sign_in, pl_sign_out))
                        status = "absence"
                    
                    # Handle Diffance Time
                    diff_time = self._handle_diff(diff_intervals, leaves)
                    float_diff = diff_time.total_seconds() / 3600
                    policy_diff = self.get_policies_time('diff', policy_id, float_diff, worked_hours)
                    note += '\n' + policy_diff[1] if note else policy_diff[1]

                    # Handle Late Time
                    late_in = self._handle_late(late_in_interval, leaves)
                    float_late = late_in.total_seconds() / 3600
                    policy_late = self.get_policies_time('late', policy_id, float_late, worked_hours)
                    note += '\n' + policy_late[1] if note else policy_late[1]

                    # TODO : Overtime policies
                    float_overtime = overtime.total_seconds() / 3600

                    # Leave Stutus
                    if leaves:
                        status = "leave"

                    # Create Attendance Sheet Data
                    values.update({
                        'diff_time': policy_diff[0],
                        'late_in': policy_late[0],
                        'overtime': float_overtime,
                        'actual_sign_in': actual_sign_in,
                        'actual_sign_out': actual_sign_out,
                        'worked_hours': worked_hours,
                        'overtime_type': overtime_type,
                        'status': status,
                        'note': note,
                        'is_processed': is_processed,
                    })
                    sheet_line.create(values)


    @api.model
    def create_employee_attendance_sheet(self):
        self = self.with_context(ir_cron=True)
        employees = self.env['hr.employee'].search([('active', '=', True)])
        for employee in employees:
            if not len(employee.contract_ids):
                continue
            attendance_sheet = self.new({
                'employee_id': employee.id,
                'date_from': fields.Date.to_string(date.today().replace(day=1)),
                'date_to': fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())
            })
            attendance_sheet.onchange_employee()
            if attendance_sheet.policy_id:
                attendance_sheet = self.create({
                    'employee_id': employee.id,
                    'name': attendance_sheet.name,
                    'policy_id': attendance_sheet.policy_id.id
                })


class AttendanceSheetLine(models.Model):
    _name = 'hr.attendance.sheet.line'
    _order = 'date'

    employee_id = fields.Many2one(
        string='Employee',
        related='sheet_id.employee_id',
        readonly=True,
        store=True
    )
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
    day = fields.Selection(
        string='Day',
        selection=[
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ],
    )
    sheet_id = fields.Many2one(
        string='Attendance Sheet',
        comodel_name='hr.attendance.sheet',
        readonly=True
    )
    plan_sign_in = fields.Float(string="Planned sign in", readonly=True)
    plan_sign_out = fields.Float(string="Planned sign out", readonly=True)
    actual_sign_in = fields.Float(string="Actual sign in", readonly=True)
    actual_sign_out = fields.Float(string="Actual sign out", readonly=True)
    overtime_type = fields.Selection(selection=[
        ('workday', 'Working Day'),
        ('official', 'Weekly Official Holidays'),
        ('vacation', 'Vacation day'),
        ('public', 'Public Holiday')
    ], string="Type")

    overtime = fields.Float(string="Work OverTime", readonly=True)
    late_in = fields.Float(string="Late In", readonly=True)
    diff_time = fields.Float(
        string="Diffrence Time",
        readonly=True,
        help="Diffrence between the working time and attendance time(s) ",
    )
    # TODO : user post change to manager, and manager need viled (add feature)
    change_late_in = fields.Float(string="Change")
    change_diff_time = fields.Float(string="Change")
    change_overtime = fields.Float(string="Change")
    
    worked_hours = fields.Float(string="Worked Hours", readonly=True)
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
    # Maybe Dobtor Check or Somthing Condiation for approve
    approve_status = fields.Selection(
        string="Approve Status",
        selection=[
            ('disapprove', 'Disapprove'),
            ('approve', 'Approve')
        ],
        default='disapprove',
    )
    approve_date = fields.Datetime('Approve Date')
    is_processed = fields.Boolean('Has the attendance been post processed', default=False)

    @api.multi
    def action_approve(self):
        for line in self:
            origin_late_in = line.late_in
            origin_diff_time = line.diff_time
            origin_overtime = line.overtime

            line.late_in = line.change_late_in
            line.diff_time = line.change_diff_time
            line.overtime = line.change_overtime
            # origin data
            line.change_late_in = origin_late_in
            line.change_diff_time = origin_diff_time
            line.change_overtime = origin_overtime

            line.approve_date = fields.Datetime.now()
            line.approve_status = 'approve'

    @api.multi
    def action_disapprove(self):
        for line in self:
            if line.approve_status == 'approve':
                origin_late_in = line.change_late_in
                origin_diff_time = line.change_diff_time
                origin_overtime = line.change_overtime

                line.change_late_in = line.late_in
                line.change_diff_time = line.diff_time
                line.change_overtime = line.overtime

                line.late_in = origin_late_in
                line.diff_time = origin_diff_time
                line.overtime = origin_overtime

            line.approve_date = None
            line.approve_status = 'disapprove'


class AttendanceSheetOvertime(models.Model):
    _name = 'hr.attendance.sheet.overtime'

    name = fields.Char()
    sheet_id = fields.Many2one(
        string='Attendance Sheet',
        comodel_name='hr.attendance.sheet',
        readonly=True
    )
    total_overtime = fields.Float(
        string="Total Overtime",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    num_overtime = fields.Integer(
        string="Number of Overtime",
        compute="settlement_attendance_data",
        readonly=True,
        store=True
    )
    type = fields.Selection(selection=[
        ('workday', 'Working Day'),
        ('official', 'Weekly Official Holidays'),
        ('vacation', 'Vacation day'),
        ('public', 'Public Holiday')
    ], string="Type")
    pattern = fields.Selection(selection=[
        ('1', '1'),
        ('2', '1.34'),
        ('3', '1.67'),
        ('4', '2'),
        ('5', '2.67'),
    ], string="pattern")
