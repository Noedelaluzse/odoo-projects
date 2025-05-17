# -*- coding: utf-8 -*-
{
    'name': 'Grades Manager',
    'summary': 'Handles grades among students and courses',
    'description': 'Handles grades among students and courses',
    'author': 'MichySoft',
    'category': 'Base',
    'version': '18.0.0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/grades_course_views.xml',
        'views/grades_evaluation_views.xml',
        'views/grades_grade_view.xml',
        'views/grades_manager_menus.xml',
        'wizard/advanced_course_wizard_view.xml',
        "data/ir_actions.xml"
    ],
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
