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
        config_parameter='insurance.health.average_dependents', 
        default=0.61,
        readonly=False,
        help=_('Number of Average Dependents'),
    )

