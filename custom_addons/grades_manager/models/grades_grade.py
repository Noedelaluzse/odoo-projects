from odoo import models, fields, api
from odoo.exceptions import ValidationError

class GradesGrade(models.Model):
  _name = 'grades.grade'
  _description = 'Grades Grade'

  student_id = fields.Many2one('res.partner', string='Student')
  value = fields.Integer(string='Value')
  date = fields.Date(string='Date', default=fields.Date.today())
  evaluation_id = fields.Many2one(
      string='Evaluation',
      comodel_name='grades.evaluation')
  
  @api.constrains('value')
  def check_value(self):
    for grade in self:
      if grade.value < 0 or grade.value > 10:
        raise ValidationError('The grade has to be from 0 to 10')