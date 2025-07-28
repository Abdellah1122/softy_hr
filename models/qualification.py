from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Qualification(models.Model):
    _name = 'softy.qualification'
    _description = 'Qualification'
    _rec_name = 'qualification'
    
    code = fields.Char(string='Code Qualification', required=True)
    qualification = fields.Char(string="Qualification", required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Le code du Service doit être unique.'),
    ]
