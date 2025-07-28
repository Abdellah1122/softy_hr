from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class DeclarationCIMR(models.Model):
    _name = 'softy.declarationcimr'
    _description = 'Declaration CIMR'
    _rec_name = 'display_name'
    _order = 'annee desc, trimestre desc'

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
        string="N° Affiliation CIMR",
        compute='_compute_affiliation_cimr',
        store=True,
        readonly=True
    )
    
    date_aff = fields.Date(
        string="Date Affiliation",
        compute='_compute_affiliation_cimr',
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
        string="Cotisation CIMR",
        compute='_compute_cotisation_cimr',
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
        string="Type Affiliation CIMR",
        compute='_compute_affiliation_cimr',
        store=True,
        readonly=True
    )

    annee = fields.Integer(
        string="Année",
        store=True,
        readonly=True
    )

    trimestre = fields.Selection([
        ('1', 'T1 (Jan-Mar)'),
        ('2', 'T2 (Avr-Juin)'),
        ('3', 'T3 (Juil-Sep)'),
        ('4', 'T4 (Oct-Déc)')
    ], string="Trimestre", compute='_compute_trimestre', store=True, readonly=True)

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

    display_name = fields.Char(
        string="Nom d'affichage",
        compute='_compute_display_name',
        store=True
    )

    taux_cimr = fields.Float(
        string="Taux CIMR (%)",
        compute='_compute_affiliation_cimr',
        store=True,
        readonly=True,
        digits=(5, 2)
    )

    _sql_constraints = [
        ('unique_declaration_bulletin', 
         'UNIQUE(bulletin_id)', 
         "Une déclaration CIMR existe déjà pour ce bulletin."),
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
                    })
            # If bulletin_id is set to False/None, keep existing stored values
        
        return super().write(vals)

    @api.depends('employe_id')  # Changed dependency
    def _compute_affiliation_cimr(self):
        for rec in self:
            cimr_affiliation = None
            
            if rec.employe_id and rec.employe_id.affiliation_ids:
                for affiliation in rec.employe_id.affiliation_ids:
                    if affiliation.aff_type_id.type_aff in ['ccimr', 'ccimr6', 'ccimr7', 'ccimr10']:
                        cimr_affiliation = affiliation
                        break
            
            if cimr_affiliation:
                rec.n_aff = cimr_affiliation.n_aff
                rec.date_aff = cimr_affiliation.date_debut
                rec.type_aff = cimr_affiliation.aff_type_id.id
                rec.taux_cimr = cimr_affiliation.aff_type_id.taux
            else:
                rec.n_aff = False
                rec.date_aff = False
                rec.type_aff = False
                rec.taux_cimr = 0.0

    @api.depends('salaire', 'taux_cimr')
    def _compute_cotisation_cimr(self):
        for rec in self:
            if rec.taux_cimr > 0:
                rec.cotisation = rec.salaire * (rec.taux_cimr / 100.0)
            else:
                rec.cotisation = 0.0

    @api.depends('mois')
    def _compute_trimestre(self):
        for rec in self:
            if rec.mois:
                mois_int = int(rec.mois)
                if 1 <= mois_int <= 3:
                    rec.trimestre = '1'
                elif 4 <= mois_int <= 6:
                    rec.trimestre = '2'
                elif 7 <= mois_int <= 9:
                    rec.trimestre = '3'
                elif 10 <= mois_int <= 12:
                    rec.trimestre = '4'
                else:
                    rec.trimestre = False
            else:
                rec.trimestre = False

    @api.depends('nom_complet', 'annee', 'trimestre')
    def _compute_display_name(self):
        for rec in self:
            if rec.nom_complet and rec.annee and rec.trimestre:
                rec.display_name = f"CIMR {rec.nom_complet} - T{rec.trimestre}/{rec.annee}"
            elif rec.nom_complet:
                rec.display_name = f"CIMR {rec.nom_complet} - (Bulletin supprimé)"
            else:
                rec.display_name = "Déclaration CIMR orpheline"

    @api.model
    def generate_declarations_for_period(self, annee, trimestre=None):
        """Génère les déclarations CIMR pour une période donnée"""
        domain = [('annee', '=', annee)]
        
        if trimestre:
            mois_trimestre = {
                '1': ['1', '2', '3'],
                '2': ['4', '5', '6'], 
                '3': ['7', '8', '9'],
                '4': ['10', '11', '12']
            }
            domain.append(('mois', 'in', mois_trimestre.get(trimestre, [])))
        
        bulletins = self.env['softy.bulletin'].search(domain)
        _logger.info(f"Found {len(bulletins)} bulletins for year {annee}")
        
        # Debug: Check each bulletin for CIMR affiliations
        bulletins_cimr = []
        for bulletin in bulletins:
            employee = bulletin.employe_id
            if employee and employee.affiliation_ids:
                cimr_affiliations = employee.affiliation_ids.filtered(
                    lambda aff: aff.aff_type_id and aff.aff_type_id.type_aff in ['ccimr', 'ccimr6', 'ccimr7', 'ccimr10']
                )
                _logger.info(f"Employee {employee.name}: {len(cimr_affiliations)} CIMR affiliations found")
                if cimr_affiliations:
                    bulletins_cimr.append(bulletin)
                else:
                    _logger.info(f"Employee {employee.name}: No CIMR affiliations")
            else:
                _logger.info(f"Employee {employee.name if employee else 'Unknown'}: No affiliations at all")
        
        _logger.info(f"Bulletins with CIMR affiliations: {len(bulletins_cimr)}")
        
        # Check for existing declarations - updated to handle null bulletin_id
        bulletins_sans_declaration = []
        for bulletin in bulletins_cimr:
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