# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AbstractContributionRatio(models.AbstractModel):
    _name = 'abstract.resource.contribution_ratio'

    # def _get_default_start_date(self):
    #     year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
    #     return '{}-01-01'.format(year)

    name = fields.Char(
        string='Title',
    )
    employer_ratio = fields.Float(
        string='Employer Ratio',
    )
    employee_ratio = fields.Float(
        string='Employee Ratio',
    )
    government_ratio = fields.Float(
        string='Government Ratio',
    )
    contribution_ratio = fields.Char(
        string='Contribution Ratio',
        compute='_compute_contribution_ratio',
    )
    # start_date = fields.Date(string='Start Date')

    @api.depends('employer_ratio', 'employee_ratio', 'government_ratio')
    def _compute_contribution_ratio(self):
        for record in self:
            record.contribution_ratio = '{:.0f}%-{:.0f}%-{:.0f}%'.format(
                record.employer_ratio, record.employee_ratio, record.government_ratio)

    @api.constrains('employer_ratio', 'employee_ratio', 'government_ratio')
    def _check_ratio_validation(self):
        """  validation at ratio create time. """
        for record in self:
            if record.employer_ratio > 100:
                raise ValidationError(
                    _("Employer Ratio has to be less then 100"))
            if record.employer_ratio < 0.0:
                raise ValidationError(
                    _("Please enter Some Value for Employer Ratio"))
            if record.employee_ratio > 100:
                raise ValidationError(
                    _("Employee Ratio has to be less then 100"))
            if record.employee_ratio < 0.0:
                raise ValidationError(
                    _("Please enter Some Value for Employee Ratio"))
            if record.government_ratio > 100:
                raise ValidationError(
                    _("Government Ratio has to be less then 100"))
            if record.government_ratio < 0.0:
                raise ValidationError(
                    _("Please enter Some Value for Government Ratio"))
