{
    'name': 'IWF Weightlifting',
    'version': '1.0',
    'summary': 'Gestión de competencias de halterofilia conforme al reglamento oficial de la IWF.',
    'description': 'Este módulo permite registrar atletas, gestionar eventos, registrar intentos, calcular resultados, y controlar cumplimiento reglamentario en halterofilia.',
    'category': 'Sports/Competition',
    'author': 'Tu Nombre o Empresa',
    'website': 'https://tusitio.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts'
    ],
    'data': [
        'security/iwf_security.xml',             # ✔ define los grupos aquí
        'security/ir.model.access.csv',          # ✔ luego los usas en permisos
        'views/rule_set_views.xml',
        'views/age_group_views.xml',
        'views/weight_category_views.xml',
        'views/athlete_views.xml',
        'views/competition_views.xml',
        'views/competition_category_views.xml',
        'views/participation_views.xml',
        'views/lift_attempt_views.xml',
        'views/result_views.xml',
        'views/penalty_views.xml',
        'views/equipment_check_views.xml',
        'views/antidoping_test_views.xml',
        'views/menus.xml',
        # 'report/result_report.xml',
        # 'report/penalty_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # si necesitas JS o CSS personalizados, aquí los cargas
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}