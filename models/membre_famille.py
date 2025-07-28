from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class MembreFamille(models.Model):
    _name = 'softy.membrefamille'
    _description = 'Membre de Famille'
    _rec_name = 'name'

    # Employee relationship (many family members for one employee)
    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')

    first_name = fields.Char(string='Prénom', required=True)
    last_name = fields.Char(string='Nom', required=True)
    name = fields.Char(
        string="Nom Complet",
        compute="_compute_name",
        store=True,
        readonly=True,
    )
    cin = fields.Char(string='CIN', required=True)
    date_of_birth = fields.Date(string="Date de Naissance", required=True)
    birth_city_id = fields.Many2one('softy.ville', string="Lieu de Naissance")
    street = fields.Char(string="Rue")
    phone = fields.Char(string="Téléphone")
    email = fields.Char(string="Email")

    # Additional family-specific fields
    lien_parente = fields.Selection([
        ('conjoint', 'Conjoint(e)'),
        ('enfant', 'Enfant'),
        ('pere', 'Père'),
        ('mere', 'Mère'),
        ('frere', 'Frère'),
        ('soeur', 'Sœur'),
        ('grand_pere', 'Grand-père'),
        ('grand_mere', 'Grand-mère'),
        ('oncle', 'Oncle'),
        ('tante', 'Tante'),
        ('cousin', 'Cousin(e)'),
        ('autre', 'Autre'),
    ], string='Lien de Parenté', required=True)

    genre = fields.Selection([
        ('masculin', 'Masculin'),
        ('feminin', 'Féminin'),
    ], string='Genre', required=True)

    situation_familiale = fields.Selection([
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
    ], string='Situation Familiale')

    profession = fields.Char(string='Profession')
    a_charge = fields.Boolean(string='À Charge', default=True, help="Personne à charge fiscalement")


    _sql_constraints = [
        ('cin_unique', 'unique(cin)', 'Le CIN doit être unique.'),
        ('email_format', 'check(email IS NULL OR email ~* \'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$\')', 'Format email invalide.'),
    ]

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = " ".join(filter(None, [rec.first_name, rec.last_name]))

    @api.constrains('date_of_birth')
    def _check_birth_date(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_of_birth > today:
                raise ValidationError("La date de naissance ne peut être future.")

