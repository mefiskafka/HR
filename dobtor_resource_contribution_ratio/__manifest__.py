# -*- coding: utf-8 -*-
{
    'name': "dobtor_resource_contribution_ratio",

    'summary': """
        Taiwan Labor insurance (Contribation ratio)
    """,
    'description': """
        Module for resource management.

        Labor (Contribation ratio) : (https://www.bli.gov.tw/0021393.html)
            - normal accident       (company - personal - government)
                - Normal               70 - 20 - 10
                - occupational unions   0 - 60 - 40
                - fishermen             0 - 20 - 80
            - occupational accident (company - personal - government)
                - Normal              100 -  0 -  0
                - occupational unions   0 - 60 - 40
                - fishermen             0 - 20 - 80
            - employment insurance
                - Normal               70 - 20 - 10

        Health (Contribation ratio) : 
            
    """,

    'author': "Dobtor SI",
    'website': "https://www.dobtor.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'resource',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/contribution_ratio_views.xml',
    ],
}
