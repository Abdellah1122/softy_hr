from odoo import api, models, fields
from odoo.exceptions import ValidationError

class Societe(models.Model):
    _name = 'softy.societe'
    _description = 'Société'
    _rec_name = 'rs'

    code = fields.Char(string='Code', required=True)
    rs = fields.Char(string='Raison Sociale', required=True)
    logo = fields.Binary(string="Image")
    prefixe = fields.Char(string='Préfixe')
    libelle = fields.Char(string='Libellé Complet')
    address = fields.Char(string='Adresse', required=True)
    n_cnss = fields.Char(string='N° CNSS', required=True)
    rc = fields.Char(string='Registre de Commerce', required=True)
    patente = fields.Char(string='Patente', required=True)
    i_fiscale = fields.Char(string='Identifiant Fiscale', required=True)
    ice = fields.Char(string='ICE', required=True)
    n_cimr = fields.Char(string='N° CIMR', required=True)
    capital = fields.Float(string='Capital', required=True)

    tel = fields.Char(string='Téléphone 1', required=True)
    tel2 = fields.Char(string='Téléphone 2')
    email = fields.Char(string='Email', required=True)
    siteweb = fields.Char(string="Site web", required=True)

    nbr_heures_mois = fields.Integer(string='Nombre Heures/Mois', required=True, default=191)
    nbr_jours_mois = fields.Integer(string='Nombre Jours/Mois', required=True, default=26)
    nbr_heures_jour = fields.Integer(string='Nombre heure/Jour', required=True, default=8)

    salaire_min_h = fields.Float(string='Salaire Min Horaire', required=True)
    salaire_max_h = fields.Float(string='Salaire Max Horaire', required=True)
    salaire_min_m = fields.Float(
        string='Salaire Min Mensuel',
        compute='_compute_salaire_min_m',
        store=True,
        readonly=True
    )
    salaire_max_m = fields.Float(
        string='Salaire Max Mensuel',
        compute='_compute_salaire_max_m',
        store=True,
        readonly=True
    )

    # Relations
    banque_id = fields.Many2one(
        comodel_name='softy.banque',
        string='Banque',
        required=True,  # Make it required if every société must have a bank
    )
    ville_id = fields.Many2one(
        comodel_name='softy.ville',
        string='Ville',
    )
    departement_ids = fields.One2many(
        comodel_name='softy.departement',
        inverse_name='societe_id',
        string='Départements',
        help='Tous les départements rattachés à cette société'
    )
    service_ids = fields.Many2many(
        comodel_name='softy.service',
        string='Services',
        compute='_compute_service_ids',
        store=False,
        readonly=True,
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Le code de la société doit être unique."),
        ("ice_uniq", "unique(ice)", "L'ICE doit être unique."),
        ("banque_uniq", "unique(banque_id)", "Chaque banque ne peut être associée qu'à une seule société."),
    ]

    @api.depends('departement_ids.service_ids')
    def _compute_service_ids(self):
        for soc in self:
            # Gather all services of all linked départements
            soc.service_ids = soc.departement_ids.mapped('service_ids')

    @api.depends('salaire_min_h', 'nbr_heures_jour', 'nbr_jours_mois')
    def _compute_salaire_min_m(self):
        for rec in self:
            rec.salaire_min_m = rec.salaire_min_h * rec.nbr_heures_jour * rec.nbr_jours_mois

    @api.depends('salaire_max_h', 'nbr_heures_jour', 'nbr_jours_mois')
    def _compute_salaire_max_m(self):
        for rec in self:
            rec.salaire_max_m = rec.salaire_max_h * rec.nbr_heures_jour * rec.nbr_jours_mois

    @api.constrains('salaire_min_h', 'salaire_max_h')
    def _check_salaire(self):
        for rec in self:
            if rec.salaire_min_h > rec.salaire_max_h:
                raise ValidationError(
                    "Le salaire minimum horaire ne peut être supérieur au salaire maximum horaire."
                )

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError("Veuillez saisir un email valide.")

    @api.constrains('capital')
    def _check_capital(self):
        for rec in self:
            if rec.capital <= 0:
                raise ValidationError("Le capital doit être supérieur à zéro.")

    @api.constrains('nbr_heures_mois', 'nbr_jours_mois', 'nbr_heures_jour')
    def _check_work_time(self):
        for rec in self:
            if rec.nbr_heures_mois <= 0:
                raise ValidationError("Le nombre d'heures par mois doit être supérieur à zéro.")
            if rec.nbr_jours_mois <= 0:
                raise ValidationError("Le nombre de jours par mois doit être supérieur à zéro.")
            if rec.nbr_heures_jour <= 0:
                raise ValidationError("Le nombre d'heures par jour doit être supérieur à zéro.")

    @api.constrains('banque_id')
    def _check_unique_banque(self):
        for rec in self:
            if rec.banque_id:
                # Check if another société is already using this bank
                existing = self.search([
                    ('banque_id', '=', rec.banque_id.id),
                    ('id', '!=', rec.id)
                ])
                if existing:
                    raise ValidationError(
                        "Cette banque est déjà utilisée par une autre société: %s" % existing.rs
                    )