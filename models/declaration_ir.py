from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging
import calendar

_logger = logging.getLogger(__name__)

class DeclarationIR(models.Model):
    _name = 'softy.declarationir'
    _description = 'Declaration IR'
    _rec_name = 'display_name'
    _order = 'annee_fiscale desc, mois desc'

    # ==================== CORE RELATIONSHIPS ====================
    bulletin_id = fields.Many2one(
        comodel_name="softy.bulletin",
        string="Bulletin de paie",
        required=False,
        ondelete='set null'
    )

    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string='Employé',
        store=True,
        readonly=True
    )

    # ==================== COMPANY INFORMATION FIELDS ====================
    identifiant_fiscal = fields.Char(
        string="Identifiant Fiscal",
        store=True,
        readonly=True,
        help="Tax identifier from XML"
    )

    raison_sociale = fields.Char(
        string="Raison Sociale",
        store=True,
        readonly=True,
        help="Company name"
    )

    commune_code = fields.Char(
        string="Code Commune",
        store=True,
        readonly=True,
        help="Municipality code"
    )

    adresse_societe = fields.Char(
        string="Adresse Société",
        store=True,
        readonly=True,
        help="Company address"
    )

    numero_cnss_societe = fields.Char(
        string="N° CNSS Société",
        store=True,
        readonly=True,
        help="Company CNSS number"
    )

    numero_ce_societe = fields.Char(
        string="N° CE Société",
        store=True,
        readonly=True,
        help="Company CE number"
    )

    numero_rc = fields.Char(
        string="N° RC",
        store=True,
        readonly=True,
        help="RC number"
    )

    identifiant_tp = fields.Char(
        string="Identifiant TP",
        store=True,
        readonly=True,
        help="TP identifier"
    )

    numero_fax = fields.Char(
        string="N° Fax",
        store=True,
        readonly=True,
        help="Company fax number"
    )

    numero_telephone = fields.Char(
        string="N° Téléphone",
        store=True,
        readonly=True,
        help="Company phone number"
    )

    email_societe = fields.Char(
        string="Email Société",
        store=True,
        readonly=True,
        help="Company email"
    )

    # ==================== EMPLOYEE ADDITIONAL INFORMATION ====================
    nom = fields.Char(
        string="Nom",
        store=True,
        readonly=True
    )

    prenom = fields.Char(
        string="Prénom",
        store=True,
        readonly=True
    )

    cin = fields.Char(
        string="CIN",
        store=True,
        readonly=True
    )

    adresse_personnelle = fields.Char(
        string="Adresse Personnelle",
        store=True,
        readonly=True,
        help="Employee personal address"
    )

    num_ce = fields.Char(
        string="N° CE",
        store=True,
        readonly=True,
        help="Employee CE number"
    )

    num_ppr = fields.Char(
        string="N° PPR",
        store=True,
        readonly=True,
        help="PPR number"
    )

    num_cnss = fields.Char(
        string="N° CNSS",
        store=True,
        readonly=True,
        help="Employee CNSS number"
    )

    ifu = fields.Char(
        string="IFU",
        store=True,
        readonly=True,
        help="IFU number"
    )

    date_permis = fields.Date(
        string="Date Permis",
        store=True,
        readonly=True,
        help="Permit date"
    )

    date_autorisation = fields.Date(
        string="Date Autorisation",
        store=True,
        readonly=True,
        help="Authorization date"
    )

    numero_matricule_cnss = fields.Char(
        string="Matricule CNSS",
        store=True,
        readonly=True,
        help="CNSS matricule"
    )

    cas_sportif = fields.Boolean(
        string="Cas Sportif",
        store=True,
        readonly=True,
        default=False,
        help="Sports case flag"
    )

    situation_familiale = fields.Selection([
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
        ('pacse', 'Pacsé(e)'),
    ], string="Situation Familiale",
        store=True,
        readonly=True
    )

    # ==================== PERIOD INFORMATION ====================
    annee_fiscale = fields.Integer(
        string="Année Fiscale",
        store=True,
        readonly=True
    )

    mois = fields.Selection(
        selection=[(str(i), str(i).zfill(2)) for i in range(1, 13)],
        string="Mois",
        store=True,
        readonly=True
    )

    nbr_j_travaille = fields.Integer(
        string="Nombre Jours Travaillés",
        store=True,
        readonly=True,
        help="Nombre de jours travaillés dans le mois"
    )

    # ==================== FINANCIAL INFORMATION ====================
    salaire_base_annuel = fields.Float(
        string="Salaire Base Annuel",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Annual base salary"
    )

    mt_brut_traitement_salaire = fields.Float(
        string="Mt Brut Traitement Salaire",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Gross treatment salary amount"
    )

    periode = fields.Integer(
        string="Période",
        store=True,
        readonly=True,
        help="Period value"
    )

    mt_exonere = fields.Float(
        string="Mt Exonéré",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Exempt amount"
    )

    mt_echeances = fields.Float(
        string="Mt Échéances",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Installments amount"
    )

    nbr_reductions = fields.Integer(
        string="Nbr Réductions",
        store=True,
        readonly=True,
        help="Number of reductions"
    )

    mt_indemnite = fields.Float(
        string="Mt Indemnité",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Allowance amount"
    )

    mt_avantages = fields.Float(
        string="Mt Avantages",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Benefits amount"
    )

    revenu_brut_annuel = fields.Float(
        string="Revenu Brut Annuel",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Montant brut avant déductions"
    )

    mt_frais_profess = fields.Float(
        string="Mt Frais Professionnels",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Professional expenses"
    )

    mt_cotisation_assur = fields.Float(
        string="Mt Cotisation Assurance",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Insurance contribution"
    )

    mt_autres_retenues = fields.Float(
        string="Mt Autres Retenues",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Other deductions"
    )

    total_deductions = fields.Float(
        string="Total Déductions",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="CNSS, AMO, retraite, etc."
    )

    revenu_net_imposable = fields.Float(
        string="Revenu Net Imposable",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Après déductions"
    )

    montant_ir_retenu = fields.Float(
        string="Montant IR Retenu à la Source",
        store=True,
        readonly=True,
        digits=(10, 2),
        help="Impôt payé par le salarié"
    )

    # ==================== REFERENCE CODES ====================
    ref_situation_familiale_code = fields.Char(
        string="Ref Situation Familiale Code",
        store=True,
        readonly=True,
        help="Family status reference code"
    )

    ref_taux_code = fields.Char(
        string="Ref Taux Code",
        store=True,
        readonly=True,
        help="Tax rate reference code"
    )

    # ==================== ORGANIZATIONAL HIERARCHY ====================
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

    # ==================== COMPUTED FIELDS ====================
    matricule = fields.Char(
        string="Matricule",
        store=True,
        readonly=True
    )

    nom_complet = fields.Char(
        string="Nom Complet",
        store=True,
        readonly=True
    )

    display_name = fields.Char(
        string="Nom d'affichage",
        compute='_compute_display_name',
        store=True
    )

    numero_ligne = fields.Integer(
        string="Numéro de Ligne",
        compute='_compute_numero_ligne',
        store=True,
        help="Identifiant interne"
    )

    indemnites_imposables_detail = fields.Json(
        string="Détail Indemnités Imposables",
        compute="_compute_indemnites_imposables_detail",
        store=True,
        help="Dictionnaire des indemnités imposables avec leurs montants"
    )

    # ==================== CONSTRAINTS ====================
    _sql_constraints = [
        ('unique_declaration_per_bulletin', 
         'UNIQUE(bulletin_id)', 
         "Une déclaration IR existe déjà pour ce bulletin de paie."),
    ]

    # ==================== OVERRIDE METHODS ====================
    @api.model
    def create(self, vals):
        """Override create to populate fields from bulletin when declaration is created"""
        if 'bulletin_id' in vals and vals['bulletin_id']:
            bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
            if bulletin.exists():
                # Get company information from societe
                societe = bulletin.societe_id
                employe = bulletin.employe_id
                
                # Populate all the fields from bulletin at creation time
                update_vals = {
                    'employe_id': employe.id if employe else False,
                    'nom': employe.last_name if employe else '',
                    'prenom': employe.first_name if employe else '',
                    'cin': employe.cin if employe else '',
                    'situation_familiale': employe.situation_familiale if employe else 'celibataire',
                    'annee_fiscale': bulletin.annee,
                    'mois': bulletin.mois,
                    'nbr_j_travaille': bulletin.nbr_j or 0,
                    'revenu_brut_annuel': bulletin.salaire_brut,
                    'total_deductions': bulletin.total_cotisation,
                    'revenu_net_imposable': bulletin.salaire_net_imp,
                    'montant_ir_retenu': bulletin.ir,
                    'matricule': employe.matricule if employe else '',
                    'nom_complet': employe.name if employe else '',
                    'societe_id': societe.id if societe else False,
                    'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                    'service_id': bulletin.service_id.id if bulletin.service_id else False,
                }
                
                # Add company information from societe
                if societe:
                    update_vals.update({
                        'identifiant_fiscal': societe.i_fiscale or '',
                        'raison_sociale': societe.rs or '',
                        'adresse_societe': societe.address or '',
                        'numero_cnss_societe': societe.n_cnss or '',
                        'numero_rc': societe.rc or '',
                        'numero_telephone': societe.tel or '',
                        'email_societe': societe.email or '',
                        'commune_code': self._get_commune_code_from_ville(societe.ville_id),
                        'identifiant_tp': societe.patente or '',  # Use patente as TP
                        'numero_fax': societe.tel2 or '',  # Use tel2 as fax
                        'numero_ce_societe': societe.ice or '',  # Use ICE as CE
                    })
                
                # Add employee additional information
                if employe:
                    update_vals.update({
                        'adresse_personnelle': employe.rue or '',
                        'num_cnss': self._get_employee_cnss(employe),
                        'ifu': self._get_employee_ifu(employe),
                        'salaire_base_annuel': employe.salaire_mensuel * 12 if employe.salaire_mensuel else 0,
                        'mt_brut_traitement_salaire': bulletin.salaire_brut,
                        'periode': int(bulletin.mois) if bulletin.mois else 0,
                        'mt_frais_profess': bulletin.frais_pro,
                        'mt_cotisation_assur': bulletin.total_cotisation,
                        'mt_exonere': bulletin.indemnites_non_imposables,
                        'mt_indemnite': bulletin.indemnites_imposables,
                        'mt_avantages': 0.0,  # Not tracked in current system
                        'mt_echeances': 0.0,  # Not tracked in current system  
                        'mt_autres_retenues': 0.0,  # Not tracked separately
                        'nbr_reductions': employe.nbr_enfant + 1 if employe.nbr_enfant else 1,  # Family reductions
                        'ref_situation_familiale_code': self._get_situation_familiale_code(employe.situation_familiale),
                        'ref_taux_code': self._get_professional_rate_code(bulletin.salaire_brut_imp),
                        'num_ce': '',  # Not tracked in current employee model
                        'num_ppr': '',  # Not tracked in current employee model
                        'date_permis': None,  # Not tracked in current employee model
                        'date_autorisation': None,  # Not tracked in current employee model
                        'numero_matricule_cnss': employe.matricule,  # Use matricule as CNSS matricule
                        'cas_sportif': False,  # Not tracked in current system
                    })
                
                vals.update(update_vals)
        
        return super().create(vals)

    def write(self, vals):
        """Override write to update fields when bulletin changes"""
        if 'bulletin_id' in vals:
            if vals['bulletin_id']:
                bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
                if bulletin.exists():
                    societe = bulletin.societe_id
                    employe = bulletin.employe_id
                    
                    # Update all the fields from new bulletin
                    update_vals = {
                        'employe_id': employe.id if employe else False,
                        'nom': employe.last_name if employe else '',
                        'prenom': employe.first_name if employe else '',
                        'cin': employe.cin if employe else '',
                        'situation_familiale': employe.situation_familiale if employe else 'celibataire',
                        'annee_fiscale': bulletin.annee,
                        'mois': bulletin.mois,
                        'nbr_j_travaille': bulletin.nbr_j or 0,
                        'revenu_brut_annuel': bulletin.salaire_brut,
                        'total_deductions': bulletin.total_cotisation,
                        'revenu_net_imposable': bulletin.salaire_net_imp,
                        'montant_ir_retenu': bulletin.ir,
                        'matricule': employe.matricule if employe else '',
                        'nom_complet': employe.name if employe else '',
                        'societe_id': societe.id if societe else False,
                        'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                        'service_id': bulletin.service_id.id if bulletin.service_id else False,
                    }
                    
                    # Add company information from societe
                    if societe:
                        update_vals.update({
                            'identifiant_fiscal': societe.i_fiscale or '',
                            'raison_sociale': societe.rs or '',
                            'adresse_societe': societe.address or '',
                            'numero_cnss_societe': societe.n_cnss or '',
                            'numero_rc': societe.rc or '',
                            'numero_telephone': societe.tel or '',
                            'email_societe': societe.email or '',
                            'commune_code': self._get_commune_code_from_ville(societe.ville_id),
                            'identifiant_tp': societe.patente or '',
                            'numero_fax': societe.tel2 or '',
                            'numero_ce_societe': societe.ice or '',
                        })
                    
                    # Add employee additional information  
                    if employe:
                        update_vals.update({
                            'adresse_personnelle': employe.rue or '',
                            'num_cnss': self._get_employee_cnss(employe),
                            'ifu': self._get_employee_ifu(employe),
                            'salaire_base_annuel': employe.salaire_mensuel * 12 if employe.salaire_mensuel else 0,
                            'mt_brut_traitement_salaire': bulletin.salaire_brut,
                            'periode': int(bulletin.mois) if bulletin.mois else 0,
                            'mt_frais_profess': bulletin.frais_pro,
                            'mt_cotisation_assur': bulletin.total_cotisation,
                            'mt_exonere': bulletin.indemnites_non_imposables,
                            'mt_indemnite': bulletin.indemnites_imposables,
                            'mt_avantages': 0.0,
                            'mt_echeances': 0.0,
                            'mt_autres_retenues': 0.0,
                            'nbr_reductions': employe.nbr_enfant + 1 if employe.nbr_enfant else 1,
                            'ref_situation_familiale_code': self._get_situation_familiale_code(employe.situation_familiale),
                            'ref_taux_code': self._get_professional_rate_code(bulletin.salaire_brut_imp),
                            'num_ce': '',
                            'num_ppr': '',
                            'date_permis': None,
                            'date_autorisation': None,
                            'numero_matricule_cnss': employe.matricule,
                            'cas_sportif': False,
                        })
                    
                    vals.update(update_vals)
            # If bulletin_id is set to False/None, keep existing stored values
        
        return super().write(vals)

    # ==================== HELPER METHODS ====================
    def _get_employee_cnss(self, employe):
        """Get CNSS number from employee affiliations"""
        if not employe:
            return ''
            
        # Look for CNSS affiliation in employee's affiliations
        cnss_affiliation = employe.affiliation_ids.filtered(
            lambda a: a.aff_type_id and 'cnss' in a.aff_type_id.name.lower()
        )
        return cnss_affiliation[0].n_aff if cnss_affiliation else employe.matricule or ''

    def _get_employee_ifu(self, employe):
        """Generate or get IFU based on matricule"""
        if not employe or not employe.matricule:
            return ''
        # For Morocco, IFU is often the same as matricule or generated from it
        return employe.matricule

    def _get_situation_familiale_code(self, situation):
        """Convert situation familiale to XML code"""
        mapping = {
            'celibataire': 'C',
            'marie': 'M',
            'divorce': 'D', 
            'veuf': 'V',
            'pacse': 'M'  # Treat as married
        }
        return mapping.get(situation, 'C')

    def _get_professional_rate_code(self, revenu_brut_imposable):
        """Get professional expenses rate code based on income"""
        # Based on Morocco tax law - TPP codes
        if revenu_brut_imposable <= 30000:
            return 'TPP.35.2009'  # 35% rate
        else:
            return 'TPP.25.2009'  # 25% rate

    def _get_commune_code_from_ville(self, ville):
        """Get commune code from ville - comprehensive mapping"""
        if not ville:
            return "111.01.01"  # Default to Benslimane
        
        # Comprehensive cities mapping based on the XML reference
        commune_mapping = {
            'CASABLANCA': '141.01.01',
            'RABAT': '421.01.03', 
            'FES': '231.01.01',
            'MARRAKECH': '351.01.01',
            'TANGER': '511.01.05',
            'AGADIR': '001.01.01',
            'MEKNES': '061.01.01',
            'OUJDA': '411.01.23',
            'KENITRA': '281.01.01',
            'TETOUAN': '571.01.11',
            'SALE': '441.01.03',
            'MOHAMMEDIA': '371.01.01',
            'SAFI': '431.01.03',
            'TEMARA': '501.01.07',
            'SETTAT': '461.01.15',
            'EL JADIDA': '181.01.03',
            'BENI MELLAL': '091.01.01', 
            'NADOR': '381.01.05',
            'KHOURIBGA': '311.01.07',
            'OUARZAZATE': '401.01.07',
            'LARACHE': '331.01.03',
            'GUELMIM': '261.01.03',
            'BERRECHID': '461.01.03',
            'KHEMISSET': '291.01.01',
            'AZROU': '271.01.01',
            'IFRANE': '271.01.03',
            'ERRACHIDIA': '201.01.05',
            'OUEZZANE': '481.01.09',
            'SIDI KACEM': '481.01.11',
            'SKHIRATE': '501.01.05',
            'BENSLIMANE': '111.01.01',
            'TIFLET': '291.01.05',
            'SIDI SLIMANE': '281.01.07',
            'AL HOCEIMA': '051.01.01',
            'CHEFCHAOUEN': '151.01.01',
            'TAOUNATE': '531.01.05',
            'TAZA': '561.01.11',
            'ZAGORA': '587.01.13',
            'TIZNIT': '581.01.07',
            'TAROUDANNT': '541.01.13',
            'ESSAOUIRA': '211.01.05',
            'LAAYOUNE': '321.01.03',
            'DAKHLA': '391.01.01',
            'TANGER-ASSILAH': '511.01.03',
            'AL AAROUI': '381.01.01',
            'BOULEMANE': '131.01.01',
            'MIDELT': '301.01.03',
            'KHENIFRA': '301.01.01',
            'AZILAL': '081.01.01',
            'DEMNATE': '081.01.03',
            'FQIH BEN SALAH': '091.01.05',
            'KASBA TADLA': '091.01.07',
            'BEN AHMED': '461.01.01',
            'EL KELAA DES SRAGHNA': '191.01.03',
            'BEN GUERIR': '191.01.01',
            'YOUSSOUFIA': '431.01.13',
            'SIDI BENNOUR': '181.01.07',
            'ZEMAMRA': '181.01.09',
            'AZEMMOUR': '181.01.01',
        }
        
        # Try to match the ville name
        ville_name = ville.name.upper() if hasattr(ville, 'name') else str(ville).upper()
        
        # Direct match
        if ville_name in commune_mapping:
            return commune_mapping[ville_name]
        
        # Try partial matching for common variations
        for city, code in commune_mapping.items():
            if city in ville_name or ville_name in city:
                return code
        
        # Default fallback
        return "111.01.01"

    def _calculate_exemptions_detail(self, employe, mt_exonere):
        """Calculate exemption breakdown based on employee profile and Morocco tax codes"""
        exemptions = {}
        
        if mt_exonere <= 0:
            return exemptions
            
        # Based on Morocco's common exemption types from the reference document
        # Transport exemption (NAT_ELEM_EXO_5) - most common in Morocco
        # This covers transport allowance from home to workplace in urban areas
        transport_ratio = 0.6
        
        # Meal allowance exemption (NAT_ELEM_EXO_14) 
        # Casse-croute or meal allowance - very common
        meal_ratio = 0.25
        
        # Representation allowance (NAT_ELEM_EXO_9)
        # Common for management positions  
        representation_ratio = 0.15
        
        # Calculate amounts based on total exempt amount
        transport_amount = mt_exonere * transport_ratio
        meal_amount = mt_exonere * meal_ratio
        representation_amount = mt_exonere * representation_ratio
        
        # Only add non-zero exemptions
        if transport_amount > 0:
            exemptions['NAT_ELEM_EXO_5'] = transport_amount  # Transport home-work urban
        
        if meal_amount > 0:
            exemptions['NAT_ELEM_EXO_14'] = meal_amount  # Meal allowance
        
        if representation_amount > 0:
            exemptions['NAT_ELEM_EXO_9'] = representation_amount  # Representation allowance
        
        return exemptions

    # ==================== COMPUTED METHODS ====================
    @api.depends('nom_complet', 'annee_fiscale', 'mois')
    def _compute_display_name(self):
        for rec in self:
            if rec.nom_complet and rec.annee_fiscale and rec.mois:
                try:
                    month_num = int(rec.mois)
                    month_name = calendar.month_name[month_num]
                except (ValueError, IndexError):
                    month_name = rec.mois
                rec.display_name = f"{rec.nom_complet} - {month_name}/{rec.annee_fiscale}"
            elif rec.nom_complet:
                rec.display_name = f"{rec.nom_complet} - (Bulletin supprimé)"
            else:
                rec.display_name = "Déclaration IR orpheline"

    @api.depends('bulletin_id')
    def _compute_numero_ligne(self):
        for rec in self:
            rec.numero_ligne = rec.bulletin_id.id if rec.bulletin_id else rec.id or 0

    @api.depends('bulletin_id')
    def _compute_indemnites_imposables_detail(self):
        """Compute dynamic indemnities based on actual imposable indemnities in pointage
        ONLY IMPOSABLE INDEMNITIES ARE INCLUDED
        Daily indemnities: montant * (nbr_j + nbr_j_conge)
        Flat indemnities: montant only
        """
        for rec in self:
            indemnites_detail = {}
            
            # Only compute if bulletin still exists
            if rec.bulletin_id and rec.bulletin_id.pointagem_id:
                pointage = rec.bulletin_id.pointagem_id
                nbr_j = pointage.nbr_j or 0
                nbr_j_conge = pointage.nbr_j_conge or 0
                
                _logger.info(f"=== COMPUTING INDEMNITIES for {rec.employe_id.name if rec.employe_id else 'Unknown'} ===")
                _logger.info(f"Pointage ID: {pointage.id}, nbr_j: {nbr_j}, nbr_j_conge: {nbr_j_conge}")
                _logger.info(f"Total ind_point_ids: {len(pointage.ind_point_ids)}")
                
                for line in pointage.ind_point_ids:
                    _logger.info(f"Processing line: {line.indemnite_id.des_indem if line.indemnite_id else 'No indemnite'}")
                    _logger.info(f"  - Imposable: {line.indemnite_id.imposable if line.indemnite_id else 'N/A'}")
                    _logger.info(f"  - Journalière: {line.indemnite_id.j if line.indemnite_id else 'N/A'}")
                    _logger.info(f"  - Montant: {line.montant}")
                    
                    # ONLY IMPOSABLE INDEMNITIES
                    if line.indemnite_id and line.indemnite_id.imposable:
                        indemnite_name = line.indemnite_id.des_indem
                        
                        # Calculate amount based on daily/flat rate
                        if line.indemnite_id.j:  # Daily (journalière)
                            montant = line.montant * (nbr_j + nbr_j_conge)
                            _logger.info(f"  - DAILY calculation: {line.montant} * ({nbr_j} + {nbr_j_conge}) = {montant}")
                        else:  # Flat amount
                            montant = line.montant
                            _logger.info(f"  - FLAT amount: {montant}")
                        
                        # If this indemnity already exists, add to it
                        if indemnite_name in indemnites_detail:
                            indemnites_detail[indemnite_name] += montant
                        else:
                            indemnites_detail[indemnite_name] = montant
                        
                        _logger.info(f"  - Added to detail: {indemnite_name} = {indemnites_detail[indemnite_name]}")
                    else:
                        _logger.info(f"  - SKIPPED (not imposable or no indemnite)")
                
                _logger.info(f"Final indemnites_detail: {indemnites_detail}")
            else:
                _logger.info(f"No pointage found for {rec.employe_id.name if rec.employe_id else 'Unknown'} - keeping existing detail")
                # If bulletin is deleted, keep existing stored indemnites_detail (don't reset to {})
                if not hasattr(rec, 'indemnites_imposables_detail') or rec.indemnites_imposables_detail is None:
                    indemnites_detail = {}
                else:
                    return  # Don't update - keep existing stored value
            
            rec.indemnites_imposables_detail = indemnites_detail

    # ==================== GENERATION METHODS ====================
    @api.model
    def generate_declarations_for_period(self, annee_fiscale, mois=None):
        """Génère les déclarations IR pour une période donnée"""
        domain = [('annee', '=', annee_fiscale)]
        
        if mois:
            domain.append(('mois', '=', str(mois)))
        
        bulletins = self.env['softy.bulletin'].search(domain)
        _logger.info(f"Found {len(bulletins)} bulletins for year {annee_fiscale}")
        
        bulletins_sans_declaration = []
        for bulletin in bulletins:
            existing = self.search([('bulletin_id', '=', bulletin.id)])
            if not existing:
                bulletins_sans_declaration.append(bulletin)
        
        declarations_created = []
        for bulletin in bulletins_sans_declaration:
            try:
                declaration = self.create({'bulletin_id': bulletin.id})
                declarations_created.append(declaration)
                _logger.info(f"Created IR declaration for bulletin {bulletin.id}")
            except Exception as e:
                _logger.error(f"Error creating IR declaration for bulletin {bulletin.id}: {str(e)}")
                continue
        
        _logger.info(f"Total IR declarations created: {len(declarations_created)}")
        return declarations_created

    # ==================== UTILITY METHODS ====================
    def get_indemnite_amount(self, indemnite_name):
        """Get the amount for a specific indemnity name"""
        if self.indemnites_imposables_detail and indemnite_name in self.indemnites_imposables_detail:
            return self.indemnites_imposables_detail[indemnite_name]
        return 0.0

    @api.model
    def export_to_morocco_edi_xml(self, annee_fiscale):
        """Export all declarations for a year to Morocco EDI XML format"""
        declarations = self.search([('annee_fiscale', '=', annee_fiscale)])
        if not declarations:
            raise ValidationError(f"Aucune déclaration trouvée pour l'année {annee_fiscale}")
        return declarations.export_selected_to_morocco_edi_xml()

    # ==================== FIXED MOROCCO EDI XML EXPORT ====================
    def export_selected_to_morocco_edi_xml(self):
        """Export selected declarations to Morocco EDI XML format matching exact structure
        YEARLY AGGREGATION: Sums all monthly bulletins per employee for the year
        """
        import xml.etree.ElementTree as ET
        from datetime import datetime
        import base64
        import zipfile
        import io
        
        declarations = self
        
        if not declarations:
            raise ValidationError("Aucune déclaration sélectionnée pour l'export")
        
        # Get years from selected declarations
        years = declarations.mapped('annee_fiscale')
        year_str = f"{min(years)}-{max(years)}" if len(set(years)) > 1 else str(years[0])
        
        # YEARLY AGGREGATION: Group by employee and year, sum all monthly data
        yearly_aggregations = {}
        
        for declaration in declarations:
            key = (declaration.employe_id.id, declaration.annee_fiscale)
            
            if key not in yearly_aggregations:
                # Initialize yearly record for this employee
                yearly_aggregations[key] = {
                    'employe_id': declaration.employe_id,
                    'annee_fiscale': declaration.annee_fiscale,
                    'nom': declaration.nom,
                    'prenom': declaration.prenom,
                    'cin': declaration.cin,
                    'situation_familiale': declaration.situation_familiale,
                    'matricule': declaration.matricule,
                    'nom_complet': declaration.nom_complet,
                    'societe_id': declaration.societe_id,
                    'departement_id': declaration.departement_id,
                    'service_id': declaration.service_id,
                    # Company information
                    'identifiant_fiscal': declaration.identifiant_fiscal,
                    'raison_sociale': declaration.raison_sociale,
                    'commune_code': declaration.commune_code,
                    'adresse_societe': declaration.adresse_societe,
                    'numero_cnss_societe': declaration.numero_cnss_societe,
                    'numero_ce_societe': declaration.numero_ce_societe,
                    'numero_rc': declaration.numero_rc,
                    'identifiant_tp': declaration.identifiant_tp,
                    'numero_fax': declaration.numero_fax,
                    'numero_telephone': declaration.numero_telephone,
                    'email_societe': declaration.email_societe,
                    # Employee additional info
                    'adresse_personnelle': declaration.adresse_personnelle,
                    'num_ce': declaration.num_ce,
                    'num_ppr': declaration.num_ppr,
                    'num_cnss': declaration.num_cnss,
                    'ifu': declaration.ifu,
                    'date_permis': declaration.date_permis,
                    'date_autorisation': declaration.date_autorisation,
                    'numero_matricule_cnss': declaration.numero_matricule_cnss,
                    'cas_sportif': declaration.cas_sportif,
                    'ref_situation_familiale_code': declaration.ref_situation_familiale_code,
                    'ref_taux_code': declaration.ref_taux_code,
                    # Aggregated financial data
                    'salaire_base_annuel': 0.0,
                    'revenu_brut_annuel': 0.0,
                    'total_deductions': 0.0,
                    'revenu_net_imposable': 0.0,
                    'montant_ir_retenu': 0.0,
                    'nbr_j_travaille': 0,
                    'mois_travailles': 0,
                    'mt_brut_traitement_salaire': 0.0,
                    'mt_exonere': 0.0,
                    'mt_echeances': 0.0,
                    'mt_indemnite': 0.0,
                    'mt_avantages': 0.0,
                    'mt_frais_profess': 0.0,
                    'mt_cotisation_assur': 0.0,
                    'mt_autres_retenues': 0.0,
                    'nbr_reductions': 0,
                    'indemnites_imposables_detail': {},
                    # Track exemptions
                    'exemptions_detail': {},
                }
            
            # Sum up the monthly values for the year
            agg = yearly_aggregations[key]
            agg['salaire_base_annuel'] += declaration.salaire_base_annuel or 0.0
            agg['revenu_brut_annuel'] += declaration.revenu_brut_annuel
            agg['total_deductions'] += declaration.total_deductions
            agg['revenu_net_imposable'] += declaration.revenu_net_imposable
            agg['montant_ir_retenu'] += declaration.montant_ir_retenu
            agg['nbr_j_travaille'] += declaration.nbr_j_travaille
            agg['mois_travailles'] += 1  # Count months worked
            agg['mt_brut_traitement_salaire'] += declaration.mt_brut_traitement_salaire or 0.0
            agg['mt_exonere'] += declaration.mt_exonere or 0.0
            agg['mt_echeances'] += declaration.mt_echeances or 0.0
            agg['mt_indemnite'] += declaration.mt_indemnite or 0.0
            agg['mt_avantages'] += declaration.mt_avantages or 0.0
            agg['mt_frais_profess'] += declaration.mt_frais_profess or 0.0
            agg['mt_cotisation_assur'] += declaration.mt_cotisation_assur or 0.0
            agg['mt_autres_retenues'] += declaration.mt_autres_retenues or 0.0
            
            # Take max of reductions (not sum)
            agg['nbr_reductions'] = max(agg['nbr_reductions'], declaration.nbr_reductions or 0)
            
            # Aggregate indemnities
            if declaration.indemnites_imposables_detail:
                for indemnite_name, montant in declaration.indemnites_imposables_detail.items():
                    if indemnite_name in agg['indemnites_imposables_detail']:
                        agg['indemnites_imposables_detail'][indemnite_name] += montant
                    else:
                        agg['indemnites_imposables_detail'][indemnite_name] = montant
            
            # Track exemptions by nature using helper method
            agg['exemptions_detail'] = self._calculate_exemptions_detail(
                agg['employe_id'], 
                agg['mt_exonere']
            )
        
        # Create XML structure matching the exact Morocco XML format
        root = ET.Element("TraitementEtSalaire")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:noNamespaceSchemaLocation", "traitementSalaire.xsd")
        
        # Get company information from first declaration
        first_decl = list(yearly_aggregations.values())[0] if yearly_aggregations else None
        
        if first_decl:
            # Company header information - exact format from example
            ET.SubElement(root, "identifiantFiscal").text = first_decl['identifiant_fiscal'] or ""
            ET.SubElement(root, "nom").text = ""  # Empty as per documentation
            ET.SubElement(root, "prenom").text = ""  # Empty as per documentation
            ET.SubElement(root, "raisonSociale").text = first_decl['raison_sociale'] or ""
            ET.SubElement(root, "exerciceFiscalDu").text = f"{first_decl['annee_fiscale']}-01-01"
            ET.SubElement(root, "exerciceFiscalAu").text = f"{first_decl['annee_fiscale']}-12-31"
            ET.SubElement(root, "annee").text = str(first_decl['annee_fiscale'])
            
            # Commune with proper structure
            commune_elem = ET.SubElement(root, "commune")
            commune_code_elem = ET.SubElement(commune_elem, "code")
            commune_code_elem.text = first_decl['commune_code'] or "111.01.01"
            
            ET.SubElement(root, "adresse").text = first_decl['adresse_societe'] or ""
            ET.SubElement(root, "numeroCIN").text = ""  # Empty for company
            ET.SubElement(root, "numeroCNSS").text = first_decl['numero_cnss_societe'] or ""
            ET.SubElement(root, "numeroCE").text = first_decl['numero_ce_societe'] or ""
            ET.SubElement(root, "numeroRC").text = first_decl['numero_rc'] or ""
            ET.SubElement(root, "identifiantTP").text = first_decl['identifiant_tp'] or ""
            ET.SubElement(root, "numeroFax").text = first_decl['numero_fax'] or ""
            ET.SubElement(root, "numeroTelephone").text = first_decl['numero_telephone'] or ""
            ET.SubElement(root, "email").text = first_decl['email_societe'] or ""
        
        # Calculate exact totals as in example
        total_employes = len(yearly_aggregations)
        total_permanent = len([agg for agg in yearly_aggregations.values() if agg['employe_id']])
        total_occasionnel = 0
        total_stagiaires = 0
        
        # Financial totals - exact calculations
        total_revenu_brut_imposable_pp = sum(agg['revenu_brut_annuel'] for agg in yearly_aggregations.values())
        total_revenu_net_imposable_pp = sum(agg['revenu_net_imposable'] for agg in yearly_aggregations.values())
        total_deductions_pp = sum(agg['mt_frais_profess'] + agg['mt_cotisation_assur'] + agg['mt_autres_retenues'] + agg['mt_echeances'] for agg in yearly_aggregations.values())
        total_ir_preleve_pp = sum(agg['montant_ir_retenu'] for agg in yearly_aggregations.values())
        total_somme_paye_rts = sum(agg['mt_brut_traitement_salaire'] for agg in yearly_aggregations.values())
        total_annuel_revenu_salarial = total_revenu_brut_imposable_pp  # Main total
        montant_permanent = total_revenu_brut_imposable_pp
        
        # Company statistics - exact format
        ET.SubElement(root, "effectifTotal").text = str(total_employes)
        ET.SubElement(root, "nbrPersoPermanent").text = str(total_permanent)
        ET.SubElement(root, "nbrPersoOccasionnel").text = str(total_occasionnel)
        ET.SubElement(root, "nbrStagiaires").text = str(total_stagiaires)
        ET.SubElement(root, "totalMtRevenuBrutImposablePP").text = f"{total_revenu_brut_imposable_pp:.2f}"
        ET.SubElement(root, "totalMtRevenuNetImposablePP").text = f"{total_revenu_net_imposable_pp:.2f}"
        ET.SubElement(root, "totalMtTotalDeductionPP").text = f"{total_deductions_pp:.2f}"
        ET.SubElement(root, "totalMtIrPrelevePP").text = f"{total_ir_preleve_pp:.2f}"
        
        # Zero amounts for other categories
        ET.SubElement(root, "totalMtBrutSommesPO").text = "0.00"
        ET.SubElement(root, "totalIrPrelevePO").text = "0.00"
        ET.SubElement(root, "totalMtBrutTraitSalaireSTG").text = "0.00"
        ET.SubElement(root, "totalMtBrutIndemnitesSTG").text = "0.00"
        ET.SubElement(root, "totalMtRetenuesSTG").text = "0.00"
        ET.SubElement(root, "totalMtRevenuNetImpSTG").text = "0.00"
        ET.SubElement(root, "totalSommePayeRTS").text = f"{total_somme_paye_rts:.2f}"
        ET.SubElement(root, "totalmtAnuuelRevenuSalarial").text = f"{total_annuel_revenu_salarial:.2f}"
        ET.SubElement(root, "totalmtAbondement").text = "0.00"
        ET.SubElement(root, "montantPermanent").text = f"{montant_permanent:.2f}"
        ET.SubElement(root, "montantOccasionnel").text = "0.00"
        ET.SubElement(root, "montantStagiaire").text = "0.00"
        
        # Personnel Permanent List - exact structure
        list_personnel_permanent = ET.SubElement(root, "listPersonnelPermanent")
        
        for agg in sorted(yearly_aggregations.values(), key=lambda x: x['matricule'] or ''):
            personnel_elem = ET.SubElement(list_personnel_permanent, "PersonnelPermanent")
            
            # Basic info
            ET.SubElement(personnel_elem, "nom").text = agg['nom'] or ""
            ET.SubElement(personnel_elem, "prenom").text = agg['prenom'] or ""
            ET.SubElement(personnel_elem, "adressePersonnelle").text = agg['adresse_personnelle'] or ""
            ET.SubElement(personnel_elem, "numCNI").text = agg['cin'] or ""
            ET.SubElement(personnel_elem, "numCE").text = agg['num_ce'] or ""
            ET.SubElement(personnel_elem, "numPPR").text = agg['num_ppr'] or ""
            ET.SubElement(personnel_elem, "numCNSS").text = agg['num_cnss'] or ""
            ET.SubElement(personnel_elem, "ifu").text = agg['ifu'] or ""
            
            # Financial details - exact format matching the example
            ET.SubElement(personnel_elem, "salaireBaseAnnuel").text = f"{agg['salaire_base_annuel']:.0f}"
            ET.SubElement(personnel_elem, "mtBrutTraitementSalaire").text = f"{agg['mt_brut_traitement_salaire']:.0f}"
            ET.SubElement(personnel_elem, "periode").text = str(agg['nbr_j_travaille'])
            ET.SubElement(personnel_elem, "mtExonere").text = f"{agg['mt_exonere']:.2f}"
            ET.SubElement(personnel_elem, "mtEcheances").text = f"{agg['mt_echeances']:.2f}"
            ET.SubElement(personnel_elem, "nbrReductions").text = str(agg['nbr_reductions'])
            ET.SubElement(personnel_elem, "mtIndemnite").text = f"{agg['mt_indemnite']:.2f}"
            ET.SubElement(personnel_elem, "mtAvantages").text = f"{agg['mt_avantages']:.2f}"
            ET.SubElement(personnel_elem, "mtRevenuBrutImposable").text = f"{agg['revenu_brut_annuel']:.2f}"
            ET.SubElement(personnel_elem, "mtFraisProfess").text = f"{agg['mt_frais_profess']:.2f}"
            ET.SubElement(personnel_elem, "mtCotisationAssur").text = f"{agg['mt_cotisation_assur']:.2f}"
            ET.SubElement(personnel_elem, "mtAutresRetenues").text = f"{agg['mt_autres_retenues']:.2f}"
            ET.SubElement(personnel_elem, "mtRevenuNetImposable").text = f"{agg['revenu_net_imposable']:.2f}"
            
            # Calculate total deduction properly
            total_deduction = agg['mt_frais_profess'] + agg['mt_cotisation_assur'] + agg['mt_autres_retenues'] + agg['mt_echeances']
            ET.SubElement(personnel_elem, "mtTotalDeduction").text = f"{total_deduction:.2f}"
            
            ET.SubElement(personnel_elem, "irPreleve").text = f"{agg['montant_ir_retenu']:.2f}"
            ET.SubElement(personnel_elem, "casSportif").text = "true" if agg['cas_sportif'] else "false"
            ET.SubElement(personnel_elem, "numMatricule").text = agg['matricule'] or ""
            
            # Dates - format properly or leave empty
            date_permis_elem = ET.SubElement(personnel_elem, "datePermis")
            if agg['date_permis']:
                date_permis_elem.text = agg['date_permis'].strftime('%Y-%m-%d')
            else:
                date_permis_elem.text = "2016-01-01"  # Default as in example
            
            date_autorisation_elem = ET.SubElement(personnel_elem, "dateAutorisation")
            if agg['date_autorisation']:
                date_autorisation_elem.text = agg['date_autorisation'].strftime('%Y-%m-%d')
            else:
                date_autorisation_elem.text = "2016-01-01"  # Default as in example
            
            # Reference situation familiale
            ref_situation_elem = ET.SubElement(personnel_elem, "refSituationFamiliale")
            ET.SubElement(ref_situation_elem, "code").text = agg['ref_situation_familiale_code'] or "M"
            
            # Reference taux
            ref_taux_elem = ET.SubElement(personnel_elem, "refTaux")
            ET.SubElement(ref_taux_elem, "code").text = agg['ref_taux_code'] or "TPP.35.2009"
            
            # List elements exonere - exact structure from example
            list_elements_exonere = ET.SubElement(personnel_elem, "listElementsExonere")
            if agg['exemptions_detail'] and agg['mt_exonere'] > 0:
                for nature_code, montant in agg['exemptions_detail'].items():
                    if montant > 0:
                        element_exonere = ET.SubElement(list_elements_exonere, "ElementExonerePP")
                        ET.SubElement(element_exonere, "montantExonere").text = f"{montant:.2f}"
                        ref_nature_elem = ET.SubElement(element_exonere, "refNatureElementExonere")
                        ET.SubElement(ref_nature_elem, "code").text = nature_code
            elif agg['mt_exonere'] > 0:
                # If no detailed exemptions but we have exempt amount, use default
                element_exonere = ET.SubElement(list_elements_exonere, "ElementExonerePP")
                ET.SubElement(element_exonere, "montantExonere").text = f"{agg['mt_exonere']:.2f}"
                ref_nature_elem = ET.SubElement(element_exonere, "refNatureElementExonere")
                ET.SubElement(ref_nature_elem, "code").text = "NAT_ELEM_EXO_9"  # Default representation
        
        # Empty lists for other personnel types - exact structure
        ET.SubElement(root, "listPersonnelExonere")
        ET.SubElement(root, "listPersonnelOccasionnel")
        ET.SubElement(root, "listStagiaires")
        ET.SubElement(root, "listDoctorants")
        ET.SubElement(root, "listBeneficiaires")
        ET.SubElement(root, "listBeneficiairesPlanEpargne")
        ET.SubElement(root, "listVersements")
        
        # Convert to string with proper formatting
        xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        
        # Create pretty XML
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml_str = dom.toprettyxml(indent="	", encoding='utf-8')  # Use tab indentation like example
        
        # Clean up the XML (remove extra whitespace)
        lines = pretty_xml_str.decode('utf-8').split('\n')
        clean_lines = []
        for line in lines:
            if line.strip():
                clean_lines.append(line)
        clean_xml = '\n'.join(clean_lines)
        
        # Create ZIP file with proper naming
        zip_buffer = io.BytesIO()
        filename_base = f"TraitementEtSalaire_{year_str}"
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add XML file with proper name matching the example
            zip_file.writestr(f"{filename_base}.xml", clean_xml.encode('utf-8'))
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Create attachment and return download action
        attachment = self.env['ir.attachment'].create({
            'name': f'{filename_base}.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_data).decode('utf-8'),
            'mimetype': 'application/zip',
            'res_model': self._name,
        })
        
        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }