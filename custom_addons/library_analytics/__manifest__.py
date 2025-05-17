# -*- coding: utf-8 -*-
{
    'name': 'Library Analytics',
    'version': '1.0',
    'category': 'Library',
    'summary': 'Gestión de rentas y estadísticas de lectura',
    'description': """
Este módulo permite:
- Gestionar la renta de libros a usuarios
- Registrar hábitos de lectura (páginas leídas, tiempo)
- Establecer y seguir metas de lectura mensuales
- Automatizar penalizaciones por retrasos
- Visualizar estadísticas y reportes
    """,
    'author': 'MichySoft',
    'website': 'https://tuweb.com',
    'depends': ['base', 'mail'],
    'data': [
        # 'security/library_analytics_security.xml',
        'security/ir.model.access.csv',
        'views/book_views.xml',
        'views/rental_views.xml',
        'views/reading_log_views.xml',
        'views/actions.xml',
        'views/library_manager_menus.xml',


        # Descomenta si incluyes acciones automatizadas o reportes
        # 'data/cron.xml',
        # 'report/report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}