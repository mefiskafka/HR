# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _
from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrLeave(models.Model):
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
    # The Rules are prescribed pursuant to Article 43 of the Labor Standards Act
    

    

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    # duration
    gov_ok = fields.Boolean(
        'Government leave',
        related='holiday_status_id.gov_ok'
    )
    gov_leave_type = fields.Selection(
        'Gov leave type',
        related='holiday_status_id.gov_leave_type'
    )
    bereavement_type = fields.Selection(
        string='Bereavement leave type',
        selection=[
            ('3', 'On the death of great-grandparent, brother or sister, grand-parent of spouse'),
            ('6', 'On the death of grand-parent, son or daughter, parent of spouse, foster-parent or step-parent of spouse'),
            ('8', 'On the death of parent, foster-parent, step-parent, spouse'),
        ]
    )
    maternity_type = fields.Selection(
        string='Maternity leave type',
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

    @api.onchange('gov_leave_type')
    def _onchange_gov_leave_type(self):
        if self.gov_ok and self.employee_id:
            if self.gov_leave_type == 'marriage':
                self.number_of_days = 8

    @api.onchange('maternity_type')
    def _onchange_maternity_type(self):
        if self.gov_ok and self.employee_id:
            if self.gov_leave_type == 'maternity' and self.maternity_type:
                if self.employee_id.gender == 'male':
                    self.number_of_days = 8
                elif self.employee_id.gender == 'female':
                    if self.maternity_type == '5day':
                        self.number_of_days = 5
                    elif self.maternity_type == '1week':
                        self.number_of_days = 7
                    elif self.maternity_type == '4week':
                        self.number_of_days = 7*4
                    elif self.maternity_type == '8week':
                        self.number_of_days = 7*8
