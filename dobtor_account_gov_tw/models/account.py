# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    notes_id = fields.Many2one(
        comodel_name='notespayable.order',
        string='Add Notespayable Order',
        readonly=True, states={'draft': [('readonly', False)]},
    )




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

# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'

#     notes_line_id = fields.Many2one(
#         'notespayable.order.line',
#         'Notespayable Order Line',
#         ondelete='set null',
#         index=True,
#         readonly=True
#     )
#     notes_id = fields.Many2one(
#         'notespayable.order', 
#         related='notes_line_id.order_id',
#         string='Notes Order',
#         store=False,
#         readonly=True,
#         related_sudo=False,
#     )
