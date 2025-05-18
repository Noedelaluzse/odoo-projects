from odoo import models, fields

class IwfDashboardOrganizer(models.TransientModel):
    _name = 'iwf.dashboard.organizer'
    _description = 'Dashboard del Organizador (Estadísticas del Evento)'

    athletes_count = fields.Integer(string='Atletas Registrados')
    attempts_count = fields.Integer(string='Intentos Completados')
    active_penalties_count = fields.Integer(string='Sanciones Activas')