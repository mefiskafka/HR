# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    notes_id = fields.Many2one(
        comodel_name='notespayable.order',
        string='Add Notespayable Order',
        readonly=True, states={'draft': [('readonly', False)]},
    )

    def _prepare_invoice_line_from_no_line(self, line):
        if line.product_id.gov_ok == True:
            qty = 1
        # taxes = line.taxes_id
        # invoice_line_tax_ids = line.order_id.fiscal_position_id.map_tax(
        #     taxes, line.product_id, line.order_id.partner_id)
        invoice_line = self.env['account.invoice.line']
        date = self.date or self.date_invoice
        data = {
            'notes_line_id': line.id,
            'name': line.order_id.name + ': ' + line.name,
            'origin': line.order_id.name,
            'uom_id': self.env['uom.uom'].search([], limit=1, order='id').id,
            'product_id': line.product_id.id,
            'account_id': invoice_line.with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
            'price_unit': line.order_id.currency_id._convert(
                line.price, self.currency_id, line.company_id, date or fields.Date.today(), round=False),
            'quantity': qty,
            'discount': 0.0,
            # 'account_analytic_id': line.account_analytic_id.id,
            # 'analytic_tag_ids': line.analytic_tag_ids.ids,
            # 'invoice_line_tax_ids': invoice_line_tax_ids.ids
        }
        account = invoice_line.get_invoice_line_account(
            'in_invoice', line.product_id, line.order_id.fiscal_position_id, self.env.user.company_id)
        if account:
            data['account_id'] = account.id
        return data

    @api.onchange('notes_id')
    def notespayable_order_change(self):
        print('here')
        if not self.notes_id:
            print('opps')
            return {}
        # if not self.partner_id:
        #     self.partner_id = self.purchase_id.partner_id.id

        # vendor_ref = self.notes_id.partner_ref
        vendor_ref = ''
        if vendor_ref and (not self.reference or (
                vendor_ref + ", " not in self.reference and not self.reference.endswith(vendor_ref))):
            self.reference = ", ".join(
                [self.reference, vendor_ref]) if self.reference else vendor_ref

        if not self.invoice_line_ids:
            #as there's no invoice line yet, we keep the currency of the PO
            self.currency_id = self.notes_id.currency_id

        new_lines = self.env['account.invoice.line']
        for line in self.notes_id.lines - self.invoice_line_ids.mapped('notes_line_id'):
            data = self._prepare_invoice_line_from_no_line(line)
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.payment_term_id = self.notes_id.payment_term_id
        # self.env.context = dict(
        #     self.env.context, from_purchase_order_change=True)
        self.notes_id = False
        return {}

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        print('Load NO partner')
        payment_term_id = False
        res = super()._onchange_partner_id()
        if payment_term_id:
            self.payment_term_id = payment_term_id
        if not self.env.context.get('default_journal_id') and self.partner_id and\
                self.type in ['in_invoice', 'in_refund'] and\
                self.currency_id != self.partner_id.property_purchase_currency_id and\
                self.partner_id.property_purchase_currency_id.id:
            journal_domain = [
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id),
                ('currency_id', '=', self.partner_id.property_purchase_currency_id.id),
            ]
            default_journal_id = self.env['account.journal'].search(
                journal_domain, limit=1)
            if default_journal_id:
                self.journal_id = default_journal_id
            if self.env.context.get('default_currency_id'):
                self.currency_id = self.env.context['default_currency_id']
            if self.partner_id.property_purchase_currency_id:
                self.currency_id = self.partner_id.property_purchase_currency_id
        return res


# class NotesPayableBillUnion(models.Model):
#     _name = 'notespayable.bill.union'
#     _auto = False
#     _description = 'Notes Payable & Bills Union'
#     _order = "date desc, name desc"

#     name = fields.Char(string='Reference', readonly=True)
#     reference = fields.Char(string='Source', readonly=True)
#     partner_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
#     date = fields.Date(string='Date', readonly=True)
#     amount = fields.Float(string='Amount', readonly=True)
#     currency_id = fields.Many2one(
#         'res.currency', string='Currency', readonly=True)
#     company_id = fields.Many2one('res.company', 'Company', readonly=True)
#     vendor_bill_id = fields.Many2one(
#         'account.invoice', string='Vendor Bill', readonly=True)
#     purchase_order_id = fields.Many2one(
#         'purchase.order', string='Purchase Order', readonly=True)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    notes_line_id = fields.Many2one(
        'notespayable.order.line',
        'Notespayable Order Line',
        ondelete='set null',
        index=True,
        readonly=True
    )
    notes_id = fields.Many2one(
        'notespayable.order',
        related='notes_line_id.order_id',
        string='Notes Order',
        store=False,
        readonly=True,
        related_sudo=False,
    )
