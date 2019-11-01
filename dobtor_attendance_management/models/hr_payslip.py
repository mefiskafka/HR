# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, tools, fields, api, _
from odoo.exceptions import ValidationError
from pytz import timezone
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    returning_hr = fields.Boolean(
        string='returning employees',
        default=False,
    )
    init_employment_date = fields.Date(
        string='Initial Date of Employment',
    )
    month_of_service = fields.Float(
        'Months of Service',
        compute='_compute_months_service',
    )
    year_of_service = fields.Float(
        'Years of Service',
        compute='_compute_months_service',
    )

    def _first_contract(self):
        hr_contract = self.env['hr.contract'].sudo()
        return hr_contract.search([('employee_id', '=', self.id)],
                                  order='date_start asc', limit=1)

    @staticmethod
    def check_next_days(date_to, date_from):
        if date_from.day != 1:
            return 0
        days_in_month = calendar.monthrange(date_to.year, date_to.month)[1]
        return 1 if date_to.day == days_in_month or \
                    date_from.day == date_to.day + 1 else 0

    @api.depends('contract_ids', 'init_employment_date')
    def _compute_months_service(self):
        date_now = fields.Date.today()
        hr_contract = self.env['hr.contract'].sudo()
        for employee in self:
            nb_month = 0

            if employee.returning_hr and employee.init_employment_date:
                first_contract = employee._first_contract()
                if first_contract:
                    to_dt = fields.Date.from_string(first_contract.date_start)
                else:
                    to_dt = fields.Date.from_string(date_now)

                from_dt = fields.Date.from_string(
                    employee.init_employment_date)

                nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                    relativedelta(to_dt, from_dt).months + \
                    self.check_next_days(to_dt, from_dt)

            contracts = hr_contract.search([('employee_id', '=', employee.id)],
                                           order='date_start asc')
            for contract in contracts:
                from_dt = fields.Date.from_string(contract.date_start)
                if contract.date_end and contract.date_end < date_now:
                    to_dt = fields.Date.from_string(contract.date_end)
                else:
                    to_dt = fields.Date.from_string(date_now)
                nb_month += relativedelta(to_dt, from_dt).years * 12 + \
                    relativedelta(to_dt, from_dt).months + \
                    self.check_next_days(to_dt, from_dt)

            employee.month_of_service = nb_month
            employee.year_of_service = nb_month / 12.0

    @api.constrains('init_employment_date', 'contract_ids')
    def _check_initial_employment_date(self):
        if self.init_employment_date and self.contract_ids:
            initial_dt = fields.Date.from_string(self.init_employment_date)
            first_contract_dt = fields.Date.from_string(
                self._first_contract().date_start)
            if initial_dt < first_contract_dt:
                raise ValidationError(_(
                    "The initial employment date "
                    "cannot be before the first "
                    "contract in the system!"))


class HrContract(models.Model):
    _inherit = 'hr.contract'

    policy_id = fields.Many2one(
        string='Attendance Policy',
        comodel_name='hr.attendance.policies'
    )


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # @api.model
    # def get_worked_day_lines(self, contracts, date_from, date_to):
    #     res = super().get_worked_day_lines(contracts, date_from, date_to)
    #     for item in res:
    #         leave_type = self.env['hr.leave.type'].search([('name', '=', item['code'])], limit=1)
    #         item['code'] = leave_type.code or item['code']

    #     # TODO : translate unfinished annual leave
    #     if date_to == date(date_to.year, 12, 31):
    #         print('')
    #     return res

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(
                fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(
                fields.Date.from_string(date_to), time.max)

            # compute leave days
            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(
                day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.code or holiday.holiday_status_id.name or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                })
                current_leave_struct['number_of_hours'] += min(
                    hours, calendar.hours_per_day or calendar.HOURS_PER_DAY)
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(day, time.min)),
                    tz.localize(datetime.combine(day, time.max)),
                    compute_leaves=False,
                )
                if work_hours:
                    if calendar.hours_per_day:
                        work_hours = min(work_hours, calendar.hours_per_day)
                    else:
                        work_hours = min(work_hours, calendar.HOURS_PER_DAY)
                    current_leave_struct['number_of_days'] += min(
                        hours, calendar.hours_per_day or calendar.HOURS_PER_DAY) / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(
                day_from, day_to, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }
            res.append(attendances)
            
            # compute unfinished annual leave
            if date_to == date(date_to.year, 12, 31):
                leave_allocation = self.env['hr.leave.allocation'].search([
                    ('holiday_type', '=', 'employee'),
                    ('employee_id', '=', contract.employee_id.id),
                    ('gov_ok', '=', 'True'),
                    ('gov_leave_type', '=', 'annual'),
                    ('annual_to', '=', date(date_to.year, 12, 31)),
                ], limit=1)
                if leave_allocation:
                    leave_days = leave_allocation.holiday_status_id.get_days(leave_allocation.employee_id.id)[
                        leave_allocation.holiday_status_id.id]
                    virtual_remaining_leaves = leave_days['virtual_remaining_leaves']
                    unfinished_annual = {
                        'name': _("Unfinished Annual Leave"),
                        'sequence': 5,
                        'code': 'UANNUAL',
                        'number_of_days': virtual_remaining_leaves / (calendar.hours_per_day or calendar.HOURS_PER_DAY),
                        'number_of_hours': virtual_remaining_leaves,
                        'contract_id': contract.id,
                    }
                    res.append(unfinished_annual)
            res.extend(leaves.values())
        return res
