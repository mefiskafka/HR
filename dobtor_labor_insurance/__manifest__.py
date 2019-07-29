# -*- coding: utf-8 -*-
{
    'name': "dobtor_labor_insurance",

    'summary': """
        Taiwan Labor insurance
    """,
    'description': """
        Employee :
            - Normal Accident
            - Occupational Injury 
            - Employment Accident
        Company :
            - Normal Accident
            - Occupational Injury (https://www.bli.gov.tw/0100540.html)
            - Employment Accident

        Function : 
            - 
    """,

    'author': "dobtor SI",
    'website': "https://www.dobtor.com",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': [
        'base',
        'hr',
        'hr_payroll'
    ],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
}
