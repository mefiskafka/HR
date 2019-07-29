# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AbstractContributionRatio(models.AbstractModel):
    _name = 'abstract.resource.contribution_ratio'

    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        return '{}-01-01'.format(year)

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
    start_date = fields.Date(string='Start Date')

    @api.depends('employer_ratio', 'employee_ratio', 'government_ratio')
    def _compute_contribution_ratio(self):
        for record in self:
            record.contribution_ratio = '{}-{}-{}'.format(record.employer_ratio, record.employee_ratio, record.government_ratio)
