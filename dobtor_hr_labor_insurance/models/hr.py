# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Role(models.Model):
    _name = 'hr.role'
    name = fields.Char(string="Name")
    code = fields.Char(string="Abbrev Code")

class Employee(models.Model):    
    _inherit = 'hr.employee'

    role = fields.Many2one(
        string='Labor Role',
        comodel_name='hr.role',
        ondelete='set null',
    )
    # TODO : here is POC, if want to Productization later, sould be modify.
    rate_occupational_injury = fields.Selection(
        string='rate of occupational_injury',
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
        ]
        help=_("The Premium Rate of Occupational Injury and Disease Insurance")
    )
    
