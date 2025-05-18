from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class IwfEquipmentCheck(models.Model):
    _name = 'iwf.equipment_check'
    _description = 'Revisión de Indumentaria del Atleta'
    _order = 'timestamp desc'

    # Relación con atleta
    athlete_id = fields.Many2one('iwf.athlete', string='Atleta', required=True)
    competition_id = fields.Many2one('iwf.competition', string='Competencia', required=True, ondelete='restrict')

    # Elementos de revisión
    singlet_ok = fields.Boolean(string='Singlet Correcto')
    belt_ok = fields.Boolean(string='Cinturón Correcto')
    shoes_ok = fields.Boolean(string='Calzado Permitido')
    wristwraps_ok = fields.Boolean(string='Muñequeras Permitidas')
    tape_ok = fields.Boolean(string='Cintas Permitidas')

    # Estado general
    approved = fields.Boolean(string='Revisión Aprobada', compute='_compute_approved', store=True)

    # Notas adicionales
    notes = fields.Text(string='Observaciones')
    reviewed_by = fields.Many2one('res.users', string='Revisado por', default=lambda self: self.env.uid, readonly=True)
    timestamp = fields.Datetime(string='Fecha de Revisión', default=lambda self: fields.Datetime.now(), readonly=True)

    @api.depends('singlet_ok', 'belt_ok', 'shoes_ok', 'wristwraps_ok', 'tape_ok')
    def _compute_approved(self):
        for rec in self:
            rec.approved = all([
                rec.singlet_ok,
                rec.belt_ok,
                rec.shoes_ok,
                rec.wristwraps_ok,
                rec.tape_ok
            ])

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if not record.approved and record.notes:
            if 'crítica' in record.notes.lower():
                # Sugerencia: lógica futura para crear una penalización vinculada
                pass  # Aquí podrías lanzar un wizard o crear automáticamente un iwf.penalty
        return record