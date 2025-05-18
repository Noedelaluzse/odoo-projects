from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class IwfAntidopingTest(models.Model):
    _name = 'iwf.antidoping_test'
    _description = 'Prueba Antidopaje Aplicada al Atleta'
    _order = 'test_date desc'

    # Relación con atleta
    athlete_id = fields.Many2one('iwf.athlete', string='Atleta', required=True)
    competition_id = fields.Many2one('iwf.competition', string='Competencia', ondelete='set null')
    
    # Resultado de prueba y detalles
    test_date = fields.Date(string='Fecha de Prueba', required=True)
    result = fields.Selection([
        ('negative', 'Negativo'),
        ('positive', 'Positivo')
    ], string='Resultado', required=True)

    substance = fields.Char(string='Sustancia Detectada')
    suspension_start = fields.Date(string='Inicio de Suspensión')
    suspension_end = fields.Date(string='Fin de Suspensión')
    notes = fields.Text(string='Observaciones')

    created_by = fields.Many2one('res.users', string='Registrado por', default=lambda self: self.env.uid, readonly=True)

    # Campo computado: si hay suspensión activa
    active_suspension = fields.Boolean(string='Suspensión Activa', compute='_compute_active_suspension', store=True)

    @api.depends('suspension_start', 'suspension_end')
    def _compute_active_suspension(self):
        today = date.today()
        for rec in self:
            rec.active_suspension = (
                rec.suspension_start and rec.suspension_end and
                rec.suspension_start <= today <= rec.suspension_end
            )

    @api.model
    def create(self, vals):
        record = super().create(vals)

        # Sanción automática por dopaje
        if record.result == 'positive':
            self.env['iwf.penalty'].create({
                'athlete_id': record.athlete_id.id,
                'competition_id': record.competition_id.id if record.competition_id else False,
                'type': 'doping',
                'reason': 'Resultado positivo en antidopaje',
                'details': f"Sustancia detectada: {record.substance or 'No especificada'}",
                'applied_by': self.env.uid,
            })

        return record