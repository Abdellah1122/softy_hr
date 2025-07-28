from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Formation(models.Model):
    _name = 'softy.formation'
    _description = 'Formation Employé'
    _rec_name = 'int_for'

    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')
    
    int_for     = fields.Char(string="Intitulé Formation", required=True)
    int_dip     = fields.Char(string="Intitulé Diplôme", required=True)
    date_debut  = fields.Date(string="Date Début", required=True)
    date_fin    = fields.Date(string="Date Fin", required=True)
    centre      = fields.Char(string="Centre de Formation", required=True)
    domain      = fields.Selection([
                    ('bureautique',   "Bureautique"),
                    ('communication', "Communication"),
                    ('comptabilite',  "Comptabilité"),
                    ('efficacite',    "Efficacité"),
                    ('finance',       "Finance"),
                    ('informatique',  "Informatique"),
                    ('integration',   "Intégration"),
                    ('langues',       "Langues"),
                  ], string="Domaine", required=True)

    _sql_constraints = [
        ('int_for_uniq', 'unique(int_for)', "Ce stage existe déjà."),
    ]

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_fin < rec.date_debut:
                raise ValidationError("La date de fin doit être postérieure ou égale à la date de début.")
