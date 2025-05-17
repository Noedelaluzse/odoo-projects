from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LibrarBook(models.Model):
  _name = 'library.book'
  _description = 'Library Book'

  name = fields.Char(string='Title', required=True)
  author = fields.Char(string='Author')
  isbn = fields.Char(string='ISBN')
  description = fields.Text(string='Description')
  cover = fields.Binary(string='Cover')
  total_copies = fields.Integer(string='Total Copies', required=True, default=1)
  available_copies = fields.Integer(string='Available Copies', compute='_compute_available_copies', store=True) #available_copies = total_copies - número de rentas activas (state == 'ongoing')
  rental_ids = fields.One2many('library.rental', 'book_id', 'Rentals')
  

  @api.depends('rental_ids.state')
  def _compute_available_copies(self):
    for book in self:
      ongoing_rentals = len(book.rental_ids.filtered(lambda r: r.state == 'ongoing'))
      book.available_copies = book.total_copies - ongoing_rentals
  