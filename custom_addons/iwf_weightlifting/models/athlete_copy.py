from odoo import models, fields, api  # Importación de módulos Odoo para definir modelos, campos y API
from odoo.exceptions import ValidationError  # Importación de excepción para validaciones personalizadas
from datetime import date  # Importación de fecha actual


class IwfAthlete(models.Model):
    _name = 'iwf.athlete'  # Nombre técnico del modelo
    _description = 'Atleta de Halterofilia'  # Descripción legible del modelo
    _order = 'name'  # Orden por defecto en listas

    # Identificador técnico único generado automáticamente por secuencia
    internal_id = fields.Char(
        string='ID Interno',
        readonly=True,
        copy=False
    )

    # Código legible y público para eventos, generado automáticamente
    athlete_code = fields.Char(
        string='Código Público',
        readonly=True,
        copy=False
    )

    # Nombre completo del atleta
    name = fields.Char(string='Nombre', required=True)

    # Fecha de nacimiento, base para calcular edad y categoría
    birth_date = fields.Date(string='Fecha de Nacimiento', required=True)

    # Género del atleta (Masculino/Femenino)
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino')
    ], string='Género', required=True)

    # País de origen o nacionalidad
    country_id = fields.Many2one('res.country', string='País')

    # Peso corporal registrado al momento del pesaje
    weight = fields.Float(string='Peso Corporal (kg)', required=True)

    # Edad calculada automáticamente a partir de birth_date
    age = fields.Integer(string='Edad', compute='_compute_age', store=True)

    # Grupo de edad asignado automáticamente según reglas
    age_category_id = fields.Many2one('iwf.age_group', string='Grupo de Edad', compute='_compute_age_category', store=True)

    # Subgrupo máster calculado en texto (ej. 40–44)
    master_group = fields.Char(string='Bloque Máster')

    # Categoría de peso asignada automáticamente
    weight_category_id = fields.Many2one('iwf.weight_category', string='Categoría de Peso', compute='_compute_weight_category', store=True)

    # Club o federación a la que pertenece el atleta
    club_id = fields.Many2one('res.partner', string='Club o Federación')

    # Imagen de perfil del atleta (usada en vista kanban o gafetes)
    image = fields.Binary(string='Foto')

    # Observaciones adicionales sobre el atleta
    notes = fields.Text(string='Observaciones')

    # Estado de actividad del atleta en el sistema
    active = fields.Boolean(string='Activo', default=True)

    # Relación con sanciones
    penalty_ids = fields.One2many(
        'iwf.penalty',
        'athlete_id',
        string='Sanciones'
    )

    # Restricción para que el código público sea único en toda la base de datos
    _sql_constraints = [
        ('code_unique', 'unique(athlete_code)', 'El código público del atleta debe ser único.')
    ]

    # FORZAR la generación de secuencias si no fueron asignadas por defecto (cuando se crea el atleta)
    @api.model
    def create(self, vals):
        vals['internal_id'] = vals.get('internal_id') or self.env['ir.sequence'].next_by_code('iwf.athlete.internal')
        vals['athlete_code'] = vals.get('athlete_code') or self.env['ir.sequence'].next_by_code('iwf.athlete.code')
        return super().create(vals)

    # Cálculo de edad en base al año actual y el año de nacimiento
    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = date.today()  # Fecha actual
                record.age = today.year - record.birth_date.year  # Cálculo simple por año

    # Asignación automática de grupo de edad en función de la edad
    @api.depends('birth_date')
    def _compute_age_category(self):
        for record in self:
            age = record.age
            if age and record.gender:
                domain = [
                    ('min_age', '<=', age),
                    '|',
                    ('max_age', '>=', age),
                    ('max_age', '=', False),
                    ('active', '=', True)
                ]
                matched = self.env['iwf.age_group'].search(domain)
                if matched:
                    record.age_category_id = matched[0].id
                    if matched[0].is_master:
                        lower = matched[0].min_age
                        upper = matched[0].max_age or lower + 4
                        record.master_group = f"{lower}–{upper}"
                else:
                    record.age_category_id = False
                    record.master_group = False

    # Asignación automática de la categoría de peso
    @api.depends('weight', 'gender')
    def _compute_weight_category(self):
        for record in self:
            if not (record.weight and record.gender and record.age_category_id):
                record.weight_category_id = False
                continue
            domain = [
                ('rule_set_id', '=', record.age_category_id.rule_set_id.id),
                ('gender', '=', record.gender),
                ('min_weight', '<=', record.weight),
                ('max_weight', '>=', record.weight),
                ('active', '=', True)
            ]
            matched = self.env['iwf.weight_category'].search(domain, limit=1)
            record.weight_category_id = matched.id if matched else False