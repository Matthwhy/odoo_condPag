{  # pylint: disable=C8101,C8103,C7902
    "name": "Rowena Antecipacao de Boletos",
    "description": "Rowena Antecipacao de Boletos",
    "author": "Trustcode",
    "category": "account",
    "version": "14.0.0.2",
    "contributors": [
        "Danimar Ribeiro <danimaribeiro@gmail.com>"
    ],
    "depends": [
        "l10n_br_account"
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/journal.xml',
        'views/account_move.xml',
        'views/payment_antecipation.xml',
        'wizard/payment_antecipation.xml',
    ],
}
