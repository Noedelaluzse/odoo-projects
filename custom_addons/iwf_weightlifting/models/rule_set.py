from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IwfRuleSet(models.Model):
    _name = 'iwf.rule_set'
    _description = 'Conjunto de Reglas de Halterofilia'
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True, copy=False)
    active = fields.Boolean(string='Activo', default=True)
    description = fields.Text(string='Descripción')
    default = fields.Boolean(string='Por Defecto')
    allow_ties = fields.Boolean(string='Permitir Empates', default=True)
    use_master_groups = fields.Boolean(string='Usar Subdivisión de Másters', default=True)
    min_weight_increment = fields.Float(string='Incremento Mínimo (kg)', default=1.0)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código del conjunto de reglas debe ser único.')
    ]

    @api.constrains('min_weight_increment')
    def _check_min_increment(self):
        for record in self:
            if record.min_weight_increment < 1:
                raise ValidationError("El incremento mínimo debe ser al menos 1 kg.")

    @api.onchange('default')
    def _onchange_default(self):
        if self.default:
            others = self.search([('id', '!=', self.id), ('default', '=', True)])
            for other in others:
                other.default = False

    def unlink(self):
        Competition = self.env['iwf.competition']
        for rule in self:
            if Competition.search([('rule_set_id', '=', rule.id)], limit=1):
                raise ValidationError("No puedes eliminar este conjunto de reglas porque está en uso por una competencia.")
        return super().unlink()
