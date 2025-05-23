from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class IwfEquipmentCheck(models.Model):
    _name = 'iwf.equipment_check'
    _description = 'Revisión de Indumentaria del Atleta'
    _order = 'timestamp desc'

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
        string='Atleta',
        store=True,
        readonly=True
    )

    # Elementos de revisión
    singlet_ok = fields.Boolean(string='Singlet Correcto')
    belt_ok = fields.Boolean(string='Cinturón Correcto')
    shoes_ok = fields.Boolean(string='Calzado Permitido')
    wristwraps_ok = fields.Boolean(string='Muñequeras Permitidas')
    tape_ok = fields.Boolean(string='Cintas Permitidas')

    # Estado general
    approved = fields.Boolean(
        string='Revisión Aprobada',
        compute='_compute_approved',
        store=True
    )

    notes = fields.Text(string='Observaciones')
    reviewed_by = fields.Many2one(
        'res.users',
        string='Revisado por',
        default=lambda self: self.env.uid,
        readonly=True
    )
    timestamp = fields.Datetime(
        string='Fecha de Revisión',
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )

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

    @api.onchange('competition_id')
    def _onchange_competition(self):
        self.competition_category_id = False
        self.participation_id = False

    @api.onchange('competition_category_id')
    def _onchange_category(self):
        self.participation_id = False

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if not record.approved and record.notes:
            if 'crítica' in record.notes.lower():
                # Aquí podría ir lógica futura para crear una sanción automáticamente
                pass
        return record