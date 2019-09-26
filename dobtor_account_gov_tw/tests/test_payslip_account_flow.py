# -*- coding: utf-8 -*-
from odoo.tests.common import tagged
from odoo.addons.dobtor_hr_labor_insurance.tests.common import TestHrAccountCommon


@tagged('-at_install', 'post_install')
class Payship_Account(TestHrAccountCommon):

    def test_00_(self):
        self.assertEqual(1, 1, msg='1 is should be equal 1 !')
