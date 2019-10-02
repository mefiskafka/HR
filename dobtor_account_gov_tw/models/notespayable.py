# -*- coding: utf-8 -*-
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


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
    date_from = fields.Date(
        string="From",
        default=lambda self: fields.Date.to_string(
            date.today().replace(day=1)),
        states={'draft': [('readonly', False)]}
    )
    date_to = fields.Date(
        string="To",
        default=lambda self: fields.Date.to_string(
            (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
        states={'draft': [('readonly', False)]}
    )
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
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='set null',
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
    #  invoice
    invoice_id = fields.Many2one(
        comodel_name="account.invoice",
        string="Bills",
        copy=False,
        readonly=True
    )
    # invoice_exist = fields.Integer(
    #     compute="_compute_invoice",
    #     string='Bill Count',
    #     copy=False,
    #     default=0,
    #     store=True
    # )
    # invoice_ids = fields.Many2many(
    #     'account.invoice',
    #     compute="_compute_invoice",
    #     string='Bills',
    #     copy=False,
    #     store=True
    # )
    # invoice_status = fields.Selection(
    #     selection=[
    #         ('no', 'Nothing to Bill'),
    #         ('to invoice', 'Waiting Bills'),
    #         ('invoiced', 'No Bill to Receive'),
    #     ],
    #     string='Billing Status',
    #     compute='_get_invoiced',
    #     store=True,
    #     readonly=True,
    #     copy=False,
    #     default='no'
    # )
    # end invoice
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
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    notes = fields.Text('Terms and Conditions')

    # HR Setting
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='hr_employee_notespayable_rel',
        column1='notes_id',
        column2='employee_id',
        domain=[('contract_ids', '!=', False)]
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
                record.product_id = record.company_id.nhi_product_id and record.company_id.nhi_product_id.id
            elif record.company_id.bli_partner.id == record.partner_id.id:
                record.base_on = 'bli'
                record.product_id = record.company_id.bli_product_id and record.company_id.bli_product_id.id
            elif record.company_id.tax_partner.id == record.partner_id.id:
                record.base_on = 'tax'
                record.product_id = record.company_id.tax_product_id and record.company_id.tax_product_id.id
            else:
                record.base_on = 'other'

    # @api.depends('lines.invoice_lines.invoice_id')
    # def _compute_invoice(self):
    #     for order in self:
    #         invoices = self.env['account.invoice']
    #         for line in order.lines:
    #             invoices |= line.invoice_lines.mapped('invoice_id')
    #         order.invoice_ids = invoices
    #         order.invoice_count = len(invoices)

    @api.multi
    def action_compute_sheet(self):
        payroll = self.env['hr.payslip']
        contract = self.env['hr.contract']
        lines = []
        for order in self:
            order.lines.unlink()
            if not order.employee_ids:
                order.employee_ids = self.env['hr.employee'].sudo().search(
                    [('contract_ids', '!=', False)])

            for employee in order.employee_ids:
                payslip = employee.slip_ids.filtered(
                    lambda r: order.date_from <= r.date_from and r.date_to <= order.date_to)
                if len(payslip):
                    payslip = payslip[0].copy()
                    payslip.struct_id = order.struct_id
                    contract_ids = payslip.contract_id.ids or \
                        payroll.sudo().get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
                    lines += [(0, 0, {
                        'product_id': order.product_id and order.product_id.id,
                        'name': '{} - {}'.format(line.get('name'), employee.name),
                        'order_id': order.id,
                        'price': line.get('amount')
                    }) for line in payroll.sudo()._get_payslip_lines(
                        contract_ids, payslip.id) if line.get('base_on') == order.base_on and line.get('amount') != 0]
                    (query, query_args) = self._delete_temp_payslip(payslip)
                    self.env.cr.execute(query, query_args)
            if len(lines):
                order.write({'lines': lines})
            
        return True

    def _delete_temp_payslip(self, payslip):
        return ("""Delete FROM hr_payslip WHERE id = %(payslip_id)s;""", {'payslip_id': payslip.id})

    @api.multi
    def action_view_invoice(self):
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_notes_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.invoice_id) == 1 and not create_bill:
            result['domain'] = "[('id', '=', " + \
                str(self.invoice_ids.id) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_origin'] = self.name
        return result

    @api.multi
    def action_cancel(self):
        for order in self:
            inv = order.invoice_id
            if inv and inv.state not in ('cancel', 'draft'):
                raise UserError(
                    _("Unable to cancel this notespayable order. You must first cancel the related bills."))
        self.write({'state': 'cancel'})


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
        ondelete='set null',
        # change_default=True,
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
    invoice_lines = fields.One2many(
        'account.invoice.line',
        'notes_line_id',
        string="Bill Lines",
        readonly=True,
        copy=False
    )

    # @api.model
    # def create(self, vals):
    #     res = super().create(vals)
    #     print(vals)
    #     return res
