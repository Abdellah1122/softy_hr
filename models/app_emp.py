from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AppEmp(models.Model):
    _name = 'softy.app_emp'
    _description = 'Appointment Employee'
    _rec_name = 'indemnite_id'

    # Employee relationship
    employe_id = fields.Many2one(
        'softy.employe',
        string='Employé',
        required=True,
        ondelete='cascade',
    )
    
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
    imposable = fields.Boolean(
        related='indemnite_id.imposable',
        readonly=True,
        store=True,
    )
    plafond = fields.Float(
        related='indemnite_id.plafond',
        readonly=True,
        store=True,
    )
    j = fields.Boolean(
        related='indemnite_id.j',
        readonly=True,
        store=True
    )
    
    @api.constrains('plafond', 'montant')
    def _check_amounts(self):
        for rec in self:
            if rec.plafond < 0:
                raise ValidationError("Le plafond ne peut pas être négatif.")
            if rec.montant <= 0:
                raise ValidationError("Le montant doit être supérieur à zéro.")
            if rec.plafond > 0 and rec.montant > rec.plafond:
                raise ValidationError("Le montant doit être strictement inférieur au plafond (s'il existe).")

    def name_get(self):
        """Custom display name"""
        result = []
        for record in self:
            name = f"{record.employe_id.name} - {record.indemnite_id.name} ({record.montant})"
            result.append((record.id, name))
        return result