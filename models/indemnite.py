from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Indemnite(models.Model):
    _name = 'softy.indemnite'
    _description = 'Indemnité'
    _rec_name = 'des_indem'

    code        = fields.Char(string="Code", required=True)
    codeir        = fields.Char(string="Code IR")
    des_indem   = fields.Char(string="Libellé", required=True)
    imposable   = fields.Boolean(string="Imposable", default=False)
    plafond     = fields.Float(string="Plafond", default=0.0)
    j           =fields.Boolean(string="Journaliere ?",required=True)
    type_ind    = fields.Selection([
        ("gain",   "Gain"),
        ("retenu", "Retenu"),
    ], string="Type", required=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', "Le code doit être unique."),
    ]

    @api.constrains('plafond')
    def _check_amounts(self):
        for rec in self:
            if rec.plafond < 0:
                raise ValidationError("Le plafond ne peut pas être négatif.")
            
