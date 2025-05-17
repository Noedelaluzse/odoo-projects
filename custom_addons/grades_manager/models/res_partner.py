from odoo import models, fields


class ResPartner(models.Model):
  _inherit = 'res.partner' # Inherit the res.partner model
  
  is_teacher = fields.Boolean(string='Is Teacher') # Add a boolean field to indicate if the partner is a teacher
  is_freelance = fields.Boolean(string='Is Freelance') # Add a boolean field to indicate if the partner is a freelance
  is_student = fields.Boolean(string='Is Student')
  vat = fields.Char(required=True, copy=False)

  def unlink(self):
    for partner in self:
      if partner.email == 'noedelaluz@michysoft.com':
        courses = self.env['grades.course'].search([('teacher_id', '=', partner.id)])
        secondary_teacher = self.env['res.partner'].search([('email', '=','adrian.simei@gmail.com')])
        courses.write(
          {
            'teacher_id': secondary_teacher.id
          }
        )
    result = super(ResPartner, self).unlink()
    return result
  
  def copy(self, default=None):
    default = default or {}
    if self.is_teacher:
      default['name'] = 'Teacher'
    elif self.is_student:
      default['name'] = 'Student'

    res = super(ResPartner, self).copy(default)
    return res