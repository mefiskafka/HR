# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class Notespayable(models.Model):
    _name = 'notespayable.order'
    _description = 'notes payable order'
    _order = 'date_from desc, id desc'

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
    amount_total = fields.Float(
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
    partner_id = fields.Many2one(
        'res.partner',
        string='Public Administration',
        required=True,
        states=READONLY_STATES,
        change_default=True,
        track_visibility='always'
    )
    base_on = fields.Selection(
        string='Base on',
        selection=[
            ('bli', 'Bureau of Labor Insurance'),
            ('nhi', 'National Health Insurance'),
            ('tax', 'National Taxation Burean'),
            ('other', 'Other')
        ],
        compute='_compute_base_on',
    )
    # user_ids = fields.Many2many(
    #     comodel_name='res.users',
    #     relation='res_user_notespayable_rel',
    #     column1='notes_id',
    #     column2='user_id',
    # )
    invoice = fields.Many2one(
        comodel_name="account.invoice",
        string="Generated invoice",
        readonly=True
    )
    lines = fields.One2many(
        comodel_name="notespayable.order.line",
        inverse_name="order_id",
        string="Order lines",
        states=READONLY_STATES,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True,
        states=READONLY_STATES,
        default=lambda self: self.env.user.company_id.currency_id.id
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.user.company_id.id
    )
    notes = fields.Text('Terms and Conditions')

    # HR Setting
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='hr_employee_notespayable_rel',
        column1='notes_id',
        column2='employee_id',
        domain=[('contract_id', '!=', False)]
    )
    struct_id = fields.Many2one(
        comodel_name='hr.payroll.structure',
        string='Structure',
        readonly=True,
        domain=[('gov_ok', '=', True)],
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'notespayable.order') or '/'
        return super().create(vals)

    @api.depends('lines', 'lines.price')
    def _compute_total(self):
        for record in self:
            record.amount_total = sum(x.price for x in record.lines)

    @api.multi
    @api.depends('company_id', 'partner_id')
    def _compute_base_on(self):
        for record in self:
            if record.company_id.nhi_partner.id == record.partner_id.id:
                record.base_on = 'nhi'
            elif record.company_id.bli_partner.id == record.partner_id.id:
                record.base_on = 'bli'
            elif record.company_id.tax_partner.id == record.partner_id.id:
                record.base_on = 'tax'
            else:
                record.base_on = 'other'

    @api.multi
    def action_compute_sheet(self):
        return False

    @api.multi
    def action_cancel(self):
        return False

    @api.multi
    def action_view_invoice(self):
        return False

class NotespayableLine(models.Model):
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
        domain=[('gov_ok', '=', True)],
        change_default=True,
        # required=True
    )
    product_type = fields.Selection(
        related='product_id.type',
        readonly=True
    )
    price = fields.Monetary(
        string='Price',
        # store=True
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )
    state = fields.Selection(
        related='order_id.state',
        store=True,
        readonly=False
    )
