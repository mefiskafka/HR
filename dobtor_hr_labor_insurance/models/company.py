# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = 'res.company'

    # Ordinary Insurance
    resource_ordinary_id = fields.Many2one(
        string='Ordinary Insurance Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','ordinary')]",
        ondelete='set null',
    )

    # Occupational Accident Insurance 
    resource_accident_id = fields.Many2one(
        string='Occupational Accident Insurance Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','accident')]",
        ondelete='set null',
    )
    accident_premium = fields.Selection(
        string='Occupational Accident Insurance Premium',
        selection=[
            ('0.11', '0.11'),
            ('0.12', '0.12'),
            ('0.13', '0.13'),
            ('0.15', '0.15'),
            ('0.16', '0.16'),
            ('0.17', '0.17'),
            ('0.18', '0.18'),
            ('0.19', '0.19'),
            ('0.20', '0.20'),
            ('0.21', '0.21'),
            ('0.22', '0.22'),
            ('0.23', '0.23'),
            ('0.24', '0.24'),
            ('0.26', '0.26'),
            ('0.27', '0.27'),
            ('0.28', '0.28'),
            ('0.37', '0.37'),
            ('0.39', '0.39'),
            ('0.40', '0.40'),
            ('0.41', '0.41'),
            ('0.47', '0.47'),
            ('0.48', '0.48'),
            ('0.53', '0.53'),
            ('0.61', '0.61'),
            ('0.92', '0.92'),
            ('0.96', '0.96'),
        ],
        default='0.11',
        help=_('percentage of Occupational Accident Insurance Premium'),
    )

    # Ordinary Insurance
    resource_employment_id = fields.Many2one(
        string='Employment Insurance Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','employment')]",
        ondelete='set null',
    )

    # Health Insurance 
    resource_health_id = fields.Many2one(
        string='Health Insurance Contribution Ratio',
        comodel_name='resource.health.contribution_ratio',
        ondelete='set null',
    )
    
    
