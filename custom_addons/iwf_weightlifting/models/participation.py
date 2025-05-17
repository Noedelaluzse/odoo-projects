from odoo import models, fields, api
from odoo.exceptions import ValidationError
import random


class IwfParticipation(models.Model):
    _name = 'iwf.participation'  # Nombre técnico del modelo
    _description = 'Participación en Competencia de Halterofilia'  # Descripción visible
    _order = 'lot_number'  # Orden por número de sorteo

    # Relación con el atleta inscrito
    athlete_id = fields.Many2one(
        'iwf.athlete',
        string='Atleta',
        required=True,
        ondelete='restrict'
    )

    # Relación con la competencia
    competition_id = fields.Many2one(
        'iwf.competition',
        string='Competencia',
        required=True,
        ondelete='cascade'
    )

    # Categoría de competencia en la que participa el atleta
    competition_category_id = fields.Many2one(
        'iwf.competition_category',
        string='Categoría',
        required=True,
        ondelete='restrict'
    )

    # Peso del atleta al momento del pesaje oficial
    weight_in = fields.Float(
        string='Peso Corporal en Pesaje (kg)',
        required=True
    )

    # Número asignado aleatoriamente al atleta para determinar orden en la competencia
    lot_number = fields.Integer(
        string='Número de Sorteo'
    )

    # Peso solicitado para el primer intento de arranque
    snatch_first_attempt = fields.Float(
        string='Arranque - Primer Intento'
    )

    # Peso solicitado para el primer intento de envión
    cleanjerk_first_attempt = fields.Float(
        string='Envión - Primer Intento'
    )

    # Estado actual de la participación
    status = fields.Selection([
        ('registered', 'Inscrito'),
        ('active', 'Activo'),
        ('disqualified', 'Descalificado'),
        ('withdrawn', 'Retirado')
    ], string='Estado', default='registered')

    # Comentarios adicionales del jurado o comité técnico
    notes = fields.Text(string='Observaciones')

        # Intentos realizados (arranque y envión)
    lift_attempt_ids = fields.One2many('iwf.lift_attempt', 'participation_id', string='Intentos')

    # Resultado generado a partir de esta participación
    #result_id = fields.Many2one('iwf.result', string='Resultado', ondelete='set null', index=True)
    result_id = fields.Many2one(
        'iwf.result',
        string='Resultado',
        ondelete='set null',
        help='Resultado final generado a partir de los intentos de esta participación.'
    )
    # Restricción: Un atleta no puede inscribirse más de una vez en la misma competencia y categoría
    _sql_constraints = [
        (
            'unique_participation',
            'unique(athlete_id, competition_id, competition_category_id)',
            'El atleta ya está inscrito en esta categoría dentro de la competencia.'
        ),
        (
            'unique_result_per_participation',
            'unique(result_id)',
            'Esta participación ya tiene un resultado asignado.'
        )
    ]

    @api.model
    def create(self, vals):
        """Asigna un número de sorteo aleatorio si no se proporciona."""
        if not vals.get('lot_number'):
            vals['lot_number'] = random.randint(1, 999)
        return super().create(vals)

    @api.constrains('weight_in', 'competition_category_id')
    def _check_weight_in_range(self):
        """Valida que el peso del atleta esté dentro del rango permitido de su categoría."""
        for rec in self:
            category = rec.competition_category_id.weight_category_id
            if category:
                if category.min_weight and rec.weight_in < category.min_weight:
                    raise ValidationError("El peso ingresado está por debajo del límite de la categoría.")
                if category.max_weight and rec.weight_in > category.max_weight:
                    raise ValidationError("El peso ingresado excede el límite de la categoría.")

    # Relaciones futuras (comentadas hasta que los modelos estén definidos)



    # Sanciones relacionadas con esta participación
    # penalty_ids = fields.One2many('iwf.penalty', 'participation_id', string='Sanciones')