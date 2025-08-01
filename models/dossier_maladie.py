from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Dossier(models.Model):
    _name = 'softy.dossier'
    _description = 'Dossier de Maladie'
    _rec_name = 'ref'
    _order = 'date_dossier desc'

    ref = fields.Char(string="Référence Dossier", required=True)
    date_dossier = fields.Date(string="Date Dossier", required=True)
    date_ouverture = fields.Date(string="Date Ouverture", required=True)
    nature_maladie = fields.Selection([
        ("afD", "AF Digestive"),
        ("afR", "AF Rhumatismale"),
        ("afg", "AF Gynécologique"),
        ("ang", "Angines"),
        ("bronchite", "Bronchite"),
        ("cardio", "Cardio"),
        ("dermatose", "Dermatose"),
        ("gastro", "Gastro-Entérite"),
        ("grippe", "Grippe"),
        ("lombo", "Lomboradiculalgie"),
        ("malx", "MALX"),
        ("ophtalmo", "Ophtalmologie"),
        ("dentaire", "Soins Dentaires"),
        ("ulcereuse", "Ulcéreuse"),
    ], string="Nature de la maladie", required=True)

    n_envoie = fields.Char(string="N° Envoi")
    complement_info = fields.Boolean(string="Complément d'info présent")
    date_comp = fields.Date(string="Date du complément")
    complement = fields.Text(string="Détail complément")
    date_contre_visite = fields.Date(string="Date Contre-Visite")
    lieu = fields.Many2one('softy.ville', string="Lieu")
    date_rem = fields.Date(string="Date de remboursement")
    montant = fields.Float(string="Montant remboursé")
    mode_reg = fields.Selection([
        ("vir", "Virement"),
        ("cheque", "Chèque"),
        ("esp", "Espèce"),
    ], string="Mode de règlement")
    n_piece = fields.Char(string="N° de pièce")
    statu = fields.Selection([
        ("cloture", "Clôturé"),
        ("enattent", "En Attente"),
        ("encours", "En Cours"),
        ("nomd", "Non Démarré"),
    ], string="Statut", default="nomd")

    employe_id = fields.Many2one(
        'softy.employe', string="Employé", required=True, ondelete='cascade'
    )
    matricule_employe = fields.Char(
        string="Matricule", related='employe_id.matricule', readonly=True, store=True
    )
    nom_employe = fields.Char(
        string="Nom Employé", related='employe_id.name', readonly=True, store=True
    )
    cin_employe = fields.Char(
        string="CIN Employé", related='employe_id.cin', readonly=True, store=True
    )

    days_open = fields.Integer(
        string="Durée (jours)", compute="_compute_days_open", store=True
    )

    _sql_constraints = [
        ('ref_unique', 'unique(ref)', "Cette référence existe déjà."),
    ]

    @api.depends('date_dossier', 'date_ouverture')
    def _compute_days_open(self):
        for rec in self:
            if rec.date_dossier and rec.date_ouverture:
                rec.days_open = (rec.date_ouverture - rec.date_dossier).days
            else:
                rec.days_open = 0

    @api.constrains('date_dossier', 'date_ouverture')
    def _check_dates(self):
        for rec in self:
            if rec.date_ouverture < rec.date_dossier:
                raise ValidationError(
                    "La Date d'Ouverture doit être postérieure ou égale à la Date Dossier."
                )
