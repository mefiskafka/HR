# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    amount_select = fields.Selection(
        selection_add=[('formula', 'Premium formula')]
    )
    type_id = fields.Many2one(
        string='Formula Type',
        comodel_name='hr.salary.rule.formula.type',
        ondelete='set null',
    )
    formula_select = fields.Many2one(
        string='Formula Base On',
        comodel_name='hr.salary.rule.formula.select',
        ondelete='set null',
    )

    @api.onchange('amount_select')
    def onchange_amount_select(self):
        return {'domain': {'type_id': [('code', '=', 'salary')]}}

    @api.onchange('type_id')
    def onchange_type_id_clear_formula_select(self):
        self.formula_select = False

    @api.multi
    def _compute_rule(self, localdict):
        self.ensure_one()
        # Premium formula
        if self.amount_select == 'formula':
            try:
                __python_code = '_{}_{}_{}'.format(
                    self.amount_select,
                    self.type_id.code,
                    self.formula_select.code
                )
                if hasattr(self, __python_code):
                    safe_eval(getattr(self, __python_code)(),
                              localdict, mode='exec', nocopy=True)
                    return float(localdict['result']), 'result_qty' in localdict and localdict['result_qty'] or 1.0, 'result_rate' in localdict and localdict['result_rate'] or 100.0
            except:
                raise UserError(_('Wrong premium formula defined for salary rule %s (%s).') % (
                    self.name, self.code))
        else:
            return super()._compute_rule(localdict)

    def _formula_salary_ordinary(self):
        return """result = -round(contract.insure_wage * (contract.ordinary_premium/100.00) * (contract.ordinary_employee_ratio/100.00))"""

    def _formula_salary_accident(self):
        return """result = -round( contract.insure_wage * (float(contract.accident_premium)/100.00) * (contract.accident_employee_ratio/100.00) )"""

    def _formula_salary_employment(self):
        return """result = -round( contract.insure_wage * (contract.employment_premium/100.00) * (contract.employment_employee_ratio/100.00) )"""

    def _formula_salary_self(self):
        return """result = -round(contract.health_insure_wage * (contract.pension_premium/100.00) )"""
    
    def _formula_salary_health(self):
        return """result = -round( contract.health_insure_wage * (contract.health_premium/100.00) * (contract.health_employee_ratio/100.00) * (1 + contract.dependents_number))"""

    def _formula_salary_nhi2nd(self):
        return """result = -round( payslip.nhi_2nd_amount * (contract.nhi_2nd_premium/100.00) )"""


class HrSalaryRuleFormulaType(models.Model):
    _name = 'hr.salary.rule.formula.type'
    _order = 'sequence, id'
    _description = 'Salary Rule Formula Type'

    sequence = fields.Integer(index=True, default=5)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)


class HrSalaryRuleFormulaType(models.Model):
    _name = 'hr.salary.rule.formula.select'
    _order = 'sequence, id'
    _description = 'Salary Rule Formula Select'

    sequence = fields.Integer(index=True, default=5)
    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    type_id = fields.Many2one(
        comodel_name='hr.salary.rule.formula.type',
        ondelete='set null',
    )
