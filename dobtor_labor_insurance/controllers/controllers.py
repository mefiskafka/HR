# -*- coding: utf-8 -*-
from odoo import http

# class DobtorLaborInsurance(http.Controller):
#     @http.route('/dobtor_labor_insurance/dobtor_labor_insurance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dobtor_labor_insurance/dobtor_labor_insurance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dobtor_labor_insurance.listing', {
#             'root': '/dobtor_labor_insurance/dobtor_labor_insurance',
#             'objects': http.request.env['dobtor_labor_insurance.dobtor_labor_insurance'].search([]),
#         })

#     @http.route('/dobtor_labor_insurance/dobtor_labor_insurance/objects/<model("dobtor_labor_insurance.dobtor_labor_insurance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dobtor_labor_insurance.object', {
#             'object': obj
#         })