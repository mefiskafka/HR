# -*- coding: utf-8 -*-
import calendar
from dateutil.relativedelta import relativedelta
from odoo import models, tools, fields, api, _
from odoo.exceptions import ValidationError


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

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super().get_worked_day_lines(contracts, date_from, date_to)
        for item in res:
            leave_type = self.env['hr.leave.type'].search([('name', '=', item['code'])], limit=1)
            item['code'] = leave_type.code or item['code'] 
        return res

