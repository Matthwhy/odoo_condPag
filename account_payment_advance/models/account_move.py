from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def create_payment_antecipation(self):
        antecipation_lines = []
        for move in self:
            for line in move.line_ids:
                antecipation_lines.append((0, 0, {
                    'name': line.name,
                    'amount': line.amount,
                    'payment_date': line.date,
                    'move_line_id': line.id,
                }))
        context = {
            'default_name': 'Payment Antecipation',
            'default_amount': sum(self.mapped('line_ids.amount')),
            'default_payment_date': fields.Date.today(),
            'default_antecipation_line_ids': antecipation_lines,
        }
        return {
            'name': 'Create Payment Antecipation',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.antecipation.wizard',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_antecipation_id = fields.Many2one('payment.antecipation', string="Borderô")
    to_pay_journal_id = fields.Many2one('account.journal', string="Diário (Banco)")
