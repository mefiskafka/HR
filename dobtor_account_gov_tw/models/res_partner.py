# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gov_ok = fields.Boolean(
        string='Government tax',
        default=False
    )

