from odoo import models, fields, api

# Modelo principal que representa una competencia oficial de halterofilia
class IwfCompetition(models.Model):
    _name = 'iwf.competition'  # Nombre técnico del modelo
    _description = 'Competencia de Halterofilia'  # Descripción visible
    _order = 'start_date desc'  # Orden por defecto: competencias más recientes primero

    # Nombre oficial de la competencia
    name = fields.Char(string='Nombre', required=True)

    # Código único interno para identificar la competencia (ej. CN-S1725)
    code = fields.Char(string='Código', required=True, copy=False)

    # Fecha de inicio de la competencia
    start_date = fields.Date(string='Fecha de Inicio', required=True)

    # Fecha de finalización
    end_date = fields.Date(string='Fecha de Finalización', required=True)

    # Ciudad o sede donde se lleva a cabo el evento
    location = fields.Char(string='Ciudad o Sede')

    # País anfitrión del evento (relación con res.country)
    country_id = fields.Many2one('res.country', string='País')

    # Estado de la competencia para controlar el ciclo de vida
    state = fields.Selection([
        ('draft', 'Borrador'),     # Aún en configuración
        ('open', 'Abierto'),       # Abierto para registros
        ('closed', 'Cerrado'),     # Finalizado
        ('archived', 'Archivado')  # Archivado (referencia histórica)
    ], string='Estado', default='draft', tracking=True)  # tracking=True permite seguimiento con mail.thread

    # Conjunto de reglas aplicadas a la competencia (relación con iwf.rule_set)
    rule_set_id = fields.Many2one(
        'iwf.rule_set',
        string='Conjunto de Reglas',
        required=True,
        ondelete='restrict'  # No permitir eliminar una regla si está en uso aquí
    )

    # Entidad organizadora (club o federación) de tipo res.partner
    organizer_id = fields.Many2one(
        'res.partner',
        string='Organizador',
        required=True
    )

    # Total de atletas inscritos (campo calculado)
    total_athletes = fields.Integer(
        string='Total de Atletas',
        compute='_compute_total_athletes',
        store=True
    )

    # Total de categorías activas definidas en el evento (campo calculado)
    total_categories = fields.Integer(
        string='Total de Categorías',
        compute='_compute_total_categories',
        store=True
    )

    # Notas administrativas o logísticas
    notes = fields.Text(string='Notas')

    # Relaciones One2many con participación y categorías (a definir en sus respectivos modelos)
    participation_ids = fields.One2many(
        'iwf.participation',
        'competition_id',
        string='Participaciones'
    )

    competition_category_ids = fields.One2many(
        'iwf.competition_category',
        'competition_id',
        string='Categorías'
    )

    # Restricción de unicidad en el campo code
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código de la competencia debe ser único.')
    ]

    # Cómputo del total de atletas a partir de las participaciones
    @api.depends('participation_ids')
    def _compute_total_athletes(self):
        for record in self:
            record.total_athletes = len(record.participation_ids)

    # Cómputo del total de categorías configuradas en la competencia
    @api.depends('competition_category_ids')
    def _compute_total_categories(self):
        for record in self:
            record.total_categories = len(record.competition_category_ids)