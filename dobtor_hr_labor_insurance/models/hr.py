# -*- coding: utf-8 -*-

from odoo import models, fields, api, _




class Employee(models.Model):    
    _inherit = 'hr.employee'




    # role = fields.Many2one(
    #     string='Labor Role',
    #     comodel_name='hr.role',
    #     ondelete='set null',
    # )
    # TODO : here is POC, if want to Productization later, sould be modify.
    
# class Role(models.Model):
#     _name = 'hr.role'
#     name = fields.Char(string="Name")
#     code = fields.Char(string="Abbrev Code")
