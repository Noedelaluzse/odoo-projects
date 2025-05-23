from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class IwfAntidopingTest(models.Model):
    _name = 'iwf.antidoping_test'
    _description = 'Prueba Antidopaje Aplicada al Atleta'
    _order = 'test_date desc'

    # Relaciones jerárquicas
    competition_id = fields.Many2one(
        'iwf.competition',
        string='Competencia',
        required=True,
        ondelete='restrict'
    )

    competition_category_id = fields.Many2one(
        'iwf.competition_category',
        string='Categoría',
        domain="[('competition_id', '=', competition_id)]",
        required=True,
        ondelete='restrict'
    )

    participation_id = fields.Many2one(
        'iwf.participation',
        string='Participación',
        domain="[('competition_id', '=', competition_id), ('competition_category_id', '=', competition_category_id)]",
        required=True,
        ondelete='restrict'
    )

    athlete_id = fields.Many2one(
        related='participation_id.athlete_id',
        string='Atleta',
        store=True,
        readonly=True
    )

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

    created_by = fields.Many2one(
        'res.users',
        string='Registrado por',
        default=lambda self: self.env.uid,
        readonly=True
    )

    active_suspension = fields.Boolean(
        string='Suspensión Activa',
        compute='_compute_active_suspension',
        store=True
    )

    @api.depends('suspension_start', 'suspension_end')
    def _compute_active_suspension(self):
        today = date.today()
        for rec in self:
            rec.active_suspension = (
                rec.suspension_start and rec.suspension_end and
                rec.suspension_start <= today <= rec.suspension_end
            )

    @api.onchange('competition_id')
    def _onchange_competition_id(self):
        self.competition_category_id = False
        self.participation_id = False

    @api.onchange('competition_category_id')
    def _onchange_competition_category_id(self):
        self.participation_id = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.result == 'positive':
                record.env['iwf.penalty'].create({
                    'competition_id': record.competition_id.id,
                    'competition_category_id': record.competition_category_id.id,
                    'participation_id': record.participation_id.id,
                    'type': 'doping',
                    'reason': 'Resultado positivo en antidopaje',
                    'details': f"Sustancia detectada: {record.substance or 'No especificada'}",
                    'applied_by': record.env.uid,
                })
        return records