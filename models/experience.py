# File: models/experience.py
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Experience(models.Model):
    _name = 'softy.experience'
    _description = 'Expérience'
    _rec_name = 'sec_activite'

    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')
    
    soc            = fields.Char(string="Société", required=True)
    date_debut     = fields.Date(string="Date de Début", required=True)
    date_fin       = fields.Date(string="Date de Fin", required=True)
    motif_depart   = fields.Char(string="Motif de Départ")
    sec_activite   = fields.Selection([
                        ('administration',   'Administration'),
                        ('agriculture',      'Agriculture'),
                        ('batimenttp',       'Bâtiment & TP'),
                        ('distribution',     'Distribution'),
                        ('finance',          'Finance – Banque'),
                        ('industrie',        'Industrie'),
                        ('metallurgie',      'Métallurgie'),
                        ('services',         'Services'),
                        ('transport',        'Transport'),
                    ], string="Secteur d'Activité", required=True)
    degre_maitrise = fields.Selection([
                        ('bonne',        'Bonne'),
                        ('excellente',   'Excellente'),
                        ('indeterminee', 'Indéterminée'),
                        ('insuffisante', 'Insuffisante'),
                        ('moyenne',      'Moyenne'),
                    ], string="Degré de Maîtrise", required=True)

    _sql_constraints = [
        ('sec_activite_unique', 'unique(soc, date_debut, date_fin)',
         "Cette expérience existe déjà pour ces dates."),
    ]

    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        for rec in self:
            if rec.date_fin < rec.date_debut:
                raise ValidationError("La date de fin doit être postérieure ou égale à la date de début.")
