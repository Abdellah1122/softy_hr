from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AffType(models.Model):
    _name = 'softy.aff_type'
    _description = "Type d'affiliation"
    _rec_name = 'name'
    _order = 'type_aff'

    type_aff = fields.Selection([
        ('cnss',    'Cotisation CNSS'),
        ('cipe',    "Cotisation Indemnité Perte d'Emploi"),
        ('ccimr',   'Cotisation CIMR'),
        ('ccimr7',  'Cotisation CIMR 7%'),
        ('ccimr10', 'Cotisation CIMR 10%'),
        ('ccimr6',  'Cotisation CIMR 6%'),
        ('amo',     'Cotisation Maladie Obligatoire'),
        ('cm',      'Cotisation Mutuelle'),
        ('ep',      'Épargne Retraite'),
    ], string="Code", required=True)
    
    # FIXED: Now stores proper percentage values (4.48 for CNSS, not 0.0448)
    taux = fields.Float(
        string="Taux (%)", 
        required=True,
        digits=(5, 4),  # Allow up to 4 decimal places for precision
        help="Entrez le taux en pourcentage (ex: 4.48 pour CNSS, 2.26 pour AMO)"
    )
    
    plafond = fields.Float(
        string="Plafond (MAD)", 
        required=True, 
        default=6000.00,  # Default to common Moroccan ceiling
        digits=(12, 2),
        help="Plafond mensuel en MAD (ex: 6000 pour CNSS et AMO)"
    )

    name = fields.Char(
        string="Type d'affiliation", 
        compute='_compute_name', 
        store=True
    )

    _sql_constraints = [
        ('type_aff_code_uniq',
         'unique(type_aff)',
         "Ce type d'affiliation existe déjà.")
    ]

    @api.depends('type_aff')
    def _compute_name(self):
        mapping = dict(self._fields['type_aff'].selection)
        for rec in self:
            rec.name = mapping.get(rec.type_aff) or ''

    @api.constrains('taux')
    def _check_taux(self):
        for rec in self:
            if rec.taux < 0 or rec.taux > 100:
                raise ValidationError("Le taux doit être entre 0 et 100 %.")

    @api.model
    def create_default_moroccan_rates(self):
        """Method to create typical Moroccan cotisation rates"""
        default_rates = [
            {
                'type_aff': 'cnss',
                'taux': 4.48,
                'plafond': 6000.00
            },
            {
                'type_aff': 'amo', 
                'taux': 2.26,
                'plafond': 6000.00
            },
            {
                'type_aff': 'cipe',
                'taux': 0.38,
                'plafond': 6000.00
            },
            {
                'type_aff': 'ccimr',
                'taux': 3.00,
                'plafond': 0.00  # No ceiling for CIMR
            },
            {
                'type_aff': 'ccimr6',
                'taux': 6.00,
                'plafond': 0.00
            },
            {
                'type_aff': 'ccimr7',
                'taux': 7.00,
                'plafond': 0.00
            },
            {
                'type_aff': 'ccimr10',
                'taux': 10.00,
                'plafond': 0.00
            }
        ]
        
        for rate_data in default_rates:
            existing = self.search([('type_aff', '=', rate_data['type_aff'])])
            if not existing:
                self.create(rate_data)


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
        readonly=True,
        digits=(5, 4)  # Match the precision of aff_type_id.taux
    )
    plafond = fields.Float(
        related='aff_type_id.plafond',
        string="Plafond (MAD)",
        store=True,
        readonly=True,
        digits=(12, 2)
    )

    n_aff = fields.Char(
        string="N° Affiliation",
        required=True
    )
    date_debut = fields.Date(
        string="Date Début",
        required=True,
        default=fields.Date.context_today
    )
    date_fin = fields.Date(
        string="Date Fin",
        required=True,
        help="Date d'expiration de l'affiliation"
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

