from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CertificatTravail(models.Model):
    _name = 'softy.certificat'
    _description = 'Certificat de Travail'
    _rec_name = 'ref'
    _order = 'date_creation desc'

    # ==================== BASIC FIELDS ====================
    ref = fields.Char(
        string='Référence',
        required=True,
    )
    
    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string="Employé",
        required=True,
        ondelete='cascade'
    )
    
    date_creation = fields.Date(
        string='Date de Création',
        default=fields.Date.context_today,
        required=True
    )
    
    # ==================== COMPUTED FIELDS FROM EMPLOYEE ====================
    cin = fields.Char(
        string='CIN',
        related='employe_id.cin',
        store=True,
        readonly=True
    )
    
    name = fields.Char(
        string='Nom Complet',
        related='employe_id.name',
        store=True,
        readonly=True
    )
    
    matricule = fields.Char(
        string='Matricule',
        related='employe_id.matricule',
        store=True,
        readonly=True
    )
    
    # ==================== AFFILIATION INFORMATION ====================
    n_aff = fields.Char(
        string='N° Affiliation',
        compute='_compute_affiliation_info',
        store=True,
        readonly=True
    )
    
    @api.depends('employe_id.affiliation_ids')
    def _compute_affiliation_info(self):
        """Compute the main affiliation number (usually CNSS)"""
        for certificat in self:
            if certificat.employe_id and certificat.employe_id.affiliation_ids:
                # Try to find CNSS affiliation first, otherwise take the first one
                cnss_aff = certificat.employe_id.affiliation_ids.filtered(
                    lambda aff: aff.aff_type_id.type_aff == 'cnss'
                )
                if cnss_aff:
                    certificat.n_aff = cnss_aff[0].n_aff
                else:
                    # Take the first affiliation if no CNSS found
                    certificat.n_aff = certificat.employe_id.affiliation_ids[0].n_aff
            else:
                certificat.n_aff = False
    
    # ==================== RELATIONAL FIELDS FOR ORGANIZATION ====================
    societe_id = fields.Many2one(
        'softy.societe',
        string='Société',
        related='employe_id.societe_id',
        store=True,
        readonly=True
    )
    
    departement_id = fields.Many2one(
        'softy.departement',
        string='Département',
        related='employe_id.departement_id',
        store=True,
        readonly=True
    )
    
    service_id = fields.Many2one(
        'softy.service',
        string='Service',
        related='employe_id.service_id',
        store=True,
        readonly=True
    )
    
    # ==================== CHAR FIELDS FOR ORGANIZATION (for backward compatibility) ====================
    service = fields.Char(
        string='Service Name',
        related='service_id.name',
        store=True,
        readonly=True
    )
    
    departement = fields.Char(
        string='Département Name',
        related='departement_id.libelle',
        store=True,
        readonly=True
    )
    
    societe_name = fields.Char(
        string='Société Name',
        related='societe_id.rs',
        store=True,
        readonly=True
    )
    
    societe_ville_nom = fields.Char(
        string='Ville Société',
        related='societe_id.ville_id.name',
        store=True,
        readonly=True
    )
    
    societe_address = fields.Char(
        string='Adresse Société',
        related='societe_id.address',
        store=True,
        readonly=True
    )
    
    # ==================== QUALIFICATION/CONTRACT INFORMATION ====================
    qualification = fields.Char(
        string='Qualification',
        related='employe_id.qualification_id.qualification',
        store=True,
        readonly=True
    )
    
    type_contrat = fields.Selection(
        string='Type de Contrat',
        related='employe_id.contrat_id.type_contrat',
        store=True,
        readonly=True
    )
    
    # ==================== CONSTRAINTS ====================
    _sql_constraints = [
        ('ref_uniq', 'unique(ref)', 'La référence du certificat doit être unique.'),
    ]
    
    def action_print_certificate(self):
        """Print the work certificate"""
        return self.env.ref('softy_hr.report_certificat_document').report_action(self)