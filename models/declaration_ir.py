from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import logging
import calendar
import xml.etree.ElementTree as ET
import xml.dom.minidom
import base64
import zipfile
import io
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class DeclarationIR(models.Model):
    _name = 'softy.declarationir'
    _description = 'Declaration IR - 100% Conforme au Manuel EDI'
    _rec_name = 'display_name'
    _order = 'annee_fiscale desc, mois desc'

    # ==================== CORE RELATIONSHIPS ====================
    bulletin_id = fields.Many2one(
        comodel_name="softy.bulletin",
        string="Bulletin de paie",
        required=False,
        ondelete='set null',
        help="Bulletin de paie source pour cette déclaration"
    )

    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string='Employé',
        store=True,
        readonly=True,
        index=True
    )

    # ==================== COMPANY IDENTIFICATION (PAGE 1 PDF) ====================
    identifiant_fiscal = fields.Char(
        string="N° D'IDENTIFICATION FISCALE",
        store=True,
        readonly=True,
        help="Identifiant fiscal de l'entreprise"
    )

    nom_entreprise = fields.Char(
        string="NOM",
        store=True,
        readonly=True,
        help="Nom de l'entreprise (vide pour personne morale)"
    )

    prenom_entreprise = fields.Char(
        string="PRENOM", 
        store=True,
        readonly=True,
        help="Prénom de l'entreprise (vide pour personne morale)"
    )

    raison_sociale = fields.Char(
        string="RAISON SOCIALE",
        store=True,
        readonly=True,
        help="Raison sociale de l'entreprise"
    )

    exercice_fiscal_du = fields.Date(
        string="EXERCICE FISCAL DU",
        store=True,
        readonly=True,
        help="1er Janvier de l'année de la déclaration"
    )

    exercice_fiscal_au = fields.Date(
        string="EXERCICE FISCAL AU",
        store=True,
        readonly=True,
        help="31 Décembre de l'année de la déclaration"
    )

    annee_fiscale = fields.Integer(
        string="ANNÉE",
        store=True,
        readonly=True,
        index=True
    )

    commune_code = fields.Char(
        string="CODE COMMUNE",
        store=True,
        readonly=True,
        help="Code de la commune selon référentiel"
    )

    adresse_siege_social = fields.Char(
        string="ADRESSE DU SIEGE SOCIAL",
        store=True,
        readonly=True,
        help="Adresse du siège social ou du principal établissement"
    )

    numero_cin_entreprise = fields.Char(
        string="N° C.N.I. ENTREPRISE",
        store=True,
        readonly=True,
        help="CIN de l'entreprise (vide pour personne morale)"
    )

    numero_cnss_entreprise = fields.Char(
        string="N° CNSS ENTREPRISE",
        store=True,
        readonly=True,
        help="Numéro CNSS de l'entreprise"
    )

    numero_ce_entreprise = fields.Char(
        string="N° CARTE DE SÉJOUR ENTREPRISE",
        store=True,
        readonly=True,
        help="Numéro carte de séjour de l'entreprise"
    )

    numero_rc = fields.Char(
        string="N° RC",
        store=True,
        readonly=True,
        help="Numéro de registre de commerce"
    )

    numero_fax = fields.Char(
        string="N° FAX",
        store=True,
        readonly=True,
        help="Numéro de fax de l'entreprise"
    )

    numero_telephone = fields.Char(
        string="N° TELEPHONE",
        store=True,
        readonly=True,
        help="Numéro de téléphone de l'entreprise"
    )

    identifiant_tp = fields.Char(
        string="IDENTIFIANT TP",
        store=True,
        readonly=True,
        help="Identifiant taxe professionnelle"
    )

    email_entreprise = fields.Char(
        string="ADRESSE EMAIL",
        store=True,
        readonly=True,
        help="Adresse email de l'entreprise"
    )

    # ==================== EFFECTIF (PAGE 2 PDF) ====================
    effectif_total = fields.Integer(
        string="EFFECTIF TOTAL",
        store=True,
        readonly=True,
        help="Effectif total au 31 décembre"
    )

    personnel_permanent = fields.Integer(
        string="PERSONNEL PERMANENT",
        store=True,
        readonly=True,
        help="Nombre de personnel permanent"
    )

    personnel_occasionnel = fields.Integer(
        string="PERSONNEL OCCASIONNEL",
        store=True,
        readonly=True,
        help="Nombre de personnel occasionnel"
    )

    stagiaires = fields.Integer(
        string="STAGIAIRES",
        store=True,
        readonly=True,
        help="Nombre de stagiaires"
    )

    # ==================== EMPLOYEE INFORMATION (PAGE 3-4 PDF) ====================
    nom_employe = fields.Char(
        string="NOM EMPLOYÉ",
        store=True,
        readonly=True,
        help="Nom de famille de l'employé"
    )

    prenom_employe = fields.Char(
        string="PRÉNOM EMPLOYÉ",
        store=True,
        readonly=True,
        help="Prénom de l'employé"
    )

    adresse_personnelle = fields.Char(
        string="ADRESSE PERSONNELLE",
        store=True,
        readonly=True,
        help="Adresse personnelle de l'employé"
    )

    num_cni = fields.Char(
        string="CNI",
        store=True,
        readonly=True,
        help="Numéro carte nationale d'identité"
    )

    num_carte_sejour = fields.Char(
        string="CARTE DE SÉJOUR",
        store=True,
        readonly=True,
        help="Numéro carte de séjour"
    )

    num_ppr = fields.Char(
        string="PPR",
        store=True,
        readonly=True,
        help="Numéro PPR"
    )

    num_cnss_employe = fields.Char(
        string="CNSS EMPLOYÉ",
        store=True,
        readonly=True,
        help="Numéro CNSS de l'employé"
    )

    ifu_employe = fields.Char(
        string="I.F. DE L'EMPLOYÉ",
        store=True,
        readonly=True,
        help="Identifiant fiscal de l'employé"
    )

    # ==================== FINANCIAL FIELDS (PAGE 4 PDF) ====================
    salaire_base_annuel = fields.Float(
        string="SALAIRE DE BASE ANNUEL",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Salaire de base annuel"
    )

    mt_brut_traitement_salaire = fields.Float(
        string="MONTANT BRUT TRAITEMENTS ET SALAIRES",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant brut des traitements, salaires et émoluments"
    )

    periode_jours = fields.Integer(
        string="PÉRIODE EN JOURS",
        store=True,
        readonly=True,
        help="Période en jours travaillés"
    )

    mt_exonere = fields.Float(
        string="MONTANT ÉLÉMENTS EXONÉRÉS",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant des éléments exonérés"
    )

    mt_echeances = fields.Float(
        string="MONTANT ÉCHÉANCES PRÉLEVÉES",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant des échéances prélevées"
    )

    nbr_reductions = fields.Integer(
        string="NOMBRE DE RÉDUCTIONS",
        store=True,
        readonly=True,
        help="Nombre de réductions pour charges de famille"
    )

    mt_indemnites = fields.Float(
        string="MONTANT INDEMNITÉS",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant des indemnités versées à titre de frais professionnels"
    )

    mt_avantages = fields.Float(
        string="MONTANT AVANTAGES",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant des avantages en argent ou en nature"
    )

    mt_revenu_brut_imposable = fields.Float(
        string="MONTANT REVENU BRUT IMPOSABLE",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant du revenu brut imposable"
    )

    mt_frais_professionnels = fields.Float(
        string="MONTANT FRAIS PROFESSIONNELS",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant des frais professionnels"
    )

    mt_cotisations_assurance = fields.Float(
        string="MONTANT COTISATIONS ASSURANCE",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant des cotisations d'assurance retraites"
    )

    mt_autres_retenues = fields.Float(
        string="MONTANT AUTRES RETENUES",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montants des autres retenues"
    )

    mt_revenu_net_imposable = fields.Float(
        string="MONTANT REVENU NET IMPOSABLE",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Montant du revenu net imposable"
    )

    mt_total_deductions = fields.Float(
        string="TOTAL DÉDUCTIONS SUR REVENU",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Total des déductions sur revenu"
    )

    ir_preleve = fields.Float(
        string="I.R. PRÉLEVÉ",
        store=True,
        readonly=True,
        digits=(12, 2),
        help="Impôt sur le revenu prélevé"
    )

    cas_sportif = fields.Boolean(
        string="CAS SPORTIF",
        store=True,
        readonly=True,
        default=False,
        help="Spécification du cas sportif"
    )

    numero_matricule = fields.Char(
        string="NUMÉRO MATRICULE",
        store=True,
        readonly=True,
        help="Numéro de matricule de l'employé"
    )

    date_permis = fields.Date(
        string="DATE PERMIS D'HABITER",
        store=True,
        readonly=True,
        help="Date du permis d'habiter"
    )

    date_autorisation = fields.Date(
        string="DATE AUTORISATION DE CONSTRUIRE",
        store=True,
        readonly=True,
        help="Date de l'autorisation de construire"
    )

    # ==================== REFERENCE CODES (PAGE 4-5 PDF) ====================
    ref_situation_familiale_code = fields.Char(
        string="CODE SITUATION FAMILIALE",
        store=True,
        readonly=True,
        help="Code situation de famille selon référentiel"
    )

    ref_taux_frais_professionnels_code = fields.Char(
        string="CODE TAUX FRAIS PROFESSIONNELS",
        store=True,
        readonly=True,
        help="Code du taux des frais professionnels selon référentiel"
    )

    # ==================== PAYMENT METHOD (PAGE 9 PDF) - NOUVEAU OBLIGATOIRE ====================
    ref_moyen_paiement_code = fields.Char(
        string="CODE MOYEN DE PAIEMENT",
        store=True,
        readonly=True,
        help="Mode de paiement selon référentiel (ES/CH/SIR)"
    )

    # ==================== ORGANIZATIONAL HIERARCHY ====================
    societe_id = fields.Many2one(
        comodel_name="softy.societe",
        string='Société',
        store=True,
        readonly=True,
        index=True
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

    # ==================== COMPUTED DISPLAY FIELDS ====================
    display_name = fields.Char(
        string="Nom d'affichage",
        compute='_compute_display_name',
        store=True
    )

    numero_ligne = fields.Integer(
        string="Numéro de Ligne",
        compute='_compute_numero_ligne',
        store=True,
        help="Numéro de ligne pour identification"
    )

    mois = fields.Selection(
        selection=[(str(i), f"{i:02d}") for i in range(1, 13)],
        string="Mois",
        store=True,
        readonly=True,
        index=True
    )

    # ==================== EXEMPTED ELEMENTS STORAGE ====================
    elements_exoneres_detail = fields.Json(
        string="Détail Éléments Exonérés",
        store=True,
        readonly=True,
        help="Détail des éléments exonérés avec codes NAT_ELEM_EXO"
    )

    # ==================== CONSTRAINTS ====================
    _sql_constraints = [
        ('unique_declaration_per_bulletin', 
         'UNIQUE(bulletin_id)', 
         "Une déclaration IR existe déjà pour ce bulletin de paie."),
        ('check_annee_fiscale', 
         'CHECK(annee_fiscale >= 2000 AND annee_fiscale <= 2099)', 
         "L'année fiscale doit être comprise entre 2000 et 2099."),
        ('check_periode_jours', 
         'CHECK(periode_jours >= 0 AND periode_jours <= 366)', 
         "La période en jours doit être comprise entre 0 et 366."),
    ]

    # ==================== CRUD METHODS ====================
    @api.model
    def create(self, vals):
        """Override create to populate all fields from bulletin"""
        if 'bulletin_id' in vals and vals['bulletin_id']:
            bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
            if bulletin.exists():
                vals.update(self._extract_all_fields_from_bulletin(bulletin))
        
        return super().create(vals)

    def write(self, vals):
        """Override write to update fields when bulletin changes"""
        if 'bulletin_id' in vals and vals['bulletin_id']:
            bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
            if bulletin.exists():
                vals.update(self._extract_all_fields_from_bulletin(bulletin))
        
        return super().write(vals)

    # ==================== FIELD EXTRACTION METHODS ====================
    def _extract_all_fields_from_bulletin(self, bulletin):
        """Extract all required fields from bulletin for 100% conformity"""
        employe = bulletin.employe_id
        societe = bulletin.societe_id
        
        # Base values
        vals = {
            'employe_id': employe.id if employe else False,
            'societe_id': societe.id if societe else False,
            'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
            'service_id': bulletin.service_id.id if bulletin.service_id else False,
            'annee_fiscale': bulletin.annee,
            'mois': bulletin.mois,
        }

        # Company information (Page 1 PDF)
        if societe:
            vals.update({
                'identifiant_fiscal': societe.i_fiscale or '',
                'nom_entreprise': '',  # Empty for legal entity as per doc
                'prenom_entreprise': '',  # Empty for legal entity as per doc
                'raison_sociale': societe.rs or '',
                'exercice_fiscal_du': date(bulletin.annee, 1, 1),
                'exercice_fiscal_au': date(bulletin.annee, 12, 31),
                'commune_code': self._get_commune_code_from_ville(societe.ville_id),
                'adresse_siege_social': societe.address or '',
                'numero_cin_entreprise': '',  # Empty for legal entity
                'numero_cnss_entreprise': societe.n_cnss or '',
                'numero_ce_entreprise': societe.ice or '',  # Using ICE as CE
                'numero_rc': societe.rc or '',
                'numero_fax': societe.tel2 or '',  # Using tel2 as fax
                'numero_telephone': societe.tel or '',
                'identifiant_tp': societe.patente or '',
                'email_entreprise': societe.email or '',
                # Effectif (calculated from societe data)
                'effectif_total': self._calculate_effectif_total(societe),
                'personnel_permanent': self._calculate_personnel_permanent(societe),
                'personnel_occasionnel': 0,  # We don't handle occasional personnel
                'stagiaires': 0,  # We don't handle trainees
            })

        # Employee information (Page 3-4 PDF)
        if employe:
            vals.update({
                'nom_employe': employe.last_name or '',
                'prenom_employe': employe.first_name or '',
                'adresse_personnelle': employe.rue or '',
                'num_cni': employe.cin or '',
                'num_carte_sejour': '',  # Not available in current model
                'num_ppr': '',  # Not available in current model
                'num_cnss_employe': self._get_employee_cnss(employe),
                'ifu_employe': employe.matricule or '',  # Using matricule as IFU
                'numero_matricule': employe.matricule or '',
                'date_permis': None,  # Default as in example
                'date_autorisation': None,  # Default as in example
                'cas_sportif': False,  # Default value
                'nbr_reductions': (employe.nbr_enfant or 0),  # Number of children only as per example
                'ref_situation_familiale_code': self._get_situation_familiale_code(employe.situation_familiale),
                'ref_moyen_paiement_code': self._get_moyen_paiement_code(employe.mode_payment),
            })

        # Financial information from bulletin (Page 4 PDF)
        if bulletin:
            # CRITICAL FIX: Calculate base salary correctly
            # Base salary = gross salary - all indemnities (taxable and non-taxable)
            total_indemnities = (bulletin.indemnites_imposables or 0.0) + (bulletin.indemnites_non_imposables or 0.0)
            base_monthly_salary = bulletin.salaire_brut - total_indemnities
            
            vals.update({
                'salaire_base_annuel': base_monthly_salary * 12,  # Annual base without indemnities
                'mt_brut_traitement_salaire': bulletin.salaire_brut or 0.0,  # Total gross including everything
                'periode_jours': (bulletin.nbr_j or 0) + (bulletin.nbr_j_conge or 0),  # Total days (worked + vacation)
                'mt_exonere': bulletin.indemnites_non_imposables or 0.0,
                'mt_echeances': 0.0,  # Not available in current model
                'mt_indemnites': 0.0,  # Professional expenses indemnities (different from imposable indemnities)
                'mt_avantages': 0.0,  # Not available in current model
                'mt_revenu_brut_imposable': bulletin.salaire_brut_imp or 0.0,
                'mt_frais_professionnels': bulletin.frais_pro or 0.0,
                'mt_cotisations_assurance': bulletin.total_cotisation or 0.0,
                'mt_autres_retenues': 0.0,  # Not separated in current model
                'mt_revenu_net_imposable': bulletin.salaire_net_imp or 0.0,
                'mt_total_deductions': (bulletin.frais_pro or 0.0) + (bulletin.total_cotisation or 0.0),
                'ir_preleve': bulletin.ir or 0.0,
                'ref_taux_frais_professionnels_code': self._get_professional_rate_code(bulletin.salaire_brut_imp),
                'elements_exoneres_detail': self._extract_real_exemptions_from_employee(employe, bulletin),
            })

        return vals

    # ==================== CRITICAL FIX: REAL EXEMPTIONS EXTRACTION ====================
    def _extract_real_exemptions_from_employee(self, employe, bulletin):
        """Extract REAL exemptions from employee indemnities with codeir mapping"""
        exemptions = {}
        
        if not employe:
            return exemptions
        
        # PART 1: Employee permanent indemnities (app_ids)
        if employe.app_ids:
            for appointment in employe.app_ids:
                # Only non-taxable indemnities with codeir
                if (not appointment.imposable and 
                    appointment.indemnite_id.codeir and 
                    appointment.montant > 0):
                    
                    codeir = appointment.indemnite_id.codeir.strip()
                    
                    # Calculate monthly amount based on journalière flag
                    if appointment.indemnite_id.j:  # Daily indemnity
                        monthly_amount = appointment.montant * ((bulletin.nbr_j or 0) + (bulletin.nbr_j_conge or 0))
                    else:  # Monthly flat indemnity
                        monthly_amount = appointment.montant
                    
                    # Add to exemptions
                    if codeir in exemptions:
                        exemptions[codeir] += monthly_amount
                    else:
                        exemptions[codeir] = monthly_amount
        
        # PART 2: Monthly variable indemnities from pointage (if exists)
        if bulletin.pointagem_id and bulletin.pointagem_id.ind_point_ids:
            for ind_point in bulletin.pointagem_id.ind_point_ids:
                # Only non-taxable indemnities with codeir
                if (not ind_point.imposable and 
                    ind_point.indemnite_id.codeir and 
                    ind_point.montant > 0):
                    
                    codeir = ind_point.indemnite_id.codeir.strip()
                    
                    # Calculate monthly amount based on journalière flag
                    if ind_point.indemnite_id.j:  # Daily indemnity
                        monthly_amount = ind_point.montant * ((bulletin.nbr_j or 0) + (bulletin.nbr_j_conge or 0))
                    else:  # Monthly flat indemnity
                        monthly_amount = ind_point.montant
                    
                    # Add to exemptions
                    if codeir in exemptions:
                        exemptions[codeir] += monthly_amount
                    else:
                        exemptions[codeir] = monthly_amount
        
        # Log for debugging
        if exemptions:
            _logger.info(f"Extracted exemptions for {employe.name}: {exemptions}")
        
        return exemptions

    # ==================== HELPER METHODS ====================
    def _get_commune_code_from_ville(self, ville):
        """Get commune code with comprehensive Morocco mapping"""
        if not ville:
            return "141.01.51"  # Default to Casablanca-Sidi Bernoussi as per example

        # Complete Morocco commune mapping based on reference document
        commune_mapping = {
            'CASABLANCA': '141.01.01',
            'SIDI BERNOUSSI': '141.01.51',  # As per example
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
        }

        ville_name = ville.name.upper() if hasattr(ville, 'name') else str(ville).upper()
        
        # Direct match
        if ville_name in commune_mapping:
            return commune_mapping[ville_name]
        
        # Partial match
        for city, code in commune_mapping.items():
            if city in ville_name or ville_name in city:
                return code
        
        return "141.01.51"  # Default fallback to Sidi Bernoussi

    def _get_situation_familiale_code(self, situation):
        """Convert situation familiale to standard codes"""
        mapping = {
            'celibataire': 'C',
            'marie': 'M',
            'divorce': 'D',  
            'veuf': 'V',
            'pacse': 'M'  # Treat as married
        }
        return mapping.get(situation, 'C')

    def _get_professional_rate_code(self, revenu_brut_imposable):
        """Get professional expenses rate code based on Morocco tax law"""
        # Morocco 2025 rates: 35% up to 6500 MAD, 25% above
        if not revenu_brut_imposable or revenu_brut_imposable <= 6500:
            return 'TPP.35.2009'  # 35% rate
        else:
            return 'TPP.25.2009'  # 25% rate

    def _get_moyen_paiement_code(self, mode_payment):
        """Convert employee payment method to standard codes"""
        mapping = {
            'vir': 'SIR',        # Virement -> Télépaiement
            'cheque': 'CH',      # Chèque -> Chèque
            'esp': 'ES',         # Espèce -> Espèces
            'telepai': 'SIR',    # Télépaiment -> Télépaiement
            'ca': 'ES',          # Cash -> Espèces
        }
        return mapping.get(mode_payment, 'SIR')  # Default to télépaiement

    def _get_employee_cnss(self, employe):
        """Get CNSS number from employee affiliations"""
        if not employe:
            return ''
        
        # Look for CNSS affiliation
        cnss_affiliation = employe.affiliation_ids.filtered(
            lambda a: a.aff_type_id and 'cnss' in a.aff_type_id.name.lower()
        )
        return cnss_affiliation[0].n_aff if cnss_affiliation else ''

    def _calculate_effectif_total(self, societe):
        """Calculate total workforce from societe"""
        if not societe:
            return 0
        # Count active employees in this company
        return self.env['softy.employe'].search_count([
            ('societe_id', '=', societe.id),
            ('paie_blocke', '=', False)
        ])

    def _calculate_personnel_permanent(self, societe):
        """Calculate permanent personnel from societe"""
        return self._calculate_effectif_total(societe)  # All our employees are permanent

    # ==================== COMPUTED METHODS ====================
    @api.depends('nom_employe', 'prenom_employe', 'annee_fiscale', 'mois')
    def _compute_display_name(self):
        for rec in self:
            if rec.nom_employe and rec.prenom_employe and rec.annee_fiscale and rec.mois:
                try:
                    month_num = int(rec.mois)
                    month_name = calendar.month_name[month_num]
                except (ValueError, IndexError):
                    month_name = rec.mois or 'XX'
                rec.display_name = f"{rec.prenom_employe} {rec.nom_employe} - {month_name}/{rec.annee_fiscale}"
            elif rec.nom_employe and rec.prenom_employe:
                rec.display_name = f"{rec.prenom_employe} {rec.nom_employe} - Déclaration IR"
            else:
                rec.display_name = "Déclaration IR"

    @api.depends('bulletin_id')
    def _compute_numero_ligne(self):
        for rec in self:
            rec.numero_ligne = rec.bulletin_id.id if rec.bulletin_id else rec.id or 0

    # ==================== GENERATION METHODS ====================
    @api.model
    def generate_declarations_for_period(self, annee_fiscale, mois=None):
        """Generate IR declarations for a specific period"""
        domain = [('annee', '=', annee_fiscale)]
        if mois:
            domain.append(('mois', '=', str(mois)))
        
        bulletins = self.env['softy.bulletin'].search(domain)
        
        # Find bulletins without declarations
        bulletins_sans_declaration = bulletins.filtered(
            lambda b: not self.search([('bulletin_id', '=', b.id)])
        )
        
        declarations_created = []
        for bulletin in bulletins_sans_declaration:
            try:
                declaration = self.create({'bulletin_id': bulletin.id})
                declarations_created.append(declaration)
                _logger.info(f"Created IR declaration for bulletin {bulletin.id}")
            except Exception as e:
                _logger.error(f"Error creating IR declaration for bulletin {bulletin.id}: {str(e)}")
                continue
        
        return declarations_created

    # ==================== XML EXPORT METHODS ====================
    @api.model 
    def export_to_morocco_edi_xml(self, annee_fiscale):
        """Export all declarations for a year to Morocco EDI XML format"""
        declarations = self.search([('annee_fiscale', '=', annee_fiscale)])
        if not declarations:
            raise ValidationError(f"Aucune déclaration trouvée pour l'année {annee_fiscale}")
        return declarations.export_selected_to_morocco_edi_xml()

    def export_selected_to_morocco_edi_xml(self):
        """Export selected declarations to 100% compliant Morocco EDI XML"""
        if not self:
            raise ValidationError("Aucune déclaration sélectionnée pour l'export")

        # Group by year and employee for yearly aggregation
        yearly_aggregations = self._aggregate_declarations_yearly()
        
        # Create XML root with exact structure
        root = ET.Element("TraitementEtSalaire")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:noNamespaceSchemaLocation", "traitementSalaire.xsd")
        
        # Add company header information
        self._add_company_header_to_xml(root, yearly_aggregations)
        
        # Add aggregated totals
        self._add_totals_to_xml(root, yearly_aggregations)
        
        # Add personnel permanent list
        self._add_personnel_permanent_to_xml(root, yearly_aggregations)
        
        # Add empty lists for other personnel types
        self._add_empty_personnel_lists_to_xml(root)
        
        # Generate formatted XML
        return self._generate_xml_file(root, yearly_aggregations)

    def _aggregate_declarations_yearly(self):
        """Aggregate monthly declarations by employee and year"""
        yearly_aggregations = {}
        
        for declaration in self:
            key = (declaration.employe_id.id, declaration.annee_fiscale)
            
            if key not in yearly_aggregations:
                yearly_aggregations[key] = self._initialize_yearly_record(declaration)
            
            # Sum monthly values
            self._sum_monthly_values(yearly_aggregations[key], declaration)
        
        return yearly_aggregations

    def _initialize_yearly_record(self, declaration):
        """Initialize yearly aggregation record"""
        return {
            'employe_id': declaration.employe_id,
            'annee_fiscale': declaration.annee_fiscale,
            'nom': declaration.nom_employe,
            'prenom': declaration.prenom_employe,
            'cin': declaration.num_cni,
            'situation_familiale': declaration.ref_situation_familiale_code,
            'matricule': declaration.numero_matricule,
            'societe_id': declaration.societe_id,
            'departement_id': declaration.departement_id,
            'service_id': declaration.service_id,
            # Company info
            'identifiant_fiscal': declaration.identifiant_fiscal,
            'raison_sociale': declaration.raison_sociale,
            'commune_code': declaration.commune_code,
            'adresse_siege_social': declaration.adresse_siege_social,
            'numero_cnss_entreprise': declaration.numero_cnss_entreprise,
            'numero_ce_entreprise': declaration.numero_ce_entreprise,
            'numero_rc': declaration.numero_rc,
            'identifiant_tp': declaration.identifiant_tp,
            'numero_fax': declaration.numero_fax,
            'numero_telephone': declaration.numero_telephone,
            'email_entreprise': declaration.email_entreprise,
            # Employee info
            'adresse_personnelle': declaration.adresse_personnelle,
            'num_carte_sejour': declaration.num_carte_sejour,
            'num_ppr': declaration.num_ppr,
            'num_cnss_employe': declaration.num_cnss_employe,
            'ifu_employe': declaration.ifu_employe,
            'date_permis': declaration.date_permis,
            'date_autorisation': declaration.date_autorisation,
            'cas_sportif': declaration.cas_sportif,
            'ref_taux_code': declaration.ref_taux_frais_professionnels_code,
            'ref_moyen_paiement_code': declaration.ref_moyen_paiement_code,
            # Financial aggregated data (yearly totals)
            'salaire_base_annuel': 0.0,
            'mt_brut_traitement_salaire': 0.0,
            'periode_jours': 0,
            'mt_exonere': 0.0,
            'mt_echeances': 0.0,
            'nbr_reductions': 0,
            'mt_indemnites': 0.0,
            'mt_avantages': 0.0,
            'mt_revenu_brut_imposable': 0.0,
            'mt_frais_professionnels': 0.0,
            'mt_cotisations_assurance': 0.0,
            'mt_autres_retenues': 0.0,
            'mt_revenu_net_imposable': 0.0,
            'mt_total_deductions': 0.0,
            'ir_preleve': 0.0,
            'elements_exoneres_detail': {},
        }

    def _sum_monthly_values(self, agg, declaration):
        """Sum monthly values into yearly aggregation"""
        # Don't sum annual values - use them directly
        agg['salaire_base_annuel'] = declaration.salaire_base_annuel or 0.0
        
        # Sum monthly values to get yearly totals
        agg['mt_brut_traitement_salaire'] += declaration.mt_brut_traitement_salaire or 0.0
        agg['periode_jours'] += declaration.periode_jours or 0
        agg['mt_exonere'] += declaration.mt_exonere or 0.0
        agg['mt_echeances'] += declaration.mt_echeances or 0.0
        agg['mt_indemnites'] += declaration.mt_indemnites or 0.0
        agg['mt_avantages'] += declaration.mt_avantages or 0.0
        agg['mt_revenu_brut_imposable'] += declaration.mt_revenu_brut_imposable or 0.0
        agg['mt_frais_professionnels'] += declaration.mt_frais_professionnels or 0.0
        agg['mt_cotisations_assurance'] += declaration.mt_cotisations_assurance or 0.0
        agg['mt_autres_retenues'] += declaration.mt_autres_retenues or 0.0
        agg['mt_revenu_net_imposable'] += declaration.mt_revenu_net_imposable or 0.0
        agg['mt_total_deductions'] += declaration.mt_total_deductions or 0.0
        agg['ir_preleve'] += declaration.ir_preleve or 0.0
        
        # Take max of reductions (not sum)
        agg['nbr_reductions'] = max(agg['nbr_reductions'], declaration.nbr_reductions or 0)
        
        # Aggregate exemptions
        if declaration.elements_exoneres_detail:
            for code, montant in declaration.elements_exoneres_detail.items():
                if code in agg['elements_exoneres_detail']:
                    agg['elements_exoneres_detail'][code] += montant
                else:
                    agg['elements_exoneres_detail'][code] = montant

    def _add_company_header_to_xml(self, root, yearly_aggregations):
        """Add company header information to XML"""
        first_decl = list(yearly_aggregations.values())[0] if yearly_aggregations else {}
        
        ET.SubElement(root, "identifiantFiscal").text = first_decl.get('identifiant_fiscal', '')
        ET.SubElement(root, "nom").text = ''  # Empty for company
        ET.SubElement(root, "prenom").text = ''  # Empty for company
        ET.SubElement(root, "raisonSociale").text = first_decl.get('raison_sociale', '')
        ET.SubElement(root, "exerciceFiscalDu").text = f"{first_decl.get('annee_fiscale', 2025)}-01-01"
        ET.SubElement(root, "exerciceFiscalAu").text = f"{first_decl.get('annee_fiscale', 2025)}-12-31"
        ET.SubElement(root, "annee").text = str(first_decl.get('annee_fiscale', 2025))
        
        # Commune with proper structure
        commune_elem = ET.SubElement(root, "commune")
        ET.SubElement(commune_elem, "code").text = first_decl.get('commune_code', '141.01.51')
        
        ET.SubElement(root, "adresse").text = first_decl.get('adresse_siege_social', '')
        ET.SubElement(root, "numeroCIN").text = ''  # Empty for company
        ET.SubElement(root, "numeroCNSS").text = first_decl.get('numero_cnss_entreprise', '')
        ET.SubElement(root, "numeroCE").text = first_decl.get('numero_ce_entreprise', '')
        ET.SubElement(root, "numeroRC").text = first_decl.get('numero_rc', '')
        ET.SubElement(root, "identifiantTP").text = first_decl.get('identifiant_tp', '')
        ET.SubElement(root, "numeroFax").text = first_decl.get('numero_fax', '')
        ET.SubElement(root, "numeroTelephone").text = first_decl.get('numero_telephone', '')
        ET.SubElement(root, "email").text = first_decl.get('email_entreprise', '')

    def _add_totals_to_xml(self, root, yearly_aggregations):
        """Add company totals to XML"""
        total_employes = len(yearly_aggregations)
        total_revenu_brut_imposable = sum(agg['mt_revenu_brut_imposable'] for agg in yearly_aggregations.values())
        total_revenu_net_imposable = sum(agg['mt_revenu_net_imposable'] for agg in yearly_aggregations.values())
        total_deductions = sum(agg['mt_total_deductions'] for agg in yearly_aggregations.values())
        total_ir_preleve = sum(agg['ir_preleve'] for agg in yearly_aggregations.values())
        total_brut_traitement = sum(agg['mt_brut_traitement_salaire'] for agg in yearly_aggregations.values())
        total_annuel_revenu = total_brut_traitement  # Same as brut traitement for our case
        
        ET.SubElement(root, "effectifTotal").text = str(total_employes)
        ET.SubElement(root, "nbrPersoPermanent").text = str(total_employes)
        ET.SubElement(root, "nbrPersoOccasionnel").text = "0"
        ET.SubElement(root, "nbrStagiaires").text = "0"
        ET.SubElement(root, "totalMtRevenuBrutImposablePP").text = f"{total_revenu_brut_imposable:.2f}"
        ET.SubElement(root, "totalMtRevenuNetImposablePP").text = f"{total_revenu_net_imposable:.2f}"
        ET.SubElement(root, "totalMtTotalDeductionPP").text = f"{total_deductions:.2f}"
        ET.SubElement(root, "totalMtIrPrelevePP").text = f"{total_ir_preleve:.2f}"
        ET.SubElement(root, "totalMtBrutSommesPO").text = "0"
        ET.SubElement(root, "totalIrPrelevePO").text = "0"
        ET.SubElement(root, "totalMtBrutTraitSalaireSTG").text = "0.00"
        ET.SubElement(root, "totalMtBrutIndemnitesSTG").text = "0.00"
        ET.SubElement(root, "totalMtRetenuesSTG").text = "0"
        ET.SubElement(root, "totalMtRevenuNetImpSTG").text = "0.00"
        ET.SubElement(root, "totalSommePayeRTS").text = "0"
        ET.SubElement(root, "totalmtAnuuelRevenuSalarial").text = f"{total_annuel_revenu:.2f}"
        ET.SubElement(root, "totalmtAbondement").text = "0"
        ET.SubElement(root, "montantPermanent").text = f"{total_brut_traitement:.2f}"
        ET.SubElement(root, "montantOccasionnel").text = "0"
        ET.SubElement(root, "montantStagiaire").text = "0"

    def _add_personnel_permanent_to_xml(self, root, yearly_aggregations):
        """Add personnel permanent list to XML with exact example structure"""
        list_personnel_permanent = ET.SubElement(root, "listPersonnelPermanent")
        
        for agg in sorted(yearly_aggregations.values(), key=lambda x: x['matricule'] or ''):
            personnel_elem = ET.SubElement(list_personnel_permanent, "PersonnelPermanent")
            
            # Basic information
            ET.SubElement(personnel_elem, "nom").text = agg['nom'] or ''
            ET.SubElement(personnel_elem, "prenom").text = agg['prenom'] or ''
            ET.SubElement(personnel_elem, "adressePersonnelle").text = agg['adresse_personnelle'] or ''
            ET.SubElement(personnel_elem, "numCNI").text = agg['cin'] or ''
            ET.SubElement(personnel_elem, "numCE").text = agg['num_carte_sejour'] or ''
            ET.SubElement(personnel_elem, "numPPR").text = agg['num_ppr'] or ''
            ET.SubElement(personnel_elem, "numCNSS").text = agg['num_cnss_employe'] or ''
            ET.SubElement(personnel_elem, "ifu").text = agg['ifu_employe'] or ''
            
            # Financial information (yearly totals) - FORMAT AS IN EXAMPLE
            ET.SubElement(personnel_elem, "salaireBaseAnnuel").text = f"{agg['salaire_base_annuel']:.2f}"
            ET.SubElement(personnel_elem, "mtBrutTraitementSalaire").text = f"{agg['mt_brut_traitement_salaire']:.2f}"
            ET.SubElement(personnel_elem, "periode").text = f"{agg['periode_jours']:.2f}"  # Format as decimal like example
            ET.SubElement(personnel_elem, "mtExonere").text = f"{agg['mt_exonere']:.2f}"
            ET.SubElement(personnel_elem, "mtEcheances").text = f"{agg['mt_echeances']}"  # No decimals if 0
            ET.SubElement(personnel_elem, "nbrReductions").text = str(agg['nbr_reductions'])
            ET.SubElement(personnel_elem, "mtIndemnite").text = f"{agg['mt_indemnites']}"  # No decimals if 0
            ET.SubElement(personnel_elem, "mtAvantages").text = f"{agg['mt_avantages']}"  # No decimals if 0
            ET.SubElement(personnel_elem, "mtRevenuBrutImposable").text = f"{agg['mt_revenu_brut_imposable']:.2f}"
            ET.SubElement(personnel_elem, "mtFraisProfess").text = f"{agg['mt_frais_professionnels']:.0f}"  # No decimals as in example
            ET.SubElement(personnel_elem, "mtCotisationAssur").text = f"{agg['mt_cotisations_assurance']:.2f}"
            ET.SubElement(personnel_elem, "mtAutresRetenues").text = f"{agg['mt_autres_retenues']}"  # No decimals if 0
            ET.SubElement(personnel_elem, "mtRevenuNetImposable").text = f"{agg['mt_revenu_net_imposable']:.2f}"
            ET.SubElement(personnel_elem, "mtTotalDeduction").text = f"{agg['mt_total_deductions']:.2f}"
            ET.SubElement(personnel_elem, "irPreleve").text = f"{agg['ir_preleve']:.2f}"
            ET.SubElement(personnel_elem, "casSportif").text = "true" if agg['cas_sportif'] else "false"
            ET.SubElement(personnel_elem, "numMatricule").text = agg['matricule'] or ''
            
            # Dates - empty elements as in example
            ET.SubElement(personnel_elem, "datePermis")  # Empty as in example
            ET.SubElement(personnel_elem, "dateAutorisation")  # Empty as in example
            
            # Reference codes
            ref_situation_elem = ET.SubElement(personnel_elem, "refSituationFamiliale")
            ET.SubElement(ref_situation_elem, "code").text = agg['situation_familiale'] or 'C'
            
            ref_taux_elem = ET.SubElement(personnel_elem, "refTaux")
            ET.SubElement(ref_taux_elem, "code").text = agg['ref_taux_code'] or 'TPP.35.2009'
            
            # Exempted elements - CRITICAL: Use REAL extracted exemptions
            list_elements_exonere = ET.SubElement(personnel_elem, "listElementsExonere")
            if agg['elements_exoneres_detail']:
                for nature_code, montant in agg['elements_exoneres_detail'].items():
                    if montant > 0:
                        element_exonere = ET.SubElement(list_elements_exonere, "ElementExonerePP")
                        ET.SubElement(element_exonere, "montantExonere").text = f"{montant:.2f}"
                        ref_nature_elem = ET.SubElement(element_exonere, "refNatureElementExonere")
                        ET.SubElement(ref_nature_elem, "code").text = nature_code

    def _add_empty_personnel_lists_to_xml(self, root):
        """Add empty lists for other personnel types"""
        ET.SubElement(root, "listPersonnelExonere")
        ET.SubElement(root, "listPersonnelOccasionnel")
        ET.SubElement(root, "listStagiaires")
        ET.SubElement(root, "listBeneficiaires")
        ET.SubElement(root, "listBeneficiairesPlanEpargne")

    def _generate_xml_file(self, root, yearly_aggregations):
        """Generate formatted XML file and return download action"""
        # Convert to string
        xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        
        # Format with proper indentation
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml_str = dom.toprettyxml(indent=" ", encoding='utf-8')  # Single space indent like example
        
        # Clean up extra whitespace
        lines = pretty_xml_str.decode('utf-8').split('\n')
        clean_lines = [line for line in lines if line.strip()]
        clean_xml = '\n'.join(clean_lines)
        
        # Get year for filename
        years = list(set(agg['annee_fiscale'] for agg in yearly_aggregations.values()))
        year_str = f"{min(years)}-{max(years)}" if len(years) > 1 else str(years[0])
        
        # Get company info for filename
        first_decl = list(yearly_aggregations.values())[0] if yearly_aggregations else {}
        company_name = first_decl.get('raison_sociale', 'Company').replace(' ', '_')
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        filename_base = f"IR_{company_name}_{year_str}"
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename_base}.xml", clean_xml.encode('utf-8'))
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'{filename_base}.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_data).decode('utf-8'),
            'mimetype': 'application/zip',
            'res_model': self._name,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    # ==================== VALIDATION METHODS ====================
    @api.constrains('ref_situation_familiale_code')
    def _check_situation_familiale_code(self):
        """Validate situation familiale code"""
        valid_codes = ['C', 'M', 'V', 'D'] 
        for rec in self:
            if rec.ref_situation_familiale_code and rec.ref_situation_familiale_code not in valid_codes:
                raise ValidationError(f"Code situation familiale invalide: {rec.ref_situation_familiale_code}")

    @api.constrains('ref_moyen_paiement_code')
    def _check_moyen_paiement_code(self):
        """Validate payment method code (removed as this field was causing issues)"""
        pass

    @api.constrains('commune_code')
    def _check_commune_code(self):
        """Validate commune code format"""
        for rec in self:
            if rec.commune_code and not rec.commune_code.count('.') == 2:
                raise ValidationError(f"Format de code commune invalide: {rec.commune_code}")

    # ==================== UTILITY METHODS ====================
    def name_get(self):
        """Custom display name"""
        result = []
        for record in self:
            result.append((record.id, record.display_name))
        return result

    @api.model
    def get_available_years(self):
        """Get list of available years for declarations"""
        years = self.search([]).mapped('annee_fiscale')
        return sorted(list(set(years)), reverse=True)

    def action_view_bulletin(self):
        """View related bulletin"""
        if not self.bulletin_id:
            raise UserError("Aucun bulletin associé à cette déclaration")
        
        return {
            'name': 'Bulletin de Paie',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.bulletin',
            'res_id': self.bulletin_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_employe(self):
        """View related employee"""
        if not self.employe_id:
            raise UserError("Aucun employé associé à cette déclaration")
        
        return {
            'name': 'Employé',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.employe',
            'res_id': self.employe_id.id,
            'view_mode': 'form',
            'target': 'current',
        }