from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GenerateResultsWizard(models.TransientModel):
    _name = 'generate.results.wizard'
    _description = 'Asistente para generar resultados finales'

    competition_id = fields.Many2one(
        'iwf.competition',
        string='Competencia',
        required=True
    )
    competition_category_id = fields.Many2one(
        'iwf.competition_category',
        string='Categoría de Competencia',
        domain="[('competition_id', '=', competition_id)]",
        required=True
    )
    gender = fields.Selection(
        [('male', 'Masculino'), ('female', 'Femenino')],
        string='Género',
        required=True
    )

    def action_generate_results(self):
        self.ensure_one()

        participation_model = self.env['iwf.participation']
        result_model = self.env['iwf.result']

        participations = participation_model.search([
            ('competition_id', '=', self.competition_id.id),
            ('competition_category_id', '=', self.competition_category_id.id),
            ('athlete_id.gender', '=', self.gender),
        ])

        if not participations:
            raise ValidationError('No hay atletas registrados con los filtros proporcionados.')

        # Eliminar resultados anteriores (opcional)
        old_results = result_model.search([
            ('participation_id', 'in', participations.ids)
        ])
        old_results.unlink()

        # Crear nuevos resultados
        for participation in participations:
            result_model.create({'participation_id': participation.id})

        # Calcular posiciones
        result_model.update_positions(self.competition_category_id.id)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'iwf.result',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('participation_id', 'in', participations.ids)],
        }