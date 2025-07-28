from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class Employe(models.Model):
    _name = 'softy.employe'
    _description = 'Employé'
    _rec_name = 'name'

    image_1920 = fields.Image("Photo")
    
    # ==================== BASIC INFORMATION ====================
    first_name      = fields.Char(string="Prénom", required=True)
    last_name       = fields.Char(string="Nom", required=True)
    name            = fields.Char(string="Nom Complet", compute='_compute_name', store=True)
    matricule       = fields.Char(string="Matricule", required=True)
    cin             = fields.Char(string="CIN", required=True)
    situation_familiale = fields.Selection([
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
        ('pacse', 'Pacsé(e)'),
    ], string='Situation Familiale', required=False)
    date_naissance  = fields.Date(string="Date de Naissance", required=True)
    lieu_naissance  = fields.Many2one('softy.ville', string="Lieu de Naissance", required=True)
    genre = fields.Selection([
        ('masculin', 'Masculin'),
        ('feminin', 'Féminin'),
    ], string='Genre', required=True)

    nbr_enfant      = fields.Integer(string="Nombre d'enfants", default=0)
    rue             = fields.Char(string="Rue", required=True)
    email           = fields.Char(string="Email", required=True)
    tel             = fields.Char(string="Téléphone", required=True)
    date_embauche   = fields.Date(string="Date d'embauche", required=True)
    paie_blocke     = fields.Boolean(string="Paie Bloquée ?", default=False)
    date_blockage   = fields.Date(string="Date de Blocage")
    motif_blockage  = fields.Char(string="Motif de Blocage")
    qualification_id=fields.Many2one(comodel_name="softy.qualification",string="Fonction")
    mode_payment=fields.Selection([
        ("vir","Virement"),
        ("cheque","Cheque"),
        ("esp","Espece"),
        ("Mise a Disposition","mise a disposition"),
        ("telepai","Tele Paiment"),
        ("ca","Cash Entreprise"),
    ])
    # Computed age field
    age = fields.Integer(string="Âge", compute='_compute_age', store=True)

    # ==================== AFFECTATION (SERVICE/DÉPARTEMENT/SOCIÉTÉ) ====================
    service_id = fields.Many2one("softy.service", string="Service")
    
    # Champs relationnels pour afficher département et société
    departement_id = fields.Many2one(
        'softy.departement',
        string='Département',
        related='service_id.departement_id',
        store=True,
        readonly=True
    )
    
    societe_id = fields.Many2one(
        'softy.societe',
        string='Société',
        related='service_id.departement_id.societe_id',
        store=True,
        readonly=True
    )
    
    # Informations ville du département
    ville_departement_id = fields.Many2one(
        'softy.ville',
        string='Ville du Département',
        related='departement_id.ville_id',
        store=True,
        readonly=True
    )

    # ==================== BANK INFORMATION (FIXED) ====================
    info_banque_ids = fields.One2many('softy.info_banque_employe', 'employe_id', string='Informations Bancaires')
    
    # For compatibility with existing views, add computed fields
    n_compte_banque = fields.Char(string='N° Compte Principal', compute='_compute_bank_info', store=True)
    banque_name = fields.Selection([
        ("albarid","Al Barid"),
        ("awb","AWB"),
        ("bmce","BMCE"),
        ("bmci","BMCI"),
        ("bp","Banque Populaire"),
        ("bqassafa","Banque Assafa"),
        ("cam","CAM"),
        ("cfg","Banque CFG"),
        ("cih","Banque CIH"),
        ("cm","Banque CM"),
        ("sgmb","Banque SGMB"),
        ("umnia","Banque Umnia"),
        ("wafacash","Wafa Cash"),
    ], string='Banque Principale', compute='_compute_bank_info', store=True)

    # ==================== AFFILIATIONS (One-to-Many) ====================
    affiliation_ids = fields.One2many('softy.affiliation', 'employe_id', string='Affiliations')

    #apps_ids = fields.One2many('softy.affiliation', 'employe_id', string='Affiliations')
    # ==================== CONTRACT (One-to-One) ====================
    contrat_id = fields.Many2one('softy.contrat', string='Contrat', ondelete='cascade')
    ref_contrat = fields.Char(related='contrat_id.ref', string='Réf. Contrat', readonly=True)
    type_contrat = fields.Selection(related='contrat_id.type_contrat', string='Type Contrat', readonly=True)
    salaire_mensuel = fields.Float(related='contrat_id.salaire', string='Salaire Mensuel', readonly=True)
    date_debut_contrat = fields.Date(related='contrat_id.date_debut', string='Début Contrat', readonly=True)
    date_fin_contrat = fields.Date(related='contrat_id.date_fin', string='Fin Contrat', readonly=True)

    # ==================== INFORMATIONS TEMPS DE TRAVAIL DE LA SOCIÉTÉ ====================
    societe_nbr_jours_mois = fields.Integer(
        string='Nombre Jours/Mois (Société)',
        related='societe_id.nbr_jours_mois',
        store=True,
        readonly=True
    )

    societe_nbr_heures_mois = fields.Integer(
        string='Nombre Heures/Mois (Société)',
        related='societe_id.nbr_heures_mois',
        store=True,
        readonly=True
    )
    
    # ==================== DOCUMENTS (One-to-Many) ====================
    document_ids = fields.One2many('softy.document', 'employe_id', string='Documents')

    # ==================== FAMILY MEMBERS (One-to-Many) ====================
    famille_ids = fields.One2many('softy.membrefamille', 'employe_id', string='Membres de la Famille')

    # ==================== COMPETENCY RELATIONSHIPS ====================
    langue_ids = fields.One2many('softy.langue', 'employe_id', string='Languages')
    competence_ids = fields.One2many('softy.competence', 'employe_id', string='Compétences')
    experience_ids = fields.One2many('softy.experience', 'employe_id', string='Experiences')
    formation_ids = fields.One2many('softy.formation', 'employe_id', string='Formations')
    diplome_ids = fields.One2many('softy.diplome', 'employe_id', string='Diplomes')

    # ==================== SMART BUTTON COUNTS ====================
    document_count = fields.Integer(string='Nombre de Documents', compute='_compute_counts')
    family_count = fields.Integer(string='Nombre de Membres Famille', compute='_compute_counts')
    diploma_count = fields.Integer(string='Nombre de Diplômes', compute='_compute_counts')
    experience_count = fields.Integer(string='Nombre d\'Expériences', compute='_compute_counts')
    formation_count = fields.Integer(string='Nombre de Formations', compute='_compute_counts')
    competence_count = fields.Integer(string='Nombre de Compétences', compute='_compute_counts')

    # ==================== AFFECTATION COUNT ====================
    affectation_info = fields.Char(
        string='Affectation Complète',
        compute='_compute_affectation_info',
        store=True
    )
    

    # ==================== CONSTRAINTS ====================
    _sql_constraints = [
        ('matricule_uniq', 'unique(matricule)', "Ce matricule existe déjà."),
        ('cin_uniq', 'unique(cin)', "Ce CIN existe déjà."),
        ('contrat_uniq', 'unique(contrat_id)', 'Ce contrat est déjà assigné à un autre employé.'),
    ]

    # ==================== CRUD METHODS ====================

    @api.model
    def create(self, vals):
        """Override create to handle contract creation"""
        employee = super(Employe, self).create(vals)
        
        # If a contract was assigned during creation, ensure bidirectional link
        if employee.contrat_id:
            # Make sure the contract points back to this employee
            if employee.contrat_id.employe_id.id != employee.id:
                employee.contrat_id.write({'employe_id': employee.id})
        
        return employee

    def write(self, vals):
        """Override write to handle contract updates"""
        # Store old contract info before update
        old_contracts = {}
        for employee in self:
            if employee.contrat_id:
                old_contracts[employee.id] = employee.contrat_id
        
        # Perform the write operation
        result = super(Employe, self).write(vals)
        
        # Handle contract changes after write
        if 'contrat_id' in vals:
            for employee in self:
                # Handle old contract
                old_contract = old_contracts.get(employee.id)
                if old_contract and old_contract.exists():
                    # If the old contract's employee is still this employee, clear it
                    if old_contract.employe_id and old_contract.employe_id.id == employee.id:
                        # Only clear if we're changing to a different contract or no contract
                        if not employee.contrat_id or employee.contrat_id.id != old_contract.id:
                            old_contract.write({'employe_id': False})
                
                # Handle new contract
                if employee.contrat_id:
                    # Make sure the contract points back to this employee
                    if employee.contrat_id.employe_id.id != employee.id:
                        employee.contrat_id.write({'employe_id': employee.id})
        
        return result

    def unlink(self):
        """Override unlink to handle contract cleanup"""
        # Store contracts before deletion
        contracts_to_update = []
        for employee in self:
            if employee.contrat_id and employee.contrat_id.employe_id == employee:
                contracts_to_update.append(employee.contrat_id)
        
        # Delete the employees
        result = super(Employe, self).unlink()
        
        # Clear employee reference from contracts (if they still exist)
        for contract in contracts_to_update:
            if contract.exists():
                contract.write({'employe_id': False})
        
        return result

    # ==================== COMPUTE METHODS ====================

    @api.depends('first_name', 'last_name')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()

    @api.depends('date_naissance')
    def _compute_age(self):
        today = date.today()
        for employee in self:
            if employee.date_naissance:
                employee.age = today.year - employee.date_naissance.year - (
                    (today.month, today.day) < (employee.date_naissance.month, employee.date_naissance.day)
                )
            else:
                employee.age = 0

    @api.depends('service_id', 'departement_id', 'societe_id')
    def _compute_affectation_info(self):
        for employee in self:
            affectation_parts = []
            if employee.societe_id:
                affectation_parts.append(employee.societe_id.rs)
            if employee.departement_id:
                affectation_parts.append(employee.departement_id.libelle)
            if employee.service_id:
                affectation_parts.append(employee.service_id.name)
            
            employee.affectation_info = ' → '.join(affectation_parts) if affectation_parts else 'Non affecté'

    @api.depends('info_banque_ids')
    def _compute_bank_info(self):
        for employee in self:
            if employee.info_banque_ids:
                # Take the first bank account as primary
                primary_bank = employee.info_banque_ids[0]
                employee.n_compte_banque = primary_bank.n_acc
                employee.banque_name = primary_bank.name
            else:
                employee.n_compte_banque = False
                employee.banque_name = False

    @api.depends('document_ids', 'famille_ids', 'diplome_ids', 'experience_ids', 'formation_ids', 'competence_ids')
    def _compute_counts(self):
        for employee in self:
            employee.document_count = len(employee.document_ids)
            employee.family_count = len(employee.famille_ids)
            employee.diploma_count = len(employee.diplome_ids)
            employee.experience_count = len(employee.experience_ids)
            employee.formation_count = len(employee.formation_ids)
            employee.competence_count = len(employee.competence_ids)

    # Computed fields for rates
    taux_horaire = fields.Float(
        string='Taux Horaire',
        compute='_compute_taux_horaire',
        store=True,
        readonly=True,
        digits=(10, 2)
    )

    taux_journalier = fields.Float(
        string='Taux Journalier',
        compute='_compute_taux_journalier',
        store=True,
        readonly=True,
        digits=(10, 2)
    )

    @api.depends('salaire_mensuel', 'societe_nbr_heures_mois')
    def _compute_taux_horaire(self):
        for employee in self:
            if employee.salaire_mensuel and employee.societe_nbr_heures_mois:
                employee.taux_horaire = employee.salaire_mensuel / employee.societe_nbr_heures_mois
            else:
                employee.taux_horaire = 0.0

    @api.depends('salaire_mensuel', 'societe_nbr_jours_mois')
    def _compute_taux_journalier(self):
        for employee in self:
            if employee.salaire_mensuel and employee.societe_nbr_jours_mois:
                employee.taux_journalier = employee.salaire_mensuel / employee.societe_nbr_jours_mois
            else:
                employee.taux_journalier = 0.0

    # ==================== VALIDATION METHODS ====================

    @api.constrains('date_blockage', 'date_embauche')
    def _check_block_dates(self):
        for rec in self:
            if rec.paie_blocke and rec.date_blockage:
                if rec.date_blockage < rec.date_embauche:
                    raise ValidationError("La date de blocage doit être postérieure ou égale à la date d'embauche.")

    @api.constrains('date_naissance')
    def _check_birth_date(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_naissance > today:
                raise ValidationError("La date de naissance ne peut être future.")

    @api.constrains('email')
    def _check_email_format(self):
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for rec in self:
            if rec.email and not re.match(email_regex, rec.email):
                raise ValidationError("Format d'email invalide.")

    @api.constrains('nbr_enfant')
    def _check_nbr_enfant(self):
        for rec in self:
            if rec.nbr_enfant < 0:
                raise ValidationError("Le nombre d'enfants ne peut être négatif.")

    #@api.constrains('service_id')
    #def _check_service_affectation(self):
    #    for rec in self:
      #      if not rec.service_id:
                raise ValidationError("Un employé doit être affecté à un service.")

    # ==================== ONCHANGE METHODS ====================
    @api.onchange('paie_blocke')
    def _onchange_paie_blocke(self):
        if not self.paie_blocke:
            self.date_blockage = False
            self.motif_blockage = False

    @api.onchange('service_id')
    def _onchange_service_id(self):
        """
        Mise à jour automatique du département et société quand on change le service
        """
        if self.service_id:
            # Les champs related se mettront à jour automatiquement
            return {
                'domain': {
                    'service_id': []  # Pas de restriction particulière
                }
            }

    @api.onchange('contrat_id')
    def _onchange_contrat_id(self):
        """
        Handle contract changes in the UI
        """
        if self.contrat_id:
            # Warn if the contract is already assigned to another employee
            if self.contrat_id.employe_id and self.contrat_id.employe_id.id != self.id:
                return {
                    'warning': {
                        'title': 'Contrat déjà assigné',
                        'message': f'Ce contrat est déjà assigné à {self.contrat_id.employe_id.name}. Il sera transféré à cet employé.'
                    }
                }

    # ==================== ACTION METHODS ====================
    def action_view_documents(self):
        return {
            'name': 'Documents',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.document',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }

    def action_view_family(self):
        return {
            'name': 'Membres de la Famille',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.membrefamille',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }

    def action_view_diplomas(self):
        return {
            'name': 'Diplômes',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.diplome',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }

    def action_view_experiences(self):
        return {
            'name': 'Expériences',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.experience',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }

    def action_view_formations(self):
        return {
            'name': 'Formations',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.formation',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }

    def action_view_competences(self):
        return {
            'name': 'Compétences',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.competence',
            'view_mode': 'list,form',
            'domain': [('employe_id', '=', self.id)],
            'context': {'default_employe_id': self.id},
        }

    def action_block_payroll(self):
        self.write({
            'paie_blocke': True,
            'date_blockage': fields.Date.context_today(self),
        })

    def action_unblock_payroll(self):
        self.write({
            'paie_blocke': False,
            'date_blockage': False,
            'motif_blockage': False,
        })

    def action_change_affectation(self):
        """
        Action pour changer l'affectation d'un employé
        """
        return {
            'name': 'Changer l\'Affectation',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.employe',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('votre_module.view_employe_affectation_form').id,
            'target': 'new',
        }

    def action_create_contract(self):
        """
        Action to create a new contract for this employee
        """
        return {
            'name': 'Créer un Contrat',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.contrat',
            'view_mode': 'form',
            'context': {
                'default_employe_id': self.id,
            },
            'target': 'new',
        }

    def action_view_contract(self):
        """
        Action to view the employee's contract
        """
        if not self.contrat_id:
            return self.action_create_contract()
        
        return {
            'name': 'Contrat',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.contrat',
            'res_id': self.contrat_id.id,
            'view_mode': 'form',
            'target': 'current',
        }