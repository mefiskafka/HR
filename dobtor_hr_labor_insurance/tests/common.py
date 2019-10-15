# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.fields import Date
from odoo.tests.common import TransactionCase


class TestHrCommon(TransactionCase):

    def setUp(self):
        super().setUp()
        # employee 
        self.michael_emp = self.ref('dobtor_hr_labor_insurance.employee_michael')

        # salary structure 
        self.salart_structure = self.ref(
            'dobtor_hr_labor_insurance.structure_base_with_insurance')

        # create a contract for "Michael"
        self.michael_contract = self.env['hr.contract'].create({
            'date_end': Date.to_string((datetime.now() + timedelta(days=365))),
            'date_start': Date.today(),
            'name': 'Contract for Michael',
            'wage': 52000.0,
            'type_id': self.ref('hr_contract.hr_contract_type_emp'),
            'employee_id': self.michael_emp,
            'struct_id': self.salart_structure,
            'pension_premium': 3.5,
        })

        # create an employee Payslip for "Michael"
        self.michael_payslip = self.env['hr.payslip'].create({
            'name': 'Payslip of Michael 2',
            'employee_id': self.michael_emp,
            'contract_id': self.michael_contract.id,
            # 'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id
        })
