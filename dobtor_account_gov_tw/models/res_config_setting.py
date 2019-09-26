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

    @api.depends('company_id')
    def _compute_has_chart_of_accounts_tw(self):
        taiwan_account_chart_id = self.env.ref(
            'l10n_tw_standard_ifrss.l10n_chart_taiwan_standard_business', raise_if_not_found=False
        ).id
        self.has_chart_of_accounts_tw = bool(
            self.company_id.chart_template_id.id != taiwan_account_chart_id
        )
    has_chart_of_accounts_tw = fields.Boolean(
        compute='_compute_has_chart_of_accounts_tw', string='Company has a chart of accounts')

    # taiwan_account_chart_id = fields.Many2one(
    #     compute='_compute_has_chart_of_accounts_tw'
    # )

    hr_salary_journal = fields.Many2one(
        string='Employee Salary Journal',
        comodel_name='account.journal',
        related='company_id.hr_salary_journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Employees Salary.",
        readonly=False,
    )

    withholding_tax_journal = fields.Many2one(
        string='Withholding Tax Jouranl',
        comodel_name='account.journal',
        related='company_id.withholding_tax_journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding Tax.",
        readonly=False,
    )

    withholding_bli_journal = fields.Many2one(
        string='Withholding BLI Jouranl',
        comodel_name='account.journal',
        related='company_id.withholding_bli_journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding BLI.",
        readonly=False,
    )

    withholding_nhi_journal = fields.Many2one(
        string='Withholding NHI Journal',
        comodel_name='account.journal',
        related='company_id.withholding_nhi_journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding NHI.",
        readonly=False,
    )

    bank_bli_journal = fields.Many2one(
        string='BLI Bank',
        comodel_name='account.journal',
        related='company_id.bank_bli_journal',
        domain=[('type', '=', 'bank')],
        help="Accounting journal used to BLI (Bank).",
        readonly=False,
    )

    back_nhi_journal = fields.Many2one(
        string='NHI Bank',
        comodel_name='account.journal',
        related='company_id.back_nhi_journal',
        domain=[('type', '=', 'bank')],
        help="Accounting journal used to NHI (Bank).",
        readonly=False,
    )