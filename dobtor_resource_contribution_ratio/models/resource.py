# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


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


class ResourcePayrollBracket(models.Model):
    _name = "resource.payroll.bracket"
    _description = "Resource Payroll Bracket"

    name = fields.Char()
    table_ids = fields.One2many(
        string='Bracket Table',
        comodel_name='resource.payroll.bracket.table',
        inverse_name='barcket_id',
    )

    def action_payroll_bracket_table(self):
        action = self.env.ref(
            'dobtor_resource_contribution_ratio.action_payroll_bracket_table').read()[0]
        action['context'] = {
            'default_barcket_id': self.id,
        }
        return action


class ResourcePayrollBracketTable(models.Model):
    _name = "resource.payroll.bracket.table"
    _description = "Resource Payroll Contribution Ratio"

    name = fields.Char(
        string='Level',
    )
    barcket_id = fields.Many2one(
        string='Bracket',
        comodel_name='resource.payroll.bracket',
        ondelete='cascade',
    )
    rank = fields.Float(
        string='Rank',
    )

    @api.constrains('rank')
    def _check_rank_validation(self):
        """  validation at rank. """
        for record in self:
            if record.rank < 0.0:
                raise ValidationError(_("Please enter Some Value for bracket table rank"))
