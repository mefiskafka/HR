# -*- coding: utf-8 -*-
{
    'name': "dobtor_hr_labor_insurance",

    'summary': """
        Taiwan Labor insurance (Rule)
    """,
    'description': """
        Employee : hard code version
            - Labor (Normal Accident)
                - Ordinary Insurance :     
                    - result = -round(contract.wage * 0.10 * 0.2)
                    - setting : Ordinary Insurance Premium
                - Occupational Accident :  
                    - result = -round(contract.wage * 0.0011 * 0)
                    - setting : Occupational Accident Insurance Premium
            - Health Insurance : 
                - setting : Ordinary Insurance Premium 

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
        'hr_payroll',
        'dobtor_resource_contribution_ratio',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/hr_salary_rule_category.xml',
        'data/hr_salary_rule.xml',
        'data/hr_salary_structure.xml',
        'views/res_config_settings_views.xml',
        'views/hr_contract_views.xml',
    ],
}
