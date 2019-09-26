# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class Notespayable():
    _name = 'notespayable.order'
    _description = 'notes payable order'
    _order = 'data_from desc, id desc'

    READONLY_STATES = {
        'invoiced': [('readonly', True)],
        'post': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(
        string="Notes Payable Referance",
        required=True,
        index=True,
        copy=False,
        default='New'
    )
    total = fields.Float(
        compute="_compute_total",
        readonly=True,
        store=True
    )
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', _('New')),
            ('invoiced', _('Invoiced')),
            ('post', _('Posted')),
            ('cancel', _('Cancel'))
        ],
        readonly=True,
        index=True,
        copy=False,
        default='draft',
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='res_user_notespayable_rel',
        column1='notes_id',
        column2='user_id',
    )
    invoice = fields.Many2one(
        comodel_name="account.invoice",
        string="Generated invoice",
        readonly=True
    )
    lines = fields.One2many(
        comodel_name="notespayable.order.line",
        inverse_name="notes payable oreder line",
        string="Order lines",
        readonly=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.user.company_id.id
    )

    @api.depends('lines', 'lines.price')
    def _compute_total(self):
        for record in self:
            record.total = sum(x.price for x in record.lines)


class NotespayableLine():
    _name = 'notespayable.order.line'
    _description = 'Notes Payable Order Line'
    _order = 'order_id, sequence, id'

    name = fields.Text(
        string='Description',
        required=True
    )
    order_id = fields.Many2one(
        string='Order Reference',
        comodel_name='notespayable.order',
        index=True, 
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        # domain=[('purchase_ok', '=', True)],
        change_default=True,
        required=True
    )
    product_type = fields.Selection(
        related='product_id.type',
        readonly=True
    )
    price = fields.Monetary(
        string='Price',
        # store=True
    )
