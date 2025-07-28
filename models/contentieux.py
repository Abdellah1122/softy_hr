from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class Contentieux(models.Model):
    _name = 'softy.contentieux'
    _description = 'Contentieux'
    _rec_name = 'ref_dossier'

    employe_id = fields.Many2one(
        'softy.employe', string="Employé", required=True, ondelete='cascade'
    )
    ref_dossier = fields.Char(string="Réf. Dossier", required=True)
    n_dossier = fields.Char(string="N° Dossier", required=True)
    date_dossier = fields.Date(string="Date du Dossier", required=True)
    date_ouverture = fields.Date(string="Date d'Ouverture", required=True)
    type_contentieux = fields.Selection([
        ("accident_travail","Accident de Travail"),
        ("sanction_disciplinaire","Sanction Disciplinaire"),
        ("solde_compte","Solde de Tout Compte"),
    ], string="Type de Contentieux", required=True)
    statut_contentieux = fields.Selection([
        ("cloture","Clôturé"),
        ("enattente","En Attente"),
        ("encours","En Cours"),
        ("nondemarer","Non Démarré"),
    ], string="Statut", required=True)

    duree_jours = fields.Integer(
        string="Durée (jours)", compute="_compute_duree", store=True
    )

    _sql_constraints = [
        ('ref_dossier_unique', 'unique(ref_dossier)', "Réf. Dossier must be unique."),
        ('n_dossier_unique', 'unique(n_dossier)', "N° Dossier must be unique."),
    ]

    @api.depends('date_dossier', 'date_ouverture')
    def _compute_duree(self):
        for rec in self:
            if rec.date_dossier and rec.date_ouverture:
                rec.duree_jours = (rec.date_ouverture - rec.date_dossier).days
            else:
                rec.duree_jours = 0

    @api.constrains('date_ouverture', 'date_dossier')
    def _check_dates(self):
        for rec in self:
            if rec.date_ouverture < rec.date_dossier:
                raise ValidationError(
                    "La date d'ouverture doit être postérieure ou égale à la date du dossier."
                )
