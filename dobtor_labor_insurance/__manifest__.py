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
        Labor (Copayment) ratio: (https://www.bli.gov.tw/0021393.html)
            normal accident       (company - personal - government)
                - Normal               70 - 20 - 10
                - occupational unions   0 - 60 - 40
                - fishermen             0 - 20 - 80
            occupational accident (company - personal - government)
                - Normal              100 -  0 -  0
                - occupational unions   0 - 60 - 40
                - fishermen             0 - 20 - 80
            employment insurance
                - Normal               70 - 20 - 10
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
