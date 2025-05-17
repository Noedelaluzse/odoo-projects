from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GradesCourse(models.Model):
  _name = 'grades.course'
  _description = 'Grades Course'
  # _order = 'name'
  # _rec_name = 'name'

  def _default_teacher_id(self):
      teacher = self.env['res.partner'].search([
          ('is_teacher', '=', True),
          ('email', '=', 'noedelaluz@michysoft.com')
      ], limit=1)
      return teacher.id if teacher else False

  name = fields.Char(string='Name')
  student_qty = fields.Integer(string='Student Quantity', compute="_compute_student_qty", store=True) #readonly=True
  grades_average = fields.Float(string='Grades Average')
  description = fields.Text(string='Description')
  is_active = fields.Boolean(string='Is Active')
  course_start = fields.Date(string='Course Start', default=fields.Date.today())
  course_end = fields.Date(string='Course End')
  last_evaluation = fields.Date(string='Last Evaluation', compute='_computed_last_evaluation', store=True)
  course_image = fields.Binary(string='Course Image')
  course_shift = fields.Selection([('day','Day'), ('night','Night')], string='Course Shift')
  teacher_id = fields.Many2one('res.partner', string='Teacher', domain="[('is_teacher', '=', True)]", default=_default_teacher_id) # ondelete='restrict' 'restrict', 'cascade'
  teacher_email = fields.Char(related='teacher_id.email', store=True) # No es bidireccional, osea en el modelo original "Teacher" no se modifica el valor. el cambio es unicamente en el modelo de Course
  evalutation_ids = fields.One2many('grades.evaluation', 'course_id', string='Evaluations')
  students_ids = fields.Many2many('res.partner', 'grades_course_students_rel', string="Students")
  state = fields.Selection([('register', 'Register'), ('in_progress', 'In progress'), ('finished', 'Finished')], string='State', default='register')
  invalid_dates = fields.Boolean(string="Invalid dates")
  type = fields.Selection([('basic', 'Basic'), ('advanced', 'Advanced')], string='Type', default='basic')

  def action_advanced_course_wizard(self):
      return {
          "type": "ir.actions.act_window",
          "name": "Create advanced course",
          "res_model": "advanced.course.wizard",
          "view_mode":"form",
          "target": "new"
      }
  
  def write(self, vals):
     if vals and 'evalutation_ids' in vals and not self.students_ids:
        raise ValidationError('There are no students for this course')
     result = super(GradesCourse, self).write(vals)
     return result
  
#   @api.onchange('course_start', 'course_end')
#   def onchange_dates(self):
#     if self.course_start >= self.course_end or self.course_end <= self.course_start:
#         self.invalid_dates = True
#     else:
#        self.invalid_dates = False
  @api.onchange('course_start', 'course_end')
  def onchange_dates(self):
        if self.course_start and self.course_end:
            if self.course_start >= self.course_end:
                self.invalid_dates = True
            else:
                self.invalid_dates = False
        else:
            self.invalid_dates = False  # O True si consideras inválido que falten fechas
    
#   @api.depends('evalutation_ids.date')
#   def _computed_last_evaluation(self):
#      for course in self:
#         evaluation = course.evalutation_ids[-1]
#         course.last_evaluation = evaluation.date
  @api.depends('evalutation_ids.date')
  def _computed_last_evaluation(self):
    for course in self:
        if course.evalutation_ids:
            course.last_evaluation = course.evalutation_ids[-1].date
        else:
            course.last_evaluation = False  # O puedes usar None si prefieres
  
  @api.depends('students_ids')
  def _compute_student_qty(self):
     for course in self:
        course.student_qty = len(course.students_ids)