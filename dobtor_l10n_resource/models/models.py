# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class dobtor_l10n_resource(models.Model):
#     _name = 'dobtor_l10n_resource.dobtor_l10n_resource'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100