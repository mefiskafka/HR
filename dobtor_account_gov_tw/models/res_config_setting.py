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
    
    back_ntbt_journal = fields.Many2one(
        string='NTBT Bank',
        comodel_name='account.journal',
        related='company_id.back_ntbt_journal',
        domain=[('type', '=', 'bank')],
        help="Accounting journal used to NTBT (Bank).",
        readonly=False,
    )

    # Public Administration
    bli_partner = fields.Many2one(
        string='BLI Contact',
        comodel_name='res.partner',
        related='company_id.bli_partner',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False,
    )
    bli_product_id = fields.Many2one(
        string='BLI Product',
        comodel_name='product.product',
        related='company_id.bli_product_id',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False,
    )
    nhi_partner = fields.Many2one(
        string='NHI Contact',
        comodel_name='res.partner',
        related='company_id.nhi_partner',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False,
    )
    nhi_product_id = fields.Many2one(
        string='NHI Product',
        comodel_name='product.product',
        related='company_id.nhi_product_id',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False,
    )
    tax_partner = fields.Many2one(
        string='TAX Contact',
        comodel_name='res.partner',
        related='company_id.tax_partner',
        domain=[
            ('gov_ok', '=', True),
        ],
        readonly=False,
    )
    tax_product_id = fields.Many2one(
        string='TAX Product',
        comodel_name='product.product',
        related='company_id.tax_product_id',
        domain=[
            ('gov_ok', '=', True)
        ],
        readonly=False,
    )

    struct_id = fields.Many2one(
        comodel_name='hr.payroll.structure',
        string='Structure',
        related='company_id.struct_id',
        readonly=False,
        domain=[('gov_ok', '=', True)],
    )

    # withholding Tax
    withholding_tax_limit = fields.Float(
        string='Withholding Tax Limit',
        config_parameter='withholding.tax.limit',
        default=40000,
        readonly=False,
    )
    tax_premium = fields.Float(
        string='Tax Premium',
        config_parameter='withholding.tax.premium',
        default=5,
        readonly=False,
    )
