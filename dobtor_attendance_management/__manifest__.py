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
        'hr_payroll',
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/post_change_data.xml',
        'data/resource_calendar_data.xml',
        'data/hr_attendance_late_data.xml',
        'data/hr_attendance_diff_data.xml',
        'data/hr_attendance_absence_data.xml',
        'data/hr_attendance_policies_data.xml',
        'data/hr_leave_type_data.xml',
        'data/hr_salary_rule_data.xml',
        'views/hr_attendance_rule_views.xml',
        'views/hr_attendance_late_views.xml',
        'views/hr_attendance_diff_views.xml',
        'views/hr_attendance_absence_views.xml',
        'views/hr_attendance_overtime_views.xml',
        'views/hr_attendance_policies_views.xml',
        'views/hr_attendance_sheet_views.xml',
        'views/hr_attendance_menuitem.xml',
        'views/hr_leave_views.xml',
        'views/hr_contract_views.xml',
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
