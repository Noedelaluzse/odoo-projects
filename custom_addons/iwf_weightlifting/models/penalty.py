from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class IwfPenalty(models.Model):
    _name = 'iwf.penalty'
    _description = 'Sanción Aplicada en Competencia'
    _order = 'timestamp desc'

    # Relaciones principales
    athlete_id = fields.Many2one('iwf.athlete', string='Atleta Sancionado', required=True)
    competition_id = fields.Many2one('iwf.competition', string='Competencia', ondelete='restrict')
    participation_id = fields.Many2one('iwf.participation', string='Participación', ondelete='set null')
    lift_attempt_id = fields.Many2one('iwf.lift_attempt', string='Intento Asociado', ondelete='set null')

    # Tipo de sanción
    type = fields.Selection([
        ('technical', 'Técnica'),
        ('disciplinary', 'Disciplina'),
        ('doping', 'Dopaje')
    ], string='Tipo de Sanción', required=True)

    # Motivo y detalles
    reason = fields.Char(string='Motivo', required=True)
    details = fields.Text(string='Descripción Detallada')

    # Usuario que aplica la sanción
    applied_by = fields.Many2one('res.users', string='Registrado por', default=lambda self: self.env.uid, readonly=True)
    timestamp = fields.Datetime(string='Fecha y Hora', default=lambda self: fields.Datetime.now(), readonly=True)

    # Validación: si es técnica, requiere intento
    @api.constrains('type', 'lift_attempt_id')
    def _check_technical_requires_attempt(self):
        for rec in self:
            if rec.type == 'technical' and not rec.lift_attempt_id:
                raise ValidationError("Una sanción técnica debe estar vinculada a un intento.")

    # Validación y efectos al crear
    @api.model_create_multi
    def create(self, vals):
        penalty = super().create(vals)

        # Disciplina grave → descalifica
        if penalty.type == 'disciplinary' and penalty.participation_id:
            penalty.participation_id.status = 'disqualified'

        # Dopaje → descalifica e invalida resultado si existe
        if penalty.type == 'doping' and penalty.participation_id:
            penalty.participation_id.status = 'disqualified'
            result = self.env['iwf.result'].search([('participation_id', '=', penalty.participation_id.id)], limit=1)
            if result:
                result.disqualified = True

        return penalty