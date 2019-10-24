# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _


class HrLeave(models.Model):
    _inherit = 'hr.leave.type'

    code = fields.Char(help="The code that can be used in the salary rules")
