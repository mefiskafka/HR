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
        'base',
        'account',
        'hr_payroll_account',
        'dobtor_hr_labor_insurance',
        'l10n_tw_standard_ifrss',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/account_journal.xml',
        'data/res_partner.xml',
        'wizard/wizard_pay_nhi.xml',
        'wizard/wizard_pay_bli.xml',
        'wizard/wizard_pay_salary.xml',
        'views/account_menuitem.xml',
        'views/res_config_setting_views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
