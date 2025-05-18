from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IwfResult(models.Model):
    _name = 'iwf.result'
    _description = 'Resultado Final del Atleta'
    _order = 'position'

    participation_id = fields.Many2one(
        'iwf.participation',
        string='Participación',
        required=True,
        ondelete='cascade'
    )

    best_snatch = fields.Float(string='Mejor Arranque', compute='_compute_best_lifts', store=True)
    best_cleanjerk = fields.Float(string='Mejor Envión', compute='_compute_best_lifts', store=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)

    position = fields.Integer(string='Posición')
    medal = fields.Selection([
        ('gold', 'Oro'),
        ('silver', 'Plata'),
        ('bronze', 'Bronce')
    ], string='Medalla')

    disqualified = fields.Boolean(string='Descalificado', default=False)
    tie_breaker_applied = fields.Boolean(string='Desempate Aplicado', default=False)
    tie_breaker_notes = fields.Text(string='Notas de Desempate')

    @api.depends('participation_id.lift_attempt_ids')
    def _compute_best_lifts(self):
        for record in self:
            attempts = record.participation_id.lift_attempt_ids.filtered(lambda a: a.status == 'valid')
            snatches = attempts.filtered(lambda a: a.type == 'snatch').mapped('weight')
            cleanjerks = attempts.filtered(lambda a: a.type == 'cleanjerk').mapped('weight')
            record.best_snatch = max(snatches) if snatches else 0.0
            record.best_cleanjerk = max(cleanjerks) if cleanjerks else 0.0
            record.disqualified = not snatches or not cleanjerks

    @api.depends('best_snatch', 'best_cleanjerk')
    def _compute_total(self):
        for record in self:
            record.total = record.best_snatch + record.best_cleanjerk

    def update_positions(self, category_id):
        Result = self.env['iwf.result']
        Participation = self.env['iwf.participation']
        participations = Participation.search([('competition_category_id', '=', category_id)])

        for p in participations:
            if not Result.search([('participation_id', '=', p.id)]):
                Result.create({'participation_id': p.id})

        results = Result.search([
            ('participation_id.competition_category_id', '=', category_id),
            ('disqualified', '=', False)
        ])

        sorted_results = results.sorted(
            key=lambda r: (
                -r.total,
                -r.best_cleanjerk,
                r.get_attempt_count(),
                r.participation_id.lot_number or 9999
            )
        )

        # Determinar empate
        last_total = None
        last_cleanjerk = None
        seen_positions = {}

        for index, result in enumerate(sorted_results, start=1):
            result.position = index

            if index == 1:
                result.medal = 'gold'
            elif index == 2:
                result.medal = 'silver'
            elif index == 3:
                result.medal = 'bronze'
            else:
                result.medal = False

            # Detectar si se aplicó desempate
            if (
                last_total is not None and result.total == last_total and
                result.best_cleanjerk != last_cleanjerk
            ):
                result.tie_breaker_applied = True
                result.tie_breaker_notes = "Desempate aplicado por mejor envión."
            else:
                result.tie_breaker_applied = False
                result.tie_breaker_notes = False

            last_total = result.total
            last_cleanjerk = result.best_cleanjerk

    def get_attempt_count(self):
        return len(self.participation_id.lift_attempt_ids.filtered(lambda a: a.status == 'valid'))

    def name_get(self):
        return [(rec.id, f"{rec.participation_id.athlete_id.name} ({rec.total} kg)") for rec in self]