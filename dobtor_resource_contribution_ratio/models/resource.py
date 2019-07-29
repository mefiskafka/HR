# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResourceLaborContributionRatio(models.Model):
    _name = "resource.labor.contribution_ratio"
    _inherit = "abstract.resource.contribution_ratio"
    _description = "Resource Labor Contribution Ratio"

    base_on = fields.Selection(
        string='Insurance base on',
        selection=[
            ('ordinary', 'Ordinary Insurance'),
            ('accident', 'Occupational Accident'),
            ('employment', 'Employment Insurance')
        ]
    ) 

class ResourceHealthContributionRatio(models.Model):
    _name = "resource.health.contribution_ratio"
    _inherit = "abstract.resource.contribution_ratio"
    _description = "Resource Health Contribution Ratio"

