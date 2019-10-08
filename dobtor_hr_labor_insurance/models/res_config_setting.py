# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Ordinary
    resource_ordinary_id = fields.Many2one(
        string='Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','ordinary')]",
        related='company_id.resource_ordinary_id',
        readonly=False
    )
    ordinary_premium = fields.Float(
        string='Insurance Premium',
        config_parameter='insurance.ordinary.premium',
        default=10,
        readonly=False,
        help=_("percentage of Ordinary Insurance Premium"),
    )
    
    #  Accident
    resource_accident_id = fields.Many2one(
        string='Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','accident')]",
        related='company_id.resource_accident_id',
        readonly=False,
    )
    accident_premium = fields.Selection(
        string='Insurance Premium',
        related='company_id.accident_premium',
        readonly=False,
    )

    # Ordinary Insurance
    resource_employment_id = fields.Many2one(
        string='Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','employment')]",
        related='company_id.resource_employment_id',
        readonly=False,
    )
    employment_premium = fields.Float(
        string='Insurance Premium',
        config_parameter='insurance.employment.premium',
        default=1,
        readonly=False,
        help=_("percentage of Employment Insurance Premium"),
    )

    # Health Insurance
    resource_health_id = fields.Many2one(
        string='Contribution Ratio',
        comodel_name='resource.health.contribution_ratio',
        related='company_id.resource_health_id',
        readonly=False,
    )
    health_premium = fields.Float(
        string='Insurance Premium',
        config_parameter='insurance.health.premium',
        default=4.69,
        readonly=False,
        help=_('percentage of Health Insurance Premium'),
    )
    average_dependents_number = fields.Float(
        string='Average Dependents',
        config_parameter='health.average.dependents',
        default=0.61,
        readonly=False,
        help=_('Number of Average Dependents'),
    )
    nhi_2nd_premium = fields.Float(
        string='2nd Generation NHI',
        config_parameter='insurance.nhi_2nd.premium',
        default=1.91,
        readonly=False,
        help=_('percentage of 2nd Generation NHI Insurance Premium'),
    )

    # Payroll Bracket Table
    payroll_bracket_id = fields.Many2one(
        string='Payroll Bracket Table',
        comodel_name='resource.payroll.bracket',
        related='company_id.payroll_bracket_id',
        readonly=False,
    )
    labor_limit = fields.Float(
        string='Labor Insured limit',
        config_parameter='labor.insured.limit',
        default=45800,
        readonly=False,
    )
    labor_pension_premium = fields.Float(
        string='Labor Pension Premium',
        config_parameter='insurance.pension.premium',
        default=6.0,
        readonly=False,
    )

    update_premium = fields.Char()

    @api.multi
    def open_update_premium(self):
        action = self.env.ref('dobtor_hr_labor_insurance.action_hr_update_insurance_premium').read()[0]
        return action