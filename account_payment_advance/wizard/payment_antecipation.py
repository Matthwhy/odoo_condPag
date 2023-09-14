from datetime import date
from odoo import fields, models, api


class PaymentAntecipationWizard(models.TransientModel):
    _name = 'payment.antecipation.wizard'
    _description = 'Payment Antecipation Wizard'

    def _get_default_amount(self):
        lines = self.env['account.move.line'].browse(self.env.context.get('active_ids'))
        return sum([
            x.amount_residual for x in lines
            if x.account_id.user_type_id.type == 'receivable' and not x.reconciled and not x.payment_antecipation_id])

    name = fields.Char(string='N. Borderô', required=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Diário a Receber', domain="[('type', '=', 'bank')]")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, related='journal_id.currency_id')
    expense_account_id = fields.Many2one('account.account', string="Conta Contábil Despesas")

    payment_date = fields.Date(string='Data', required=True)
    amount = fields.Monetary(string='Total Boletos', required=True, readonly=True, default=_get_default_amount)

    desagio = fields.Monetary(string="(-) Deságio")
    ad_valorem = fields.Monetary(string="(-) Ad Valorem")
    fees = fields.Monetary(string="(-) Tarifas")
    taxes = fields.Monetary(string="(-) Impostos Diversos")
    retention = fields.Monetary(string="(+) Impostos Retidos")

    final_amount = fields.Monetary(string="Valor a Pagar", store=True, compute='_compute_final_amount')
    
    description = fields.Text(string='Observações')

    @api.depends('amount', 'desagio', 'ad_valorem', 'fees', 'taxes', 'retention')
    def _compute_final_amount(self):
        for item in self:
            item.final_amount = (item.amount + item.retention) - item.desagio - item.ad_valorem - item.fees - item.taxes


    def _create_account_move(self, antecipation_id):
        journal = self.env.ref('account_payment_advance.journal_antecipation')

        ref = 'Borderô: %s' % self.name
        currency = journal.currency_id or journal.company_id.currency_id

        move = self.env['account.move'].create({
            'name': '/',
            'journal_id': journal.id,
            'company_id': journal.company_id.id,
            'date': date.today(),
            'ref': ref,
            'currency_id': currency.id,
            'move_type': 'entry',
        })
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        credit_aml_dict = {
            'name': ref,
            'move_id': move.id,
            'debit': 0.0,
            'credit': antecipation_id.amount,
            'account_id': journal.default_account_id.id,
        }
        debit_aml_dict = {
            'name': ref + " - Valor Pago",
            'move_id': move.id,
            'debit': antecipation_id.final_amount,
            'credit': 0.0,
            'account_id': journal.suspense_account_id.id,
        }
        fee_aml_dict = {
            'name': ref + " - Taxas",
            'move_id': move.id,
            'debit': antecipation_id.desagio + antecipation_id.ad_valorem + antecipation_id.fees + antecipation_id.taxes - antecipation_id.retention,
            'credit': 0.0,
            'account_id': antecipation_id.expense_account_id.id,
        }
        aml_obj.create(credit_aml_dict)
        aml_obj.create(debit_aml_dict)
        aml_obj.create(fee_aml_dict)
        move.action_post()
        return move

    def create_payment_antecipation(self):
        line_ids = self.env.context.get('active_ids')
        model = self.env.context.get('active_model')
        if model != 'account.move.line':
            return

        payment_antecipation = self.env['payment.antecipation'].create({
            'name': self.name,
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'expense_account_id': self.expense_account_id.id,
            'payment_date': self.payment_date,
            'amount': self.amount,
            'desagio': self.desagio,
            'ad_valorem': self.ad_valorem,
            'fees': self.fees,
            'taxes': self.taxes,
            'retention': self.retention,
            'final_amount': self.final_amount,
            'description': self.description,
        })
        antecipation_lines = []
        for line in self.env['account.move.line'].browse(line_ids):
            if line.reconciled:
                continue
            if line.account_id.user_type_id.type != 'receivable':
                continue
            if line.payment_antecipation_id:
                continue
            line.payment_antecipation_id = payment_antecipation.id
            line.to_pay_journal_id = payment_antecipation.journal_id.id
            antecipation_lines.append((0, 0, {
                'name': line.name,
                'move_line_id': line.id,
            }))

        payment_antecipation.antecipation_line_ids = antecipation_lines

        self._create_account_move(payment_antecipation)

        _, act_id = self.env['ir.model.data'].get_object_reference(
                'account_payment_advance', 'action_payment_antecipation')
        vals = self.env['ir.actions.act_window'].browse(act_id).read()[0]
        vals['res_id'] = payment_antecipation.id
        return vals

