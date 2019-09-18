# -*- coding: utf-8 -*-
{
    'name': "dobtor_hr_labor_insurance_account",

    'summary': """
        handle payslip account 
    """,

    'description': """
        handle payslip account 
    """,

    'author': "Dobtor SI",
    'website': "https://www.dobtor.com",
    'category': 'Human Resources',
    'version': '0.1',

    'depends': [
        'base'
        'account',
        'hr_payroll_account'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/account_journal.xml',
        'data/res_partner.xml',
        'views/views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
