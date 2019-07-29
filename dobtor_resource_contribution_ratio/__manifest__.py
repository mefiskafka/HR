# -*- coding: utf-8 -*-
{
    'name': "dobtor_resource_contribution_ratio",
    'summary': """
        Taiwan Labor/Health insurance (Contribation ratio)
    """,
    'description': """
        Module for resource management.
            -Labor (Contribation ratio)
            -Health (Contribation ratio)
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
