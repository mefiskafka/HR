# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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

    # ordinary insurance
    resource_ordinary_id = fields.Many2one(
        string='Ordinary Insurance Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','ordinary')]",
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_ordinary_id.id,
    )
    ordinary_employee_ratio = fields.Float(
        string='Ordinary of Contribution Ratio',
        related='resource_ordinary_id.employee_ratio',
        store=True,
    )
    ordinary_premium = fields.Float(
        string='Ordinary Insurance Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.ordinary.premium"),
        store=True,
    )

    # occupational insurance
    resource_accident_id = fields.Many2one(
        string='Occupational Accident Insurance Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','accident')]",
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_accident_id.id,
    )
    accident_employee_ratio = fields.Float(
        string='Occupational Accident of Contribution Ratio',
        related='resource_accident_id.employee_ratio',
        store=True,
    )
    accident_premium = fields.Selection(
        string='Occuptional Accident Insurance Premium',
        related='company_id.accident_premium',
        store=True,
    )
    # employment insurance
    resource_employment_id = fields.Many2one(
        string='Employment Insurance Contribution Ratio',
        comodel_name='resource.labor.contribution_ratio',
        domian="[('base_on','=','employment')]",
        ondelete='set null',
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_employment_id.id,
    )
    employment_employee_ratio = fields.Float(
        string='Employment of Contribution Ratio',
        related='resource_employment_id.employee_ratio',
        store=True,
    )
    employment_premium = fields.Float(
        string='Employment Insurance Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.employment.premium"),
        store=True,
    )

    # health insurance
    resource_health_id = fields.Many2one(
        string='Health Insurance Contribution Ratio',
        comodel_name='resource.health.contribution_ratio',
        ondelete='set null',
        default=lambda self: self.env['res.company']._company_default_get(
        ).resource_health_id.id,
    )
    health_employee_ratio = fields.Float(
        string='Health of Contribution Ratio',
        related='resource_health_id.employee_ratio',
        store=True,
    )
    health_premium = fields.Float(
        string='Health Insurance Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.health.premium"),
        store=True,
    )
    dependents_number =  fields.Integer(
        string='Number of dependents',
        default=0
    )
    
    @api.depends('wage', 'payroll_bracket_id')
    def _compute_insure_wage(self):
        for record in self:
            insure_wage = record.payroll_bracket_id.table_ids.filtered(
                lambda item: item.rank >= record.wage)[0]
            record.insure_wage = insure_wage.rank
