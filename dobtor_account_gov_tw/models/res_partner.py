# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gov_ok = fields.Boolean(
        string='Government tax',
        default=False
    )
    # gov_product_id = fields.Many2one(
    #     string='Gov Product',
    #     comodel_name='product.product',
    #     ondelete='set null',
    #     domain=[('gov_ok', '=', True)]
    # )

    # def _check_chart_of_account_is_tw(self, company_id):
    #     taiwan_account_chart_id = self.env.ref(
    #         'l10n_tw_standard_ifrss.l10n_chart_taiwan_standard_business', raise_if_not_found=False
    #     ).id
    #     return company_id.chart_template_id.id != taiwan_account_chart_id

    # def _check_industry_is_res_partner_industry_O(self, industry_id):
    #     if industry_id:
    #         return industry_id == self.env.ref('base.res_partner_industry_O', raise_if_not_found=False).id
    #     return False

    # def _get_account_common(self, chart_of_account_name):
    #     return self.env.ref(chart_of_account_name).id

    # @api.model
    # def create(self, vals):
    #     """ inherit create """
    #     company_id = self._default_company() or vals.get('company_id', False)
    #     if company_id:
    #         if self._check_chart_of_account_is_tw(company_id) and self._check_industry_is_res_partner_industry_O(vals.get('industry_id', False)):
    #             vals['property_account_receivable_id'] = self._get_account_common(
    #                 'l10n_tw_standard_ifrss.account_120600'
    #             )
    #             vals['property_account_payable_id'] = self._get_account_common(
    #                 'l10n_tw_standard_ifrss.account_220900'
    #             )
    #             print(vals)
    #     return super().create(vals)
