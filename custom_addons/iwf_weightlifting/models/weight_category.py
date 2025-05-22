from odoo import models, fields, api
from odoo.exceptions import ValidationError


class IwfWeightCategory(models.Model):
    _name = 'iwf.weight_category'
    _description = 'Categoría de Peso en Halterofilia'
    _order = 'max_weight'

    name = fields.Char(string='Nombre', required=False)
    code = fields.Char(string='Código', required=True, copy=False)
    min_weight = fields.Float(string='Peso Mínimo (kg)')
    max_weight = fields.Float(string='Peso Máximo (kg)', required=True)
    is_super_heavy = fields.Boolean(string='¿Es Súper Pesada?', default=False)
    gender = fields.Selection([
        ('male', 'Masculino'),
        ('female', 'Femenino')
    ], string='Género', required=True)
    age_group_ids = fields.Many2many('iwf.age_group', string='Grupos de Edad')
    rule_set_id = fields.Many2one('iwf.rule_set', string='Conjunto de Reglas', required=True, ondelete='restrict')
    active = fields.Boolean(string='Activo', default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código de la categoría de peso debe ser único.')
    ]

    @api.constrains('min_weight', 'max_weight', 'gender', 'rule_set_id')
    def _check_overlap(self):
        for record in self:
            domain = [
                ('rule_set_id', '=', record.rule_set_id.id),
                ('gender', '=', record.gender),
                ('id', '!=', record.id)
            ]
            others = self.env['iwf.weight_category'].search(domain)
            for other in others:
                if (record.max_weight > (other.min_weight or 0)) and \
                ((record.min_weight or 0) < other.max_weight):
                    raise ValidationError("El rango de peso se superpone con otra categoría del mismo género y conjunto de reglas.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                max_w = vals.get('max_weight')
                name = f"+{int(max_w)} kg" if vals.get('is_super_heavy') else f"–{int(max_w)} kg"
                vals['name'] = name
        return super().create(vals_list)