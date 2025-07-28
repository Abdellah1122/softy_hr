from odoo import models, fields

class Ville(models.Model):
    _name = 'softy.ville'
    _description = 'Ville'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Nom de la ville', required=True)
    code_postale = fields.Char(string='Code Postal', required=True)
    pays_id = fields.Many2one(
        comodel_name='softy.pays',
        string='Pays',
        required=True,
        ondelete='cascade',
        help='Le pays auquel appartient cette ville'
    )
