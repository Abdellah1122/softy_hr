try:
    from importlib.metadata import entry_points
except ImportError:
    from importlib_metadata import entry_points
    
from odoo import api, models, fields
from odoo.exceptions import ValidationError

class Societe(models.Model):
    _name = 'softy.societe'
    _description = 'Société'
    _rec_name = 'rs'

    code = fields.Char(string='Code', required=True)
    rs = fields.Char(string='Raison Sociale', required=True)
    logo=fields.Binary(string="Image")
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
    siteweb = fields.Char(string="Site web",required=True)

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
    ###################

    #relations
    banque_id = fields.Many2one(
        comodel_name='softy.banque',
        string='Banque',
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

    @api.depends('departement_ids.service_ids')
    def _compute_service_ids(self):
        for soc in self:
            # gather all services of all linked départements
            soc.service_ids = soc.departement_ids.mapped('service_ids')
                
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Le code de la société doit être unique.'),
        ('ice_uniq', 'unique(ice)', 'L’ICE doit être unique.')
    ]

    

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
