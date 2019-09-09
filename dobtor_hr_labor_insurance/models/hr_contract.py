# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _inherit = 'hr.contract'

    # insure wage
    payroll_bracket_id = fields.Many2one(
        string='Payroll Bracket Table',
        comodel_name='resource.payroll.bracket',
        default=lambda self: self.env['res.company']._company_default_get(
        ).payroll_bracket_id.id,
    )
    insure_wage = fields.Float(
        string='Insure Wage',
        compute='_compute_insure_wage',
        store=True,
    )
    health_insure_wage = fields.Float(
        string='Health Insure Wage',
        compute='_compute_insure_wage',
        store=True,
    )

    # ordinary insurance
    resource_ordinary_id = fields.Many2one(
        string='Policy',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','ordinary')]",
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_ordinary_id.id,
    )
    ordinary_employee_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_ordinary_id.employee_ratio',
        store=True,
        help="Employee of Ordinary insurance contribution ratio"
    )
    ordinary_premium = fields.Float(
        string='Insurance Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.ordinary.premium"),
        store=True,
    )

    # occupational insurance
    resource_accident_id = fields.Many2one(
        string='Policy',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','accident')]",
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_accident_id.id,
    )
    accident_employee_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_accident_id.employee_ratio',
        store=True,
        help="Employee of Occupational Accident insurance contribution ratio"
    )
    accident_premium = fields.Selection(
        string='Insurance Premium',
        related='company_id.accident_premium',
        store=True,
    )
    # employment insurance
    resource_employment_id = fields.Many2one(
        string='Policy',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','employment')]",
        ondelete='set null',
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_employment_id.id,
    )
    employment_employee_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_employment_id.employee_ratio',
        store=True,
        help="Employee of Employment insurance contribution ratio"
    )
    employment_premium = fields.Float(
        string='Insurance Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.employment.premium"),
        store=True,
    )

    # Self-Labor pension
    pension_premium = fields.Float(
        string='Self-Labor pension',
        default=0,
        digits=(2, 1)
    )

    # health insurance
    resource_health_id = fields.Many2one(
        string='Policy',
        comodel_name='resource.health.contribution_ratio',
        ondelete='set null',
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_health_id.id,
    )
    health_employee_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_health_id.employee_ratio',
        store=True,
        help="Employee of health insurance contribution ratio"
    )
    health_premium = fields.Float(
        string='Insurance Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.health.premium"),
        store=True,
    )
    dependents_number = fields.Integer(
        string='Number of dependents',
        default=0
    )
    nhi_2nd_premium = fields.Float(
        string='2nd Generation NHI',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.nhi_2nd.premium"),
        store=True,
    )

    @api.depends('wage', 'payroll_bracket_id')
    def _compute_insure_wage(self):
        for record in self:
            if record.wage > float(self.env["ir.config_parameter"].sudo().get_param("labor.insured.limit")):
                insure_wage = float(self.env["ir.config_parameter"].sudo(
                ).get_param("labor.insured.limit"))
            else:
                insure_wage = record.payroll_bracket_id.table_ids.filtered(
                    lambda item: item.rank >= record.wage)[0].rank
            

            if record.wage > record.payroll_bracket_id.table_ids[-1].rank:
                health_insure_wage = record.payroll_bracket_id.table_ids[-1].rank
            else:
                health_insure_wage = record.payroll_bracket_id.table_ids.filtered(
                    lambda item: item.rank >= record.wage)[0].rank

            record.insure_wage = insure_wage
            record.health_insure_wage = health_insure_wage

    @api.constrains('pension_premium')
    def _check_pension_premium(self):
        """  validation at Self-Labor pension. """
        for record in self:
            if record.pension_premium < 0.0:
                raise ValidationError(
                    _("Please enter positive Value for 'Self-Labor pension'"))
            if record.pension_premium > 6.0:
                raise ValidationError(
                    _("It has to be no greater than 6.0"))

    @api.constrains('dependents_number')
    def _check_dependents_number(self):
        """  validation at dependents_number. """
        for record in self:
            if record.dependents_number < 0.0:
                raise ValidationError(
                    _("Please enter positive Value for 'Number of dependents'"))
