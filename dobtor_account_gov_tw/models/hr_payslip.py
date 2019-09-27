# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    # ordinary insurance
    ordinary_employer_ratio = fields.Float(
        string='Company Contribution Ratio',
        related='resource_ordinary_id.employer_ratio',
        store=True,
        help="Company of Ordinary insurance contribution ratio"
    )

    # occupational insurance
    accident_employer_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_accident_id.employer_ratio',
        store=True,
        help="Company of Occupational Accident insurance contribution ratio"
    )

    # employment insurance
    employment_employer_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_employment_id.employer_ratio',
        store=True,
        help="Compnay of Employment insurance contribution ratio"
    )

    # health insurance
    health_employer_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_health_id.employer_ratio',
        store=True,
        help="Compnay of health insurance contribution ratio"
    )
    average_dependents_number = fields.Float(
        string='Average Dependents',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("health.average.dependents"),
        store=True,
        help=_('Number of Average Dependents'),
    )
