from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Affiliation(models.Model):
    _name = 'softy.affiliation'
    _description = 'Affiliation'
    _rec_name = 'n_aff'
    _order = 'date_debut desc'

    employe_id = fields.Many2one(
        'softy.employe',
        string="Employé",
        required=True,
        ondelete='cascade'
    )
    aff_type_id = fields.Many2one(
        'softy.aff_type',
        string="Type d'affiliation",
        required=True,
        ondelete='restrict'
    )

    # Related fields for legacy views & badges
    type_aff = fields.Selection(
        related='aff_type_id.type_aff',
        string="Code Type",
        store=True,
        readonly=True
    )
    taux = fields.Float(
        related='aff_type_id.taux',
        string="Taux (%)",
        store=True,
        readonly=True
    )

    n_aff = fields.Char(
        string="N° Affiliation",
        required=True
    )
    date_debut = fields.Date(
        string="Date Début",
        required=True
    )
    date_fin = fields.Date(
        string="Date Fin",
        required=True
    )
    diffusion_info = fields.Boolean(
        string="Autoriser diffusion information",
        default=False
    )

    _sql_constraints = [
        ('n_aff_uniq', 'unique(n_aff)', "Ce numéro d'affiliation existe déjà.")
    ]

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_fin and rec.date_debut and rec.date_fin < rec.date_debut:
                raise ValidationError(
                    "La date de fin doit être postérieure ou égale à la date de début."
                )
