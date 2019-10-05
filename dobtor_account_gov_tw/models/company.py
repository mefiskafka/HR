# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = 'res.company'

    def check_chart_template_in_tw(self):
        taiwan_account_chart_id = self.env.ref(
            'l10n_tw_standard_ifrss.l10n_chart_taiwan_standard_business', raise_if_not_found=False
        ).id
        return bool(
            self.chart_template_id != taiwan_account_chart_id
        )

    def _default_misc_journal(self):
        return self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.env.user.company_id.id)], limit=1)

    def _perpare_account_journal(self, journal_ref_name, company_id):
        if journal_ref_name == 'dobtor_account_gov_tw.miscellaneous_hr_salary_journal':
            return {
                'name': _('Employee Salary'),
                'code': 'HRMISC',
                'type': 'general',
                'sequence': 92,
                'company_id': company_id,
            }
        return {}

    def _default_journal(self, journal_ref_name):
        journal = self.env.ref(journal_ref_name, raise_if_not_found=False)
        # if not journal:
        #     account_journal = self.env['account.journal']
        #     datas = self._perpare_account_journal(journal_ref_name, self.id)
        #     if datas:
        #         journal = account_journal.sudo().create(datas)
        if journal and journal.sudo().company_id == self.env.user.company_id and self.check_chart_template_in_tw():
            return journal
        return self._default_misc_journal()

    @api.depends('chart_template_id')
    def onchange_chart_template_id(self):
        for res in self:
            if res.check_chart_template_in_tw():
                res.hr_salary_journal = res._default_journal(
                    'dobtor_account_gov_tw.miscellaneous_hr_salary_journal'
                )
                res.withholding_tax_journal = res._default_journal(
                    'dobtor_account_gov_tw.miscellaneous_withholding_tax_journal'
                )
                res.withholding_bli_journal = res._default_journal(
                    'dobtor_account_gov_tw.miscellaneous_company_bli_journal'
                )
                res.withholding_nhi_journal = res._default_journal(
                    'dobtor_account_gov_tw.miscellaneous_company_nhi_journal'
                )
                res.bank_bli_journal = res._default_journal(
                    'dobtor_account_gov_tw.bank_blijournal'
                )
                res.back_nhi_journal = res._default_journal(
                    'dobtor_account_gov_tw.back_nhi_journal'
                )

    hr_salary_journal = fields.Many2one(
        string='Employee Salary Journal',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Employees Salary.",
        readonly=False,
    )

    withholding_tax_journal = fields.Many2one(
        string='Withholding Tax Journal',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding Tax.",
        readonly=False,
    )

    withholding_bli_journal = fields.Many2one(
        string='Withholding BLI Journal',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding BLI.",
        readonly=False,
    )

    withholding_nhi_journal = fields.Many2one(
        string='Withholding NHI Journal',
        comodel_name='account.journal',
        domain=[('type', '=', 'general')],
        help="Accounting journal used to Withholding NHI.",
        readonly=False,
    )

    bank_bli_journal = fields.Many2one(
        string='BLI Bank',
        comodel_name='account.journal',
        domain=[('type', '=', 'bank')],
        help="Accounting journal used to BLI (Bank).",
        readonly=False,
    )

    back_nhi_journal = fields.Many2one(
        string='NHI Bank',
        comodel_name='account.journal',
        domain=[('type', '=', 'bank')],
        help="Accounting journal used to NHI (Bank).",
        readonly=False,
    )

    back_ntbt_journal = fields.Many2one(
        string='NTBT Bank',
        comodel_name='account.journal',
        domain=[('type', '=', 'bank')],
        help="Accounting journal used to NTBT (Bank).",
        readonly=False,
    )

    # Public Administration
    bli_partner = fields.Many2one(
        string='BLI Contact',
        comodel_name='res.partner',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False
    )
    bli_product_id = fields.Many2one(
        string='BLI Product',
        comodel_name='product.product',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False
    )
    nhi_partner = fields.Many2one(
        string='NHI Contact',
        comodel_name='res.partner',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False
    )
    nhi_product_id = fields.Many2one(
        string='NHI Product',
        comodel_name='product.product',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False
    )
    tax_partner = fields.Many2one(
        string='TAX Contact',
        comodel_name='res.partner',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False
    )
    tax_product_id = fields.Many2one(
        string='TAX Product',
        comodel_name='product.product',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False
    )
    struct_id = fields.Many2one(
        comodel_name='hr.payroll.structure',
        string='Structure',
        readonly=False,
        domain=[('gov_ok', '=', True)],
    )
    
