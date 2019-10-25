# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _


class HrResource(models.Model):
    _inherit = 'resource.calendar'

    two_days_off = fields.Boolean(
        string='Two days off',
        default=False,
        help='one mandatory day off and one flexible rest day',
    )
    mandatory_day = fields.Selection(selection=[
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string='mandatory day off', default='6')

    rest_day = fields.Selection(selection=[
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], string='flexible rest day', default='5')

    # TODO: Flexible working hours
    # Two-week (80hr) two mandatory day off and two flexible rest day
    # Tax-exempt income
    # Overtime pay of up to 46 hours per month is exempt from tax
