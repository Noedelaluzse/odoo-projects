from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IwfAgeGroup(models.Model):
    _name = 'iwf.age_group'
    _description = 'Grupo de Edad en Reglamentos de Halterofilia'
    _order = 'min_age'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True, copy=False)
    min_age = fields.Integer(string='Edad Mínima', required=True)
    max_age = fields.Integer(string='Edad Máxima')
    is_master = fields.Boolean(string='Es Máster', default=False)
    rule_set_id = fields.Many2one('iwf.rule_set', string='Conjunto de Reglas', required=True, ondelete='restrict')
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código del grupo de edad debe ser único.')
    ]

    @api.constrains('min_age', 'max_age')
    def _check_age_range(self):
        for record in self:
            if record.max_age and record.min_age >= record.max_age:
                raise ValidationError("La edad mínima debe ser menor que la edad máxima.")

# Esta condición compara el rango [min_age, max_age] del grupo nuevo contra los grupos existentes del mismo rule_set. Si hay cruce (overlap), lanza error.
    @api.constrains('min_age', 'max_age', 'rule_set_id')
    def _check_overlap_in_ruleset(self):
        for record in self:
            domain = [('rule_set_id', '=', record.rule_set_id.id), ('id', '!=', record.id)]
            others = self.env['iwf.age_group'].search(domain)
            for other in others:
                # Revisamos solapamiento de rangos
                if (record.max_age is None or other.min_age <= record.max_age) and \
                   (other.max_age is None or record.min_age <= other.max_age):
                    raise ValidationError("El rango de edades se superpone con otro grupo en el mismo conjunto de reglas.")
