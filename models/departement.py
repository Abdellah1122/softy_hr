from odoo import api, models, fields
from odoo.exceptions import ValidationError

class Departement(models.Model):
    _name = 'softy.departement'
    _description = 'Departement'
    _rec_name = 'libelle'

    code = fields.Char(string='Code Departement', required=True)
    libelle = fields.Char(string='Libellé Complet du Departement')

    representant = fields.Char(string='Representant', required=True)
    agent = fields.Char(string='Agent', required=True)

    address = fields.Char(string='Adresse', required=True)

    tel = fields.Char(string='Téléphone 1', required=True)
    tel2 = fields.Char(string='Téléphone 2')
    email = fields.Char(string='Email', required=True)
    siteweb = fields.Char(string="Site web",required=True)

    rc = fields.Char(string='R.C.', required=True)
    patente = fields.Char(string='Patente', required=True)
    i_fiscale = fields.Char(string='Identifiant Fiscale', required=True)
    ice = fields.Char(string='ICE', required=True)

    n_cnss = fields.Char(string='N° CNSS', required=True)
    n_cimr = fields.Char(string='N° CIMR', required=True)
    
    capital = fields.Float(string='Capital', required=True, default=0.0)

    nbr_heures_mois = fields.Integer(string='Nombre Heures/Mois', required=True, default=160)
    nbr_jours_mois = fields.Integer(string='Nombre Jours/Mois', required=True, default=22)

    conge_1er_contrat=fields.Boolean(string="Congé à partir de la 1er Contrat ", default="False")
    conge_15=fields.Boolean(string="Congé 1.5", default="False")

    indice_pret=fields.Char(string="Indice des préts")
    ###################

    #relations
    
    ville_id = fields.Many2one(
        comodel_name='softy.ville',
        string='Ville',
    )
    societe_id=fields.Many2one(
        comodel_name='softy.societe',
        string="Departements"
    )
    service_ids = fields.One2many(
        comodel_name='softy.service',
        inverse_name='departement_id',
        string='Services / Sites',
        help='Tous les Sites rattachés à ce Departement'
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Le code du Departement doit être unique.'),
        ('ice_uniq', 'unique(ice)', 'L’ICE doit être unique.')
    ]

    @api.constrains('capital')
    def _check_capital_positive(self):
        for rec in self:
            if rec.capital < 0:
                raise ValidationError("Le capital ne peut pas être négatif.")


