from odoo import api, fields, models


class PaymentAntecipationLine(models.Model):
    _name = 'payment.antecipation.line'
    _description = 'Payment Antecipation Line'

    name = fields.Char(string='Name', required=True)

    payment_antecipation_id = fields.Many2one('payment.antecipation', string='Payment Antecipation')
    move_line_id = fields.Many2one('account.move.line', string='Move Line')
    
    partner_id = fields.Many2one('res.partner', related="move_line_id.partner_id")
    account_id = fields.Many2one('account.account', related="move_line_id.account_id")
    date_maturity = fields.Date(related="move_line_id.date_maturity") 
    currency_id = fields.Many2one('res.currency', related="move_line_id.currency_id")
    move_id = fields.Many2one('account.move', related="move_line_id.move_id")

    amount_residual = fields.Monetary(related='move_line_id.amount_residual')
    reconciled = fields.Boolean(related='move_line_id.reconciled', string="Pago")


class PaymentAntecipation(models.Model):
    _name = 'payment.antecipation'
    _description = 'Antecipação de Boletos'

    name = fields.Char(string='N. Borderô', required=True, readonly=True, unique=True)

    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Diário a Receber', domain="[('type', '=', 'bank')]", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, related='journal_id.currency_id')
    expense_account_id = fields.Many2one('account.account', string="Conta Contábil Despesas")

    payment_date = fields.Date(string='Data', required=True)
    amount = fields.Monetary(string='Total Boletos', required=True, readonly=True)

    desagio = fields.Monetary(string="(-) Deságio", readonly=True)
    ad_valorem = fields.Monetary(string="(-) Ad Valorem", readonly=True)
    fees = fields.Monetary(string="(-) Tarifas", readonly=True)
    taxes = fields.Monetary(string="(-) Impostos Diversos", readonly=True)
    retention = fields.Monetary(string="(+) Impostos Retidos", readonly=True)

    final_amount = fields.Monetary(string="Valor a Pagar", readonly=True)
    
    description = fields.Text(string='Observações')

    antecipation_line_ids = fields.One2many('payment.antecipation.line', 'payment_antecipation_id', string='Antecipation Lines', readonly=True)
