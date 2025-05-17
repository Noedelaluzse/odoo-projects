from odoo import models, fields, api



class GradesEvaluation(models.Model):
  _name ="grades.evaluation"
  _description = "Grades Evaluation"

  name = fields.Char(string="Name")
  date = fields.Date(string="Date")
  observations = fields.Text(string="Observations")
  course_id = fields.Many2one('grades.course', string="Course", ondelete="cascade")
  grade_ids = fields.One2many('grades.grade', 'evaluation_id', string='Grades', readonly=True)
  

  @api.model_create_multi
  def create(self, vals):
    result = super(GradesEvaluation, self).create(vals)
    for student in result.course_id.students_ids:
      self.env['grades.grade'].create(
        {
          'evaluation_id': result.id,
          'date': fields.Date.today(), 
          'student_id': student.id
        }
      )
    return result