# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    gov_ok = fields.Boolean(
        string='Government Tax',
        default=False
    )


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    gov_ok = fields.Boolean(
        string='Government Tax',
        default=False
    )


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    def _default_gov_ok(self):
        return self.category_id.gov_ok

    gov_ok = fields.Boolean(
        string='Government Tax',
        default=_default_gov_ok,
    )
    base_on = fields.Selection(
        string='Base on',
        selection=[
            ('bli', 'Bureau of Labor Insurance'),
            ('nhi', 'National Health Insurance'),
            ('tax', 'National Taxation Burean'),
            ('other', 'Other')
        ],
    )
    superposition = fields.Boolean(
        string='superposition principle',
        default=False,
        help="help to NHI2nd (Company)"
    )

    @api.depends('amount_select')
    @api.onchange('amount_select')
    def onchange_amount_select(self):
        self.onchange_type_id()
        return super().onchange_amount_select()

    @api.depends('gov_ok', 'base_on', 'type_id')
    @api.onchange('gov_ok', 'base_on', 'type_id')
    def onchange_type_id(self):
        self.formula_select = False
        if self.gov_ok:
            if self.base_on in ('bli', 'nhi'):
                return {'domain': {'type_id': [('code', 'in', ('company', 'withholding'))]}}
            elif self.base_on == 'tax':
                return {'domain': {'type_id': [('code', '=', 'company')]}}
            else:
                return {'domain': {'type_id': [('code', '=', 'other')]}}
        return {'domain': {'type_id': [('code', '=', 'salary')]}}

    @api.depends('formula_select')
    @api.onchange('formula_select')
    def onchange_formula_select(self):
        self.superposition = bool(self.formula_select.id == self.env.ref(
            'dobtor_account_gov_tw.hr_rule_formula_select_cnhi2nd').id)

    # Company
    def _formula_company_cordinary(self):
        return """result = -round( contract.insure_wage * (contract.ordinary_premium/100.00) * (contract.ordinary_employer_ratio/100.00) )"""

    def _formula_company_caccident(self):
        return """result = -round( contract.insure_wage * (float(contract.accident_premium)/100.00) * (contract.accident_employer_ratio/100.00) )"""

    def _formula_company_cemployment(self):
        return """result = -round( contract.insure_wage * (contract.employment_premium/100.00) * (contract.employment_employer_ratio/100.00) )"""

    def _formula_company_cpension(self):
        return """result = -round( contract.health_insure_wage * (contract.labor_pension_premium/100.00) )"""

    def _formula_company_chealth(self):
        return """result = -round( contract.health_insure_wage * (contract.health_premium/100.00) * (contract.health_employer_ratio/100.00) * (1 + contract.average_dependents_number) )"""

    def _formula_company_cnhi2nd(self):
        return """result = -round( contract.wage + payslip.line_amount - contract.health_insure_wage )"""

    # withholding
    def _formula_withholding_wordinary(self):
        return self._formula_salary_ordinary()

    def _formula_withholding_waccident(self):
        return self._formula_salary_accident()

    def _formula_withholding_wemployment(self):
        return self._formula_salary_employment()

    def _formula_withholding_wself(self):
        return self._formula_salary_self()

    def _formula_withholding_whealth(self):
        return self._formula_salary_health()

    def _formula_withholding_wnhi2nd(self):
        return self._formula_salary_nhi2nd()

    def _formula_withholding_wtax(self):
        return """result = -round( contract.wage * (contract.tax_premium/100.00) ) if round( contract.wage * (contract.tax_premium/100.00) ) > round( contract.withholding_tax_limit * (contract.tax_premium/100.00) ) else 0.00"""
