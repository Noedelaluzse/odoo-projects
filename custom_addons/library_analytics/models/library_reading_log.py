from odoo import models, fields

class LibraryReadingLog(models.Model):
    _name = 'library.reading.log'
    _description = 'Reading Log'

    book_id = fields.Many2one('library.book', string='Book', required=True)
    date = fields.Date(string='Date', default=fields.Date.today, required=True)
    pages_read = fields.Integer(string='Pages Read')
    reading_time = fields.Float(string='Reading Time (hours)')