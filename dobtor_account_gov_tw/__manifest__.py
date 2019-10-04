# -*- coding: utf-8 -*-
{
    'name': "dobtor_account_gov_tw",

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
        'sale',
        'account',
        'l10n_tw_standard_ifrss',
        'dobtor_hr_labor_insurance',
        'hr_payroll_account'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/account_journal.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr_salary_rule_formula_type.xml',
        'data/hr_salary_rule_formula_select.xml',
        'data/hr_salary_rule.xml',
        'data/hr_salary_structure.xml',
        'data/notespayable_data.xml',
        'data/res_partner.xml',
        'data/product.xml',
        'views/product_views.xml',
        'views/res_partner.xml',
        'views/hr_payroll_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/notespayable_views.xml',
        'views/account_invoice_views.xml',
        'views/account_menuitem.xml',
        'views/res_config_setting_views.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
}
