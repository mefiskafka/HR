# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            return employee.get_work_days_data(date_from, date_to)['days']

        today_hours = self.env.user.company_id.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)
        #  TODO : need to change
        if self.env.user.company_id.resource_calendar_id.hours_per_day:
            today_hours = min(
                today_hours, self.env.user.company_id.resource_calendar_id.hours_per_day)
        else:
            today_hours = min(today_hours, HOURS_PER_DAY)
        return self.env.user.company_id.resource_calendar_id.get_work_hours_count(date_from, date_to) / (today_hours)

    @api.multi
    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):
        for holiday in self:
            calendar = holiday.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
            if holiday.date_from and holiday.date_to:
                number_of_hours = calendar.get_work_hours_count(
                    holiday.date_from, holiday.date_to)
                #  TODO : need to change
                hour_per_day = calendar.hours_per_day or HOURS_PER_DAY
                holiday.number_of_hours_display = min(number_of_hours, (
                    holiday.number_of_days * hour_per_day))
            else:
                holiday.number_of_hours_display = 0


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    gov_ok = fields.Boolean(
        string='Government leave',
        default=False
    )
    code = fields.Char(help="The code that can be used in the salary rules")
    gov_leave_type = fields.Selection(
        string='Gov Leave type',
        selection=[
            ('annual', 'Annual Leave'),
            ('bereavement', 'Bereavement Leave'),
            ('marriage', 'Marriage Leave'),
            ('maternity', 'Maternity Leave'),
        ]
    )

    @api.multi
    def get_days(self, employee_id):
        result = super().get_days(employee_id)
        requests = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids)
        ])
        allocations_all = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('gov_leave_type', '=', 'annual'),
            ('holiday_status_id', 'in', self.ids)
        ])
        allocations_annual = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee_id),
            ('state', 'in', ['confirm', 'validate1', 'validate']),
            ('holiday_status_id', 'in', self.ids),
            ('gov_leave_type', '=', 'annual'),
            ('annual_to', '<', date.today())
        ])
        allocations = allocations_all - allocations_annual
        request_annual_virtual_remaining_leaves = 0.00
        allocation_day = 0.00
        requestes = self.env['hr.leave']
        i = 0

        for allocation_annual in allocations_annual:
            i += 1
            # expired allocations leave.
            if allocation_annual.gov_leave_type == 'annual':
                status_dict = result[allocation_annual.holiday_status_id.id]
                allocation_day = (allocation_annual.number_of_hours_display
                                              if allocation_annual.type_request_unit == 'hour'
                                              else allocation_annual.number_of_days)
                status_dict['max_leaves'] -= allocation_day
                status_dict['virtual_remaining_leaves'] = 0
                status_dict['remaining_leaves'] = 0
                if not len(allocations):
                    for request_annual in requests.filtered(lambda r: r.request_date_to > allocation_annual.annual_to and r.holiday_status_id == allocation_annual.holiday_status_id):
                        request_annual_virtual_remaining_leaves = (request_annual.number_of_hours_display
                                                             if request_annual.leave_type_request_unit == 'hour'
                                                             else request_annual.number_of_days)
                        status_dict['virtual_remaining_leaves'] -= request_annual_virtual_remaining_leaves
                        if request_annual.state == 'validate':
                            status_dict['remaining_leaves'] -= request_annual_virtual_remaining_leaves
                    for request_old in requests.filtered(lambda r: r.holiday_status_id == allocation_annual.holiday_status_id) - requests.filtered(lambda r: r.request_date_to > allocation_annual.annual_to and r.holiday_status_id == allocation_annual.holiday_status_id):
                        # You cannot request expired allocations leave.
                        #  today :                                 |█|
                        #  allocation annual :   |██████████████|
                        #  request leave :                 |██|         
                        if request_old.create_date.date() == date.today():
                            status_dict['virtual_remaining_leaves'] = -1
                            status_dict['remaining_leaves'] = -1
                else:
                    # find last expired allocation annual
                    #  today :                                 |█|
                    #  allocation annual :             |██████████████|
                    #  allocation annual :   |██████████████|
                    #  request leave :                  |██|
                    if len(allocations_annual) == i:
                        check_requestes = requests.filtered(lambda r: r.request_date_to <= allocation_annual.annual_to and r.holiday_status_id == allocation_annual.holiday_status_id)     
                        # count requestes day and max_leave
                        check_request_leaves = 0.0
                        for request in requestes:
                            check_request_leaves += (request.number_of_hours_display
                                                 if request.leave_type_request_unit == 'hour'
                                                 else request.number_of_days)
                        if check_request_leaves <= allocation_day:
                            requestes = check_requestes
                        else:
                            # TODO : handle overlapping leave and allocation_day > check_request_leaves
                            requestes = check_requestes

        allocation_virtual_remaining_leaves = 0.00
        j = 0.00
        for allocation in allocations:
            # normal
            #  allocation annual :   |██████████████|
            #  request leave :                 |██|   
            status_dict = result[allocation.holiday_status_id.id]
            j += 1
            if allocation.gov_leave_type == 'annual' and status_dict['virtual_remaining_leaves'] == 0:
                if len(allocations) == j:
                    requestes = requests.filtered(
                        lambda r: r.request_date_to <= allocation.annual_to and r.holiday_status_id == allocation.holiday_status_id) - requestes
                
                if allocation.state == 'validate':
                    allocation_virtual_remaining_leaves = (allocation.number_of_hours_display
                                                        if allocation.type_request_unit == 'hour'
                                                        else allocation.number_of_days)
                    status_dict['virtual_remaining_leaves'] += allocation_virtual_remaining_leaves
                    status_dict['remaining_leaves'] += allocation_virtual_remaining_leaves
        # if no expired allocation annual, but request leave over-time
        #  allocation annual :   |██████████████|
        #  request leave :                         |██|
        if len(allocations) == 1:
            request_over_time = requests.filtered(
                lambda r: r.request_date_to > allocations[0].annual_to and r.holiday_status_id == allocations[0].holiday_status_id)
            if len(request_over_time) > 1:
                raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                    'Please also check the leaves waiting for validation.'))
        
        request_virtual_remaining_leaves = 0.00
        for request in requestes:
            request_virtual_remaining_leaves = (request.number_of_hours_display
                                                if request.leave_type_request_unit == 'hour'
                                                else request.number_of_days)
            status_dict['virtual_remaining_leaves'] -= request_virtual_remaining_leaves
            if request.state == 'validate':
                status_dict['remaining_leaves'] -= request_virtual_remaining_leaves

        return result
    # The Rules are prescribed pursuant to Article 43 of the Labor Standards Act


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    # duration
    gov_ok = fields.Boolean(
        'Government leave',
        store=True,
        related='holiday_status_id.gov_ok'
    )
    gov_leave_type = fields.Selection(
        'Gov leave type',
        store=True,
        related='holiday_status_id.gov_leave_type'
    )
    annual_year = fields.Selection(
        string='Annual year',
        selection=[
            ('0.5_3', '0.5'),
            ('1_7', '1'),
            ('2_10', '2'),
            ('3_14', '3'),
            ('4_14', '4'),
            ('5_15', '5'),
            ('6_15', '6'),
            ('7_15', '7'),
            ('8_15', '8'),
            ('9_15', '9'),
            ('10_16', '10'),
            ('11_17', '11'),
            ('12_18', '12'),
            ('13_19', '13'),
            ('14_20', '14'),
            ('15_21', '15'),
            ('16_22', '16'),
            ('17_23', '17'),
            ('18_24', '18'),
            ('19_25', '19'),
            ('20_26', '20'),
            ('21_27', '21'),
            ('22_28', '22'),
            ('23_29', '23'),
            ('24_30', '24'),
            ('over25_30', _('over 25')),
        ]
    )
    annual_to = fields.Date(
        string='annual date to',
    )
    # annual_from = fields.Date(
    #     string='annual date from',
    # )
    bereavement_type = fields.Selection(
        string='Bereavement leave',
        selection=[
            ('3', 'On the death of great-grandparent, brother or sister, grand-parent of spouse'),
            ('6', 'On the death of grand-parent, son or daughter, parent of spouse, foster-parent or step-parent of spouse'),
            ('8', 'On the death of parent, foster-parent, step-parent, spouse'),
        ]
    )
    maternity_type = fields.Selection(
        string='Maternity leave',
        selection=[
            ('5day', 'miscarriage, occurs less than two months into the pregnancy'),
            ('1week', 'miscarriage, occurs two to three months into the pregnancy'),
            ('4week', 'miscarriage, occurs after three months of pregnancy'),
            ('8week', 'after childbirth'),
        ]
    )

    @api.onchange('bereavement_type')
    def _onchange_bereavement_type(self):
        if self.gov_ok and self.employee_id:
            if self.gov_leave_type == 'bereavement' and self.bereavement_type:
                self.number_of_days = int(self.bereavement_type)
            else:
                self.number_of_days = 0

    @api.onchange('maternity_type')
    def _onchange_maternity_type(self):
        if self.gov_ok and self.employee_id:
            if self.gov_leave_type == 'maternity' and self.maternity_type:
                if self.employee_id.gender == 'male':
                    if self.maternity_type == '8week':
                        self.number_of_days = 5
                    else:
                        self.number_of_days = 0
                elif self.employee_id.gender == 'female':
                    if self.maternity_type == '5day':
                        self.number_of_days = 5
                    elif self.maternity_type == '1week':
                        self.number_of_days = 5
                    elif self.maternity_type == '4week':
                        self.number_of_days = 5*4
                    elif self.maternity_type == '8week':
                        self.number_of_days = 5*8
                else:
                    self.number_of_days = 0

    @api.onchange('annual_year')
    def _onchange_annual_year(self):
        if self.gov_ok and self.employee_id:
            if self.gov_leave_type == 'annual' and self.annual_year:
                annual_split = self.annual_year.split("_")
                self.number_of_days = int(annual_split[1])

    @api.onchange('gov_leave_type')
    def _onchange_gov_leave_type(self):
        if self.gov_ok and self.employee_id:
            if self.gov_leave_type == 'marriage':
                self.number_of_days = 8

    @api.model
    def compute_annual_leaves(self):
        employees = self.env['hr.employee'].search([('active', '=', True)])
        for employee in employees:
            year = 0
            #  TODO : HOURS_PER_DAY need to change company_id resource_calendar_id
            days = 0
            if employee.year_of_service:
                if 0.5 < employee.year_of_service < 1:
                    year = 0.5
                    days = 3
                elif employee.year_of_service >= 1:
                    year = int(employee.year_of_service)
                    if 1 <= employee.year_of_service < 2:
                        days = 7
                    elif 2 <= employee.year_of_service < 3:
                        days = 10
                    elif 3 <= employee.year_of_service < 5:
                        days = 14
                    elif 5 <= employee.year_of_service < 10:
                        days = 15
                    elif 10 <= employee.year_of_service:
                        days = (15 + (int(employee.year_of_service)-9))
            annual_year = '{}_{}'.format(str(year), str(
                days)) if year <= 24 else 'over25_30'
            days = 30 if days > 30 else days
            hours = days * HOURS_PER_DAY
            annual_allocation = self.env['hr.leave.allocation'].search([
                ('gov_ok', '=', 'True'),
                ('gov_leave_type', '=', 'annual'),
                ('holiday_type', '=', 'employee'),
                ('employee_id', '=', employee.id),
                ('annual_year', '=', annual_year)
            ], limit=1)
            if not annual_allocation and year:
                annual_type = self.env['hr.leave.type'].search([
                    ('gov_ok', '=', 'True'),
                    ('gov_leave_type', '=', 'annual'),
                ], limit=1)
                if annual_type:
                    data = {
                        'name': "{}'s {} annual leave".format(employee.name, year),
                        'annual_year': annual_year,
                        'holiday_type': 'employee',
                        'gov_leave_type': 'annual',
                        'gov_ok': 'gov_ok',
                        'holiday_status_id': annual_type.id,
                        'number_of_days': hours / (employee.resource_calendar_id.hours_per_day or HOURS_PER_DAY),
                        'employee_id': employee.id,
                        # TODO : need to change, this case for acqu
                        # 'annual_from': date()
                        'annual_to': date((datetime.now() + relativedelta(years=1)).year, 12, 31)
                    }
                    annual_allocation = self.env['hr.leave.allocation'].create(
                        data)
                    annual_allocation.sudo().action_approve()
