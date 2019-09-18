# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_misc_journal(self):
        return self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.env.user.company_id.id)], limit=1)

    def _default_journal(self, journal_ref_name):
        journal = self.env.ref(journal_ref_name, raise_if_not_found=False)
        if journal and journal.sudo().company_id == self.env.user.company_id:
            return journal
        return self._default_misc_journal()

    hr_salary_journal = fields.Many2one(
        string='Employee Salary Journal',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Employees Salary.",
        default=lambda self: self._default_journal(
            'dobtor_hr_labor_insurance_account.miscellaneous_hr_salary_journal'
        )
    )

    withholding_tax_journal = fields.Many2one(
        string='Withholding Tax Jouranl',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding Tax.",
        default=lambda self: self._default_journal(
            'dobtor_hr_labor_insurance_account.miscellaneous_withholding_tax_journal'
        )
    )

    withholding_bli_journal = fields.Many2one(
        string='Withholding BLI Jouranl',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding BLI.",
        default=lambda self: self._default_journal(
            'dobtor_hr_labor_insurance_account.miscellaneous_company_bli_journal'
        )
    )

    withholding_nhi_journal = fields.Many2one(
        string='Withholding NHI Jouranl',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding NHI.",
        default=lambda self: self._default_journal(
            'dobtor_hr_labor_insurance_account.miscellaneous_company_nhi_journal'
        )
    )

    bank_bli_journal = fields.Many2one(
        string='BLI Bank',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to BLI (Bank).",
        default=lambda self: self._default_journal(
            'dobtor_hr_labor_insurance_account.bank_blijournal'
        )
    )

    back_nhi_journal = fields.Many2one(
        string='NHI Bank',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to NHI (Bank).",
        default=lambda self: self._default_journal(
            'dobtor_hr_labor_insurance_account.back_nhi_journal'
        )
    )
