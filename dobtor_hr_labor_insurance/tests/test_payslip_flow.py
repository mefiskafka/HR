# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.dobtor_hr_labor_insurance.tests.common import TestHrCommon


@tagged('-at_install', 'post_install')
class Payship_With_Insurance(TestHrCommon):

    def test_00_compute_insure_wage(self):
        insure_wage = self.michael_contract.insure_wage
        self.assertEqual(insure_wage, 45800,
                         msg='insure_wage should be 45,800!')

        health_insure_wage = self.michael_contract.health_insure_wage
        self.assertEqual(health_insure_wage, 53000,
                         msg='health_insure_wage should be 53,000!')

    def test_01_payslip_workflow(self):
        """ Testing payslip flow and report printing """

        payslip_input = self.env['hr.payslip.input'].search(
            [('payslip_id', '=', self.michael_payslip.id)]
        )
        payslip_input.write({'amount': 5.0})

        # I verify the payslip is in draft state
        self.assertEqual(self.michael_payslip.state, 'draft',
                         msg='State should be draft!')

        context = {
            "lang": "en_US", "tz": False, "active_model": "ir.ui.menu",
            "department_id": False, "section_id": False,
            "active_ids": [self.ref("hr_payroll.menu_department_tree")],
            "active_id": self.ref("hr_payroll.menu_department_tree")
        }
        # click on 'Compute Sheet' button on payslip
        self.michael_payslip.with_context(context).compute_sheet()
        line = self.michael_payslip.line_ids
        self.assertTrue(len(line) > 0, msg='No line in payslip')
        # Labor Insurance
        # Ordinary : test _formula_salary_ordinary
        ordinary = line.filtered(lambda r: r.code == 'ORDINARY')
        self.assertEqual(ordinary.total, -916,
                         msg='In this case ordinary insurance fee should be 916!')
        # Occupational Accident : test _formula_salary_accident
        accident = line.filtered(lambda r: r.code == 'ACCIDENT')
        self.assertEqual(accident.total, 0,
                         msg='In this case occupational accident insurance fee should be 0!')
        # Employment : test _formula_salary_employment
        employment = line.filtered(lambda r: r.code == 'EMPLOYMENT')
        self.assertEqual(employment.total, -92,
                         msg='In this case employment fee should be 92!')
        # Person payable of Labor Insurance
        person_labor_total = ordinary.total + accident.total + employment.total
        self.assertEqual(person_labor_total, -1008,
                         msg='In this case person payable of Labor insurance fee should be 1008!')
        # Self-Labor Pension : test _formula_salary_self
        self_pension = line.filtered(lambda r: r.code == 'SELF')
        self.assertEqual(self_pension.total, -1855,
                         msg='In this case self-labor pension insurance fee should be 1855!')
        # Health : test _formula_salary_health
        health = line.filtered(lambda r: r.code == 'HEALTH')
        self.assertEqual(health.total, -746,
                         msg='In this case health insurance fee should be 746!')

        # click on the 'Confirm' button on payslip
        self.michael_payslip.action_payslip_done()
        self.assertEqual(self.michael_payslip.state, 'done',
                         msg='State should be Done!')

