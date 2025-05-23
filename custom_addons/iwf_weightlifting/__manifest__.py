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
        'contacts',
        'web',
    ],
    'data': [
        # Seguridad primero
        'security/iwf_security.xml',
        'security/ir.model.access.csv',

        # Menú base (sin actions)
        'views/menu_base.xml',

        # Vistas que definen actions
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
        'views/dashboard_organizer_views.xml',
        
        'views/generate_results_wizard_views.xml', 
        # Menús con actions (estos van hasta el final)
        'views/menu_items.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'web._assets_primary_variables',
        'web._assets_backend_helpers',
        'web._assets_core',
        'web.assets_backend',

        # Tus archivos JS/XML
        'iwf_weightlifting/static/src/components/**/*.js',
        'iwf_weightlifting/static/src/components/**/*.xml',
    ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}