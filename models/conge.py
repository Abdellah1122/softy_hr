from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Conge(models.Model):
    _name = 'softy.conge'
    _description = 'Congé'
    _rec_name = 'ref_conge'

    employe_id = fields.Many2one(
        'softy.employe', string="Employé", required=True, ondelete='cascade'
    )
    ref_conge = fields.Char(string="Réf. Congé", required=True)
    motif = fields.Char(string="Motif de Congé", required=True)
    date_depart = fields.Date(string="Date de Départ", required=True)
    date_reprise = fields.Date(string="Date de Reprise", required=True)
    duree_jour = fields.Integer(
        string="Durée (jours)",
        compute='_compute_duree',
        store=True
    )
    nature_conge = fields.Selection([
        ("congeannuel", "Congé Annuel"),
        ("congededeces", "Congé de Décès"),
        ("congedemariage", "Congé de Mariage"),
        ("congedenaissance", "Congé de Naissance"),
        ("congedemaladie", "Congé de Maladie"),
        ("congesanssolde", "Congé Sans Solde"),
    ], string="Nature du Congé", required=True)

    _sql_constraints = [
        ('ref_conge_unique', 'unique(ref_conge)', "Réf. Congé doit être unique."),
    ]

    @api.depends('date_depart', 'date_reprise')
    def _compute_duree(self):
        for rec in self:
            if rec.date_depart and rec.date_reprise:
                rec.duree_jour = (rec.date_reprise - rec.date_depart).days + 1
            else:
                rec.duree_jour = 0

    @api.constrains('date_reprise', 'date_depart')
    def _check_dates(self):
        for rec in self:
            if rec.date_reprise < rec.date_depart:
                raise ValidationError(
                    "La date de reprise doit être postérieure ou égale à la date de départ."
                )
