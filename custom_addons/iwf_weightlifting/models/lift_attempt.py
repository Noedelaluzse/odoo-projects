from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class IwfLiftAttempt(models.Model):
    _name = 'iwf.lift_attempt'
    _description = 'Intento de Levantamiento en Competencia'
    _order = 'timestamp'

    # Participación a la que pertenece este intento (relación con iwf.participation)
    participation_id = fields.Many2one(
        'iwf.participation',
        string='Participación',
        required=True,
        ondelete='cascade'
    )

    # Tipo de levantamiento: arranque o envión
    type = fields.Selection([
        ('snatch', 'Arranque'),
        ('cleanjerk', 'Envión')
    ], string='Tipo', required=True)

    # Número de intento: 1, 2 o 3
    attempt_number = fields.Selection([
        ('1', 'Primer Intento'),
        ('2', 'Segundo Intento'),
        ('3', 'Tercer Intento'),
    ], string='Número de Intento', required=True)

    # Peso solicitado para el intento
    weight = fields.Float(string='Peso (kg)', required=True)

    # Estado del intento: válido, nulo, pendiente, etc.
    status = fields.Selection([
        ('pending', 'Pendiente'),
        ('valid', 'Válido'),
        ('no_lift', 'Nulo'),
        ('not_performed', 'No realizado')
    ], string='Resultado', default='pending')

    # Luces blancas y rojas emitidas por los tres jueces
    white_judge_1 = fields.Boolean(string='Juez 1 - Blanca')
    white_judge_2 = fields.Boolean(string='Juez 2 - Blanca')
    white_judge_3 = fields.Boolean(string='Juez 3 - Blanca')

    red_judge_1 = fields.Boolean(string='Juez 1 - Roja')
    red_judge_2 = fields.Boolean(string='Juez 2 - Roja')
    red_judge_3 = fields.Boolean(string='Juez 3 - Roja')

    # Observaciones técnicas o comentarios del jurado
    notes = fields.Text(string='Observaciones')

    # Fecha y hora del intento registrado
    timestamp = fields.Datetime(string='Registrado en', default=lambda self: datetime.now())

    # Restricción: no más de 3 intentos por tipo de levantamiento y atleta
    @api.constrains('participation_id', 'type', 'attempt_number')
    def _check_attempt_limits(self):
        for record in self:
            domain = [
                ('participation_id', '=', record.participation_id.id),
                ('type', '=', record.type)
            ]
            attempts = self.env['iwf.lift_attempt'].search(domain)
            if len(attempts.filtered(lambda a: a.id != record.id)) >= 3:
                raise ValidationError("No se pueden registrar más de 3 intentos por tipo de levantamiento.")

    # Validación: peso no puede disminuir respecto al intento anterior si fue válido
    @api.constrains('weight')
    def _check_weight_progression(self):
        for record in self:
            prev_attempts = self.env['iwf.lift_attempt'].search([
                ('participation_id', '=', record.particpiation_id.id),
                ('type', '=', record.type),
                ('status', '=', 'valid'),
                ('attempt_number', '<', record.attempt_number)
            ])
            if prev_attempts:
                max_prev_weight = max(prev_attempts.mapped('weight'))
                if record.weight < max_prev_weight:
                    raise ValidationError("El nuevo intento debe ser igual o mayor al mejor intento válido anterior.")
    @api.constrains(
    'white_judge_1', 'white_judge_2', 'white_judge_3',
    'red_judge_1', 'red_judge_2', 'red_judge_3'
    )
    def _check_judge_lights(self):
        for record in self:
            white_count = sum([
                record.white_judge_1,
                record.white_judge_2,
                record.white_judge_3
            ])
            red_count = sum([
                record.red_judge_1,
                record.red_judge_2,
                record.red_judge_3
            ])

            # Máximo 3 luces en total
            if white_count + red_count > 3:
                raise ValidationError("Solo se pueden marcar 3 luces entre blancas y rojas.")

            # Un juez no puede emitir 2 luces
            if record.white_judge_1 and record.red_judge_1:
                raise ValidationError("El Juez 1 no puede marcar blanca y roja al mismo tiempo.")
            if record.white_judge_2 and record.red_judge_2:
                raise ValidationError("El Juez 2 no puede marcar blanca y roja al mismo tiempo.")
            if record.white_judge_3 and record.red_judge_3:
                raise ValidationError("El Juez 3 no puede marcar blanca y roja al mismo tiempo.")