# -*- coding: utf-8 -*-
{
    'name': "dobtor_attendance_management",

    'summary': """
        annual leave & compensate the missed work time & work overtime Feature
    """,

    'description': """
       - Attendance
           - Late
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
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_attendance_late_data.xml',
        'data/hr_attendance_policies_data.xml',
        'views/hr_attendance_late_views.xml',
        'views/hr_attendance_policies_views.xml',
        'views/hr_attendance_sheet_views.xml',
        'views/hr_attendance_menuitem.xml',
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}