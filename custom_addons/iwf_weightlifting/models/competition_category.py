from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IwfCompetitionCategory(models.Model):
    _name = 'iwf.competition_category'
    _description = 'Categoría de Competencia de Halterofilia'
    _order = 'order_sequence, name'

    name = fields.Char(string='Nombre', required=True)
    competition_id = fields.Many2one('iwf.competition', string='Competencia', required=True, ondelete='cascade')
    weight_category_id = fields.Many2one('iwf.weight_category', string='Categoría de Peso', required=True, ondelete='restrict')
    age_group_id = fields.Many2one('iwf.age_group', string='Grupo de Edad', required=True, ondelete='restrict')
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino')
    ], string='Género', required=True)
    total_participants = fields.Integer(string='Total de Participantes', compute='_compute_total_participants', store=True)
    order_sequence = fields.Integer(string='Orden')
    active = fields.Boolean(string='Activo', default=True)

    participation_ids = fields.One2many('iwf.participation', 'competition_category_id', string='Participaciones')
    can_update_results = fields.Boolean(
        string="Puede actualizar resultados",
        compute="_compute_can_update_results"
    )
    _sql_constraints = [
        ('category_unique', 'unique(competition_id, weight_category_id, age_group_id, gender)',
         'Ya existe una categoría con la misma combinación de edad, peso y género en esta competencia.')
    ]

    @api.depends('participation_ids')
    def _compute_total_participants(self):
        for record in self:
            record.total_participants = len(record.participation_ids)

    @api.onchange('participation_ids')
    def _onchange_participations_warning(self):
        for record in self:
            if not record.participation_ids:
                return {
                    'warning': {
                        'title': 'Sin Participantes',
                        'message': 'No hay participantes registrados en esta categoría.'
                    }
                }

    def action_update_results(self):
        self.ensure_one()
        Result = self.env['iwf.result']
        participations = self.participation_ids.filtered(lambda p: not p.result_id)
        for participation in participations:
            Result.create({'participation_id': participation.id})
        Result.update_positions(self.id)

    @api.depends('competition_id.state')
    def _compute_can_update_results(self):
        for record in self:
            record.can_update_results = record.competition_id.state == 'closed'