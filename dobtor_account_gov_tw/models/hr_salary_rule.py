# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    gov_ok = fields.Boolean(
        string='Using Government Tax',
    )    


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    gov_ok = fields.Boolean(
        string='Using Government Tax',
    )


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    def _default_gov_ok(self):
        return self.category_id.gov_ok

    gov_ok = fields.Boolean(
        string='Using Government Tax',
        default='_default_gov_ok',
    )
