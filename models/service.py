from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Service(models.Model):
    _name = 'softy.service'
    _description = 'Service'
    _rec_name = 'name'

    code = fields.Char(string='Code Service', required=True)
    name = fields.Char(string='Nom du Service', required=True)
    libelle = fields.Char( string='Libellé Complet du Service', required=True)
    ref = fields.Char(string='Référence Service', required=True)

    departement_id = fields.Many2one(
        'softy.departement',
        string='Département',
        required=True,
        ondelete='cascade'
    )
    societe_id = fields.Many2one(
            'softy.societe',
            string="Société",
            related='departement_id.societe_id',
            store=True,
            readonly=True
        )
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Le code du Service doit être unique.'),
    ]
