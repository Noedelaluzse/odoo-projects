from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class IwfPenalty(models.Model):
    _name = 'iwf.penalty'
    _description = 'Sanción Aplicada en Competencia'
    _order = 'timestamp desc'

    # Relaciones principales
    competition_id = fields.Many2one(
        'iwf.competition',
        string='Competencia',
        required=True,
        ondelete='restrict'
    )

    competition_category_id = fields.Many2one(
        'iwf.competition_category',
        string='Categoría',
        domain="[('competition_id', '=', competition_id)]"
    )

    participation_id = fields.Many2one(
        'iwf.participation',
        string='Participación',
        domain="[('competition_id', '=', competition_id), ('competition_category_id', '=', competition_category_id)]",
        ondelete='set null'
    )

    athlete_id = fields.Many2one(
        related='participation_id.athlete_id',
        string='Atleta Sancionado',
        store=True,
        readonly=True
    )

    lift_attempt_id = fields.Many2one(
        'iwf.lift_attempt',
        string='Intento Asociado',
        domain="[('participation_id', '=', participation_id)]",
        ondelete='set null'
    )

    # Tipo de sanción
    type = fields.Selection([
        ('technical', 'Técnica'),
        ('disciplinary', 'Disciplina'),
        ('doping', 'Dopaje')
    ], string='Tipo de Sanción', required=True)

    # Motivo y detalles
    reason = fields.Char(string='Motivo', required=True)
    details = fields.Text(string='Descripción Detallada')

    # Usuario y fecha
    applied_by = fields.Many2one(
        'res.users',
        string='Registrado por',
        default=lambda self: self.env.uid,
        readonly=True
    )

    timestamp = fields.Datetime(
        string='Fecha y Hora',
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )

    # Mostrar campo intento solo si la sanción es técnica
    show_lift_attempt = fields.Boolean(
        compute='_compute_show_lift_attempt',
        store=False
    )

    @api.depends('type')
    def _compute_show_lift_attempt(self):
        for rec in self:
            rec.show_lift_attempt = rec.type == 'technical'
            
    # Validación de tipo técnica requiere intento
    @api.constrains('type', 'lift_attempt_id')
    def _check_technical_requires_attempt(self):
        for rec in self:
            if rec.type == 'technical' and not rec.lift_attempt_id:
                raise ValidationError("Una sanción técnica debe estar vinculada a un intento.")

    # Onchange: limpieza jerárquica
    @api.onchange('competition_id')
    def _onchange_competition_id(self):
        self.competition_category_id = False
        self.participation_id = False

    @api.onchange('competition_category_id')
    def _onchange_competition_category_id(self):
        self.participation_id = False

    # Creación con efecto en el estado del atleta
    @api.model_create_multi
    def create(self, vals):
        penalties = super().create(vals)

        for rec in penalties:
            if rec.type == 'disciplinary' and rec.participation_id:
                rec.participation_id.status = 'disqualified'

            if rec.type == 'doping' and rec.participation_id:
                rec.participation_id.status = 'disqualified'
                result = self.env['iwf.result'].search([
                    ('participation_id', '=', rec.participation_id.id)
                ], limit=1)
                if result:
                    result.disqualified = True

        return penalties