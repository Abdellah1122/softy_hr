from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Banque(models.Model):
    _name = 'softy.banque'
    _description = 'Banque'
    
    code = fields.Char(string='Code Banque', required=True)
    logo=fields.Binary(string="Logo")
    name = fields.Char(string='Nom du Banque', required=True)
    libelle = fields.Char( string='Libellé Complet du Banque', required=True)
    agence = fields.Char(string='Agence', required=True)
    n_compte = fields.Char(string='N° Compte', required=True)
    lib_societe = fields.Char(string='Libelle Societé', required=True)
    ref = fields.Char(string='Reference du Banque', required=True)
    address = fields.Char(string='Address de la banque')
    email = fields.Char(string='Email Banque')
    tel = fields.Char(string='Tel Banque')
    responsable = fields.Char(string='Responsable')
    active = fields.Boolean(string='Active', default=True)


    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Le code du Service doit être unique.'),
    ]
