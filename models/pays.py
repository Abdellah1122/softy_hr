from odoo import models, fields

class Pays(models.Model):
    _name = 'softy.pays'
    _description = 'Pays'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Nom du pays', required=True)