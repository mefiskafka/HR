# -*- coding: utf-8 -*-
{
    'name': "dobtor_leave_management",

    'summary': """
        annual leave & compensate the missed work time & work overtime Feature
    """,

    'description': """
       - Annual Leave
       - Compensate the missed work time
       - Work Overtime
    """,

    'author': "Dobtor SI",
    'website': "https://www.dobtor.com",
    'category': 'HR',
    'version': '0.1',
    'depends': [
        'base',
        'hr_holidays',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
