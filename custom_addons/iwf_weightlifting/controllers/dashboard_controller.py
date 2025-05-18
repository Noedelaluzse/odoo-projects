from odoo import http
from odoo.http import request

class IwfDashboardController(http.Controller):

    @http.route('/iwf/dashboard/organizer', type='http', auth='user', website=False)
    def show_dashboard(self, **kw):
        athletes = request.env['iwf.athlete'].search_count([])
        attempts = request.env['iwf.lift_attempt'].search_count([('status', '=', 'valid')])
        penalties = request.env['iwf.penalty'].search_count([('type', '!=', False)])

        values = {
            'athletes_count': athletes,
            'attempts_count': attempts,
            'active_penalties_count': penalties
        }

        return request.render('iwf_weightlifting.dashboard_organizer_template', values)