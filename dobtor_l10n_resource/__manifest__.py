# -*- coding: utf-8 -*-
{
    'name': "dobtor_l10n_resource",

    'summary': """
        Taiwan Labor/Heath insurance (L10n Data)
    """,
    'description': """
        Data for resource.
        Labor (Contribation ratio) : (https://www.bli.gov.tw/0021393.html)
            - Ordinary insurance    (personal - company - government)
                - Normal               20 - 70 - 10
                - occupational unions  60 -  0 - 40
                - fishermen            20 -  0 - 80
            - occupational accident (personal - company - government)
                - Normal                0 - 100 -  0
                - occupational unions  60 -   0 - 40
                - fishermen            20 -   0 - 80
            - employment insurance
                - Normal               20 - 70 - 10

        Health (Contribation ratio) : 
            -              (personal - company - government)
            - Employee         30 - 60 - 10
            - Employer        100 -  0 -  0
    """,

    'author': "Dobtor SI",
    'website': "https://www.dobtor.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'dobtor_resource_contribution_ratio',
    ],
    'data': [
        # 'views/views.xml',
        'data/resource.labor.contribution_ratio.csv',
        'data/resource.health.contribution_ratio.csv'
    ],
}
