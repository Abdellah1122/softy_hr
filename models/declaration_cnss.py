from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class DeclarationCNSS(models.Model):
    _name = 'softy.declarationcnss'
    _description = 'Declaration CNSS'
    _rec_name = 'display_name'
    _order = 'annee desc, mois desc'

    bulletin_id = fields.Many2one(
        comodel_name="softy.bulletin",
        string="Bulletin de paie",
        required=False,  # Changed from True
        ondelete='set null'  # Changed from 'cascade'
    )

    # CHANGED: Convert all related fields to regular stored fields
    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string='Employé',
        store=True,
        readonly=True
    )

    n_aff = fields.Char(
        string="N° Affiliation CNSS",
        compute='_compute_affiliation_cnss',
        store=True,
        readonly=True
    )
    
    date_aff = fields.Date(
        string="Date Affiliation",
        compute='_compute_affiliation_cnss',
        store=True,
        readonly=True
    )
    
    date_fin_aff = fields.Date(
        string="Date Fin Affiliation",
        compute='_compute_affiliation_cnss',
        store=True,
        readonly=True
    )

    matricule = fields.Char(
        string="Matricule",
        store=True,
        readonly=True
    )

    nom_complet = fields.Char(
        string="Nom complet",
        store=True,
        readonly=True
    )

    salaire = fields.Float(
        string="Salaire Brut Imposable",
        store=True,
        readonly=True,
        digits=(10, 2)
    )

    cotisation = fields.Float(
        string="Cotisation CNSS",
        compute='_compute_cotisation_cnss',
        store=True,
        readonly=True,
        digits=(10, 2)
    )

    situation = fields.Selection([
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
        ('pacse', 'Pacsé(e)'),
    ], string="Situation Familiale",
        store=True,
        readonly=True
    )

    type_aff = fields.Many2one(
        comodel_name="softy.aff_type",
        string="Type Affiliation CNSS",
        compute='_compute_affiliation_cnss',
        store=True,
        readonly=True
    )

    annee = fields.Integer(
        string="Année",
        store=True,
        readonly=True
    )
    
    mois = fields.Selection(
        selection=[(str(i), f"{i:02d}") for i in range(1,13)],
        string='Mois',
        store=True,
        readonly=True
    )

    societe_id = fields.Many2one(
        comodel_name="softy.societe",
        string='Société',
        store=True,
        readonly=True
    )

    departement_id = fields.Many2one(
        comodel_name="softy.departement",
        string='Département',
        store=True,
        readonly=True
    )

    service_id = fields.Many2one(
        comodel_name="softy.service",
        string='Service',
        store=True,
        readonly=True
    )

    # CHANGED: Convert from related field to regular stored field
    jours_travaille = fields.Integer(
        string="Jours Travaillés",
        store=True,
        readonly=True
    )

    display_name = fields.Char(
        string="Nom d'affichage",
        compute='_compute_display_name',
        store=True
    )

    taux_cnss = fields.Float(
        string="Taux CNSS (%)",
        compute='_compute_affiliation_cnss',
        store=True,
        readonly=True,
        digits=(5, 2)
    )

    _sql_constraints = [
        ('unique_declaration_bulletin', 
         'UNIQUE(bulletin_id)', 
         "Une déclaration CNSS existe déjà pour ce bulletin."),
    ]

    @api.model
    def create(self, vals):
        """Override create to populate fields from bulletin when declaration is created"""
        if 'bulletin_id' in vals and vals['bulletin_id']:
            bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
            if bulletin.exists():
                # Populate all the fields from bulletin at creation time
                vals.update({
                    'employe_id': bulletin.employe_id.id if bulletin.employe_id else False,
                    'matricule': bulletin.employe_id.matricule if bulletin.employe_id else False,
                    'nom_complet': bulletin.employe_id.name if bulletin.employe_id else False,
                    'salaire': bulletin.salaire_brut_imp,
                    'situation': bulletin.employe_id.situation_familiale if bulletin.employe_id else False,
                    'annee': bulletin.annee,
                    'mois': bulletin.mois,
                    'societe_id': bulletin.societe_id.id if bulletin.societe_id else False,
                    'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                    'service_id': bulletin.service_id.id if bulletin.service_id else False,
                    'jours_travaille': bulletin.nbr_j or 0,  # From bulletin.nbr_j instead of bulletin.pointagem_id.nbr_j
                })
        
        return super().create(vals)

    def write(self, vals):
        """Override write to update fields when bulletin changes"""
        if 'bulletin_id' in vals:
            if vals['bulletin_id']:
                bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
                if bulletin.exists():
                    # Update all the fields from new bulletin
                    vals.update({
                        'employe_id': bulletin.employe_id.id if bulletin.employe_id else False,
                        'matricule': bulletin.employe_id.matricule if bulletin.employe_id else False,
                        'nom_complet': bulletin.employe_id.name if bulletin.employe_id else False,
                        'salaire': bulletin.salaire_brut_imp,
                        'situation': bulletin.employe_id.situation_familiale if bulletin.employe_id else False,
                        'annee': bulletin.annee,
                        'mois': bulletin.mois,
                        'societe_id': bulletin.societe_id.id if bulletin.societe_id else False,
                        'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                        'service_id': bulletin.service_id.id if bulletin.service_id else False,
                        'jours_travaille': bulletin.nbr_j or 0,
                    })
            # If bulletin_id is set to False/None, keep existing stored values
        
        return super().write(vals)

    @api.depends('employe_id')  # Changed dependency from 'employe_id.affiliation_ids'
    def _compute_affiliation_cnss(self):
        for rec in self:
            cnss_affiliation = None
            
            if rec.employe_id and rec.employe_id.affiliation_ids:
                for affiliation in rec.employe_id.affiliation_ids:
                    if affiliation.aff_type_id.type_aff == 'cnss':
                        cnss_affiliation = affiliation
                        break
            
            if cnss_affiliation:
                rec.n_aff = cnss_affiliation.n_aff
                rec.date_aff = cnss_affiliation.date_debut
                rec.date_fin_aff = cnss_affiliation.date_fin
                rec.type_aff = cnss_affiliation.aff_type_id.id
                rec.taux_cnss = cnss_affiliation.aff_type_id.taux
            else:
                rec.n_aff = False
                rec.date_aff = False
                rec.date_fin_aff = False
                rec.type_aff = False
                rec.taux_cnss = 0.0

    @api.depends('salaire', 'taux_cnss')
    def _compute_cotisation_cnss(self):
        for rec in self:
            if rec.taux_cnss > 0:
                # CNSS has a ceiling/plafond, get it from the affiliation type
                plafond = rec.type_aff.plafond if rec.type_aff else 6000.0
                salaire_plafonné = min(rec.salaire, plafond) if plafond > 0 else rec.salaire
                rec.cotisation = salaire_plafonné * (rec.taux_cnss / 100.0)
            else:
                rec.cotisation = 0.0

    @api.depends('nom_complet', 'annee', 'mois')
    def _compute_display_name(self):
        for rec in self:
            if rec.nom_complet and rec.annee and rec.mois:
                rec.display_name = f"CNSS {rec.nom_complet} - {rec.mois}/{rec.annee}"
            elif rec.nom_complet:
                rec.display_name = f"CNSS {rec.nom_complet} - (Bulletin supprimé)"
            else:
                rec.display_name = "Déclaration CNSS orpheline"

    @api.model
    def generate_declarations_for_period(self, annee, mois=None):
        """Génère les déclarations CNSS pour une période donnée"""
        domain = [('annee', '=', annee)]
        
        if mois:
            domain.append(('mois', '=', str(mois)))
        
        bulletins = self.env['softy.bulletin'].search(domain)
        _logger.info(f"Found {len(bulletins)} bulletins for year {annee}")
        
        # Debug: Check each bulletin for CNSS affiliations
        bulletins_cnss = []
        for bulletin in bulletins:
            employee = bulletin.employe_id
            if employee and employee.affiliation_ids:
                cnss_affiliations = employee.affiliation_ids.filtered(
                    lambda aff: aff.aff_type_id and aff.aff_type_id.type_aff == 'cnss'
                )
                _logger.info(f"Employee {employee.name}: {len(cnss_affiliations)} CNSS affiliations found")
                if cnss_affiliations:
                    bulletins_cnss.append(bulletin)
                else:
                    _logger.info(f"Employee {employee.name}: No CNSS affiliations")
            else:
                _logger.info(f"Employee {employee.name if employee else 'Unknown'}: No affiliations at all")
        
        _logger.info(f"Bulletins with CNSS affiliations: {len(bulletins_cnss)}")
        
        # Check for existing declarations - updated to handle null bulletin_id
        bulletins_sans_declaration = []
        for bulletin in bulletins_cnss:
            existing = self.search([('bulletin_id', '=', bulletin.id)])
            if not existing:
                bulletins_sans_declaration.append(bulletin)
            else:
                _logger.info(f"Declaration already exists for bulletin {bulletin.id}")
        
        _logger.info(f"Bulletins without declarations: {len(bulletins_sans_declaration)}")
        
        declarations_created = []
        for bulletin in bulletins_sans_declaration:
            try:
                declaration = self.create({'bulletin_id': bulletin.id})
                declarations_created.append(declaration)
                _logger.info(f"Created declaration for bulletin {bulletin.id}")
            except Exception as e:
                _logger.error(f"Error creating declaration for bulletin {bulletin.id}: {str(e)}")
                continue
        
        _logger.info(f"Total declarations created: {len(declarations_created)}")
        return declarations_created