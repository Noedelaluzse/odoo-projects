from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryRental(models.Model): 
  _name = 'library.rental'
  _description = 'Library Rental'

  book_id = fields.Many2one('library.book', string='Book', required=True)
  renter_id = fields.Many2one('res.partner', string='Renter', required=True, domain=[('customer_rank', '>', 0)])
  rental_date = fields.Date(string='Rental Date', default=fields.Date.today, required=True)
  return_date = fields.Date(string='Return Date')
  state = fields.Selection(
    [('ongoing', 'Ongoing'), ('returned', 'Returned')],
    string='State', default='ongoing', required=True  
  )


  @api.constrains('book_id')
  def _check_book_availability(self):
    for record in self:
      if record.book_id and record.book_id.available_copies <= 0:
        raise ValidationError("No available copies for this book.")
