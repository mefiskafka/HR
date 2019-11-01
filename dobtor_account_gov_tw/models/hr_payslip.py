# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    # ordinary insurance
    ordinary_employer_ratio = fields.Float(
        string='Company Contribution Ratio',
        related='resource_ordinary_id.employer_ratio',
        store=True,
        help="Company of Ordinary insurance contribution ratio"
    )

    # occupational insurance
    accident_employer_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_accident_id.employer_ratio',
        store=True,
        help="Company of Occupational Accident insurance contribution ratio"
    )

    # employment insurance
    employment_employer_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_employment_id.employer_ratio',
        store=True,
        help="Compnay of Employment insurance contribution ratio"
    )

    # health insurance
    health_employer_ratio = fields.Float(
        string='Contribution Ratio',
        related='resource_health_id.employer_ratio',
        store=True,
        help="Compnay of health insurance contribution ratio"
    )
    average_dependents_number = fields.Float(
        string='Average Dependents',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("health.average.dependents"),
        store=True,
        help=_('Number of Average Dependents'),
    )

    # withholding Tax
    withholding_tax_limit = fields.Float(
        string='withholding tax limit',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("withholding.tax.limit"),
        store=True,
    )
    tax_premium = fields.Float(
        string='tax Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("withholding.tax.premium"),
        store=True,
    )

    # pension
    labor_pension_premium = fields.Float(
        string='Labor Pension Premium',
        default=lambda self: self.env["ir.config_parameter"].sudo(
        ).get_param("insurance.pension.premium"),
        store=True,
    )
    journal_id = fields.Many2one(
        'account.journal', 'Salary Journal',
        default=lambda self: self.env.user.company_id.hr_salary_journal.id
    )

    @api.multi
    def action_update_premium(self):
        super().action_update_premium()
        for res in self:
            res.average_dependents_number = self.env["ir.config_parameter"].sudo(
            ).get_param("health.average.dependents")
            res.withholding_tax_limit = self.env["ir.config_parameter"].sudo(
            ).get_param("withholding.tax.limit")
            res.tax_premium = self.env["ir.config_parameter"].sudo(
            ).get_param("withholding.tax.premium")

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        result = super()._get_payslip_lines(contract_ids, payslip_id)
        for line in result:
            rule = self.env['hr.salary.rule'].browse(
                line.get('salary_rule_id'))
            if rule.gov_ok and rule.base_on:
                line['base_on'] = rule.base_on
                if rule.superposition:
                    line['superposition'] = rule.superposition
        return result

