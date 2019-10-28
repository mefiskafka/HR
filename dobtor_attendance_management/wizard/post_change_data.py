# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PostChangeData(models.TransientModel):
    _name = "post.change.data"
    _description = "Change Attendance data"

    late_in = fields.Float(string="Late In")
    diff_time = fields.Float(string="Diff Time")
    overtime = fields.Float(string="Work Overtime")
    note = fields.Text(string="Note", required=True)
    line_id = fields.Many2one(comodel_name="attendance.sheet.line")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        line_id = self.env['hr.attendance.sheet.line'].browse(self._context['active_id'])
        res['late_in'] = line_id.late_in
        res['diff_time'] = line_id.diff_time
        res['overtime'] = line_id.overtime
        res['line_id'] = line_id.id
        return res

    @api.multi
    def action_change_data(self):
        self.ensure_one()
        [data] = self.read()
        line_id = self.env['hr.attendance.sheet.line'].browse(self._context['active_id'])
        res = {
            'late_in': data['late_in'],
            'diff_time': data['diff_time'],
            'overtime': data['overtime'],
            'note': data['note'],
        }
        line_id.write(res)
        return {'type': 'ir.actions.act_window_close'}
