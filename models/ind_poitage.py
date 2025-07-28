from odoo import api, fields, models
from odoo.exceptions import ValidationError

class IndPoint(models.Model):
    _name = 'softy.ind_point'
    _description = 'Indemnité de pointage'
    _rec_name = 'indemnite_id'

    indemnite_id = fields.Many2one(
        'softy.indemnite', 
        string='Indemnité', 
        required=True, 
        ondelete='cascade',
    )
    montant = fields.Float(
        string='Montant', 
        required=True, 
        default=0.0,
    )
    imposable   = fields.Boolean(related='indemnite_id.imposable',readonly=True,store=True,)
    plafond     = fields.Float(related='indemnite_id.plafond',readonly=True,store=True,)
    j           =fields.Boolean(related='indemnite_id.j',readonly=True,store=True)
    
    @api.constrains('plafond', 'montant')
    def _check_amounts(self):
        for rec in self:
            if rec.plafond < 0:
                raise ValidationError("Le plafond ne peut pas être négatif.")
            if rec.montant <= 0:
                raise ValidationError("Le montant doit être supérieur à zéro.")
            if rec.plafond > 0 and rec.montant >= rec.plafond:
                raise ValidationError("Le montant doit être strictement inférieur au plafond (s'il existe).")

