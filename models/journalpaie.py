from odoo import api, fields, models
from odoo.exceptions import ValidationError
import calendar

class JournalPaie(models.Model):
    _name = 'softy.jornal'  # Keep your existing name
    _description = 'Journal de Paie'
    _rec_name = 'employe_id'
    _order = 'annee desc, mois desc, employe_id'

    # ==================== RELATIONS ====================
    bulletin_id = fields.Many2one(
        comodel_name="softy.bulletin",
        string="Bulletin de paie",
        required=False,
        ondelete='set null'
    )

    employe_id = fields.Many2one(
        related="bulletin_id.employe_id",
        string='Employé',
        store=True,
        readonly=True
    )

    societe_id = fields.Many2one(
        related="employe_id.societe_id",
        string="Société",
        store=True,
        readonly=True
    )

    departement_id = fields.Many2one(
        related="employe_id.departement_id",
        string="Département",
        store=True,
        readonly=True
    )

    service_id = fields.Many2one(
        related="employe_id.service_id",
        string="Service",
        store=True,
        readonly=True
    )

    # ==================== TIME PERIOD ====================
    mois = fields.Selection(
        related="bulletin_id.mois",
        selection=[(str(i), calendar.month_name[i]) for i in range(1,13)],
        string='Mois',
        store=True,
        readonly=True
    )
    
    annee = fields.Integer(
        related="bulletin_id.annee",
        string='Année',
        store=True,
        readonly=True
    )

    # ==================== EMPLOYEE INFO ====================
    matricule = fields.Char(
        related="employe_id.matricule",
        string="Matricule",
        store=True,
        readonly=True
    )

    nom_prenom = fields.Char(
        related="employe_id.name",
        string="Nom et Prénom",
        store=True,
        readonly=True
    )

    date_embauche = fields.Date(
        related="employe_id.date_embauche",
        string="Date Embauche",
        store=True,
        readonly=True
    )

    situation_familiale = fields.Selection(
        related="employe_id.situation_familiale",
        string="Situation Familiale",
        store=True,
        readonly=True
    )

    nbr_enfant = fields.Integer(
        related="employe_id.nbr_enfant",
        string="Nombre d'enfants",
        store=True,
        readonly=True
    )

    # ==================== AFFILIATION INFO ====================
    n_aff_cnss = fields.Char(
        string="N° CNSS",
        compute="_compute_affiliation_info",
        store=True
    )

    # ==================== WORK CATEGORY ====================
    categorie = fields.Selection([
        ('nombre_j', 'Nombre J'),
        ('nombre_h', 'Nombre H'),
        ('forfait', 'Forfait'),
    ], string='Catégorie', default='nombre_j')

    # Number of deductions (set to 0 for now as per your comment)
    nbr_ded = fields.Integer(
        string="Nombre Déductions",
        default=0
    )

    # ==================== SALARY COMPONENTS ====================
    # From bulletin - Base salary components
    salaire_base = fields.Float(
        related="bulletin_id.salaire_brut",
        string="Sal. Base",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # Working days and hours
    jours_normaux = fields.Integer(
        related="bulletin_id.nbr_j",
        string="JN (Jours Normaux)",
        store=True,
        readonly=True
    )

    jours_conge = fields.Integer(
        related="bulletin_id.nbr_j_conge",
        string="JCON (Jours Congé)",
        store=True,
        readonly=True
    )

    heures_sup = fields.Float(
        string="HS (Heures Supplémentaires)",
        digits=(10, 2),
        default=0.0,
        readonly=True
    )

    # Indemnities
    indemnites_imposables = fields.Float(
        related="bulletin_id.indemnites_imposables",
        string="Ind I. (Indemnités Imposables)",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    indemnites_non_imposables = fields.Float(
        related="bulletin_id.indemnites_non_imposables",
        string="Ind N.I. (Indemnités Non Imposables)",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # ==================== SOCIAL SECURITY ====================
    cnss_salarie = fields.Float(
        string="CNSS S. (CNSS Salarié)",
        compute="_compute_cotisations_from_bulletin",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    amo_salarie = fields.Float(
        string="AMO S. (AMO Salarié)",
        compute="_compute_cotisations_from_bulletin",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    amc_salarie = fields.Float(
        string="AMC S. (AMC Salarié)",
        compute="_compute_cotisations_from_bulletin",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # ==================== EMPLOYER CONTRIBUTIONS ====================
    cnss_patronale = fields.Float(
        string="CNSS P. (CNSS Patronale)",
        compute="_compute_cotisations_from_bulletin",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    amo_patronale = fields.Float(
        string="AMO P. (AMO Patronale)",
        compute="_compute_cotisations_from_bulletin",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    amc_patronale = fields.Float(
        string="AMC P. (AMC Patronale)",
        compute="_compute_cotisations_from_bulletin",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # Professional fees
    frais_professionnels = fields.Float(
        related="bulletin_id.frais_pro",
        string="Frais Pro",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # ==================== TAX COMPONENTS ====================
    # Other deductions
    autres_retenues = fields.Float(
        string="Autre Ret.",
        digits=(10, 2),
        default=0.0
    )

    # Income tax
    impot_revenu = fields.Float(
        related="bulletin_id.ir",
        string="IPE (Impôt sur le Revenu)",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # Advances
    avances = fields.Float(
        string="Avance",
        digits=(10, 2),
        default=0.0
    )

    # Contributions (union, etc.)
    contributions = fields.Float(
        string="Contrib.",
        digits=(10, 2),
        default=0.0
    )

    # ==================== FINAL AMOUNTS ====================
    net_a_payer = fields.Float(
        related="bulletin_id.salaire_net_payer",
        string="Net à Payer",
        digits=(10, 2),
        store=True,
        readonly=True
    )

    # ==================== COMPUTED TOTALS ====================
    total_cotisations_salarie = fields.Float(
        string="Total Cotisations Salarié",
        compute="_compute_totals",
        store=True,
        digits=(10, 2)
    )

    total_cotisations_patronale = fields.Float(
        string="Total Cotisations Patronale", 
        compute="_compute_totals",
        store=True,
        digits=(10, 2)
    )

    cout_total_employeur = fields.Float(
        string="Coût Total Employeur",
        compute="_compute_totals",
        store=True,
        digits=(10, 2)
    )

    # ==================== CONSTRAINTS ====================
    _sql_constraints = [
        ('unique_employe_periode', 
         'UNIQUE(employe_id, mois, annee)', 
         "Un journal existe déjà pour cet employé sur cette période."),
    ]

    # ==================== CRUD METHODS ====================
    # Removed complex CRUD overrides since we're using related fields now

    # ==================== COMPUTE METHODS ====================
    @api.depends('employe_id.affiliation_ids')
    def _compute_affiliation_info(self):
        for rec in self:
            if rec.employe_id and rec.employe_id.affiliation_ids:
                # Find CNSS affiliation
                cnss_aff = rec.employe_id.affiliation_ids.filtered(
                    lambda a: a.aff_type_id.type_aff == 'cnss'
                )
                rec.n_aff_cnss = cnss_aff[0].n_aff if cnss_aff else ''
            else:
                rec.n_aff_cnss = ''

    @api.depends('bulletin_id.total_cotisation')
    def _compute_cotisations_from_bulletin(self):
        """Compute individual cotisation amounts from bulletin total"""
        for rec in self:
            if not rec.bulletin_id or not rec.employe_id:
                continue
                
            total_cotisation = rec.bulletin_id.total_cotisation
            
            # Reset all cotisations
            rec.cnss_salarie = 0.0
            rec.amo_salarie = 0.0 
            rec.amc_salarie = 0.0
            rec.cnss_patronale = 0.0
            rec.amo_patronale = 0.0
            rec.amc_patronale = 0.0
            
            # Calculate individual cotisations based on affiliations
            for affiliation in rec.employe_id.affiliation_ids:
                aff_type = affiliation.aff_type_id.type_aff
                taux_decimal = (affiliation.aff_type_id.taux or 0.0) / 100.0
                plafond = affiliation.aff_type_id.plafond or 0.0
                
                # Calculate base (same logic as in bulletin)
                salaire_brut_imp = rec.bulletin_id.salaire_brut_imp
                if plafond <= 0:
                    base_cotisation = salaire_brut_imp
                else:
                    base_cotisation = min(salaire_brut_imp, plafond)
                
                cotisation_amount = base_cotisation * taux_decimal
                
                # Assign to appropriate field based on type
                if aff_type == 'cnss':
                    rec.cnss_salarie = cotisation_amount
                    # Patronale is typically same rate
                    rec.cnss_patronale = cotisation_amount
                elif aff_type == 'amo':
                    rec.amo_salarie = cotisation_amount
                    rec.amo_patronale = cotisation_amount
                elif aff_type == 'amc':
                    rec.amc_salarie = cotisation_amount
                    rec.amc_patronale = cotisation_amount

    @api.depends('cnss_salarie', 'amo_salarie', 'amc_salarie', 
                 'cnss_patronale', 'amo_patronale', 'amc_patronale',
                 'salaire_base', 'indemnites_imposables', 'indemnites_non_imposables')
    def _compute_totals(self):
        for rec in self:
            # Total cotisations salarié
            rec.total_cotisations_salarie = (
                rec.cnss_salarie + rec.amo_salarie + rec.amc_salarie
            )
            
            # Total cotisations patronale
            rec.total_cotisations_patronale = (
                rec.cnss_patronale + rec.amo_patronale + rec.amc_patronale
            )
            
            # Coût total employeur = salaire brut + cotisations patronales
            salaire_brut_total = (
                rec.salaire_base + rec.indemnites_imposables + rec.indemnites_non_imposables
            )
            rec.cout_total_employeur = salaire_brut_total + rec.total_cotisations_patronale

    # ==================== ACTION METHODS ====================
    @api.model
    def generate_journal_from_bulletins(self, bulletin_ids=None):
        """
        Generate journal entries from bulletins
        :param bulletin_ids: List of bulletin IDs to process. If None, process all bulletins without journal
        :return: Dictionary with results
        """
        if bulletin_ids:
            bulletins_to_process = self.env['softy.bulletin'].browse(bulletin_ids)
        else:
            # Find all bulletins without journal entries
            bulletins_sans_journal = self.env['softy.bulletin'].search([])
            existing_journal_bulletins = self.search([('bulletin_id', '!=', False)]).mapped('bulletin_id.id')
            bulletins_to_process = bulletins_sans_journal.filtered(lambda b: b.id not in existing_journal_bulletins)
        
        if not bulletins_to_process:
            return {
                'success': False,
                'message': "Aucun bulletin à traiter trouvé.",
                'created_count': 0,
                'errors': []
            }
        
        journals_created = []
        errors = []
        
        for bulletin in bulletins_to_process:
            try:
                # Check if journal already exists for this bulletin
                existing_journal = self.search([('bulletin_id', '=', bulletin.id)], limit=1)
                if existing_journal:
                    continue
                
                # Prepare journal data from bulletin
                journal_vals = self._prepare_journal_vals_from_bulletin(bulletin)
                
                # Create journal entry
                journal = self.create(journal_vals)
                journals_created.append(journal)
                
            except Exception as e:
                error_msg = f"Erreur pour bulletin {bulletin.lib or 'ID:' + str(bulletin.id)}: {str(e)}"
                errors.append(error_msg)
        
        return {
            'success': len(journals_created) > 0,
            'created_count': len(journals_created),
            'created_journals': journals_created,
            'errors': errors,
            'message': f"{len(journals_created)} journal(aux) créé(s)" if journals_created else "Aucun journal créé"
        }

    def _prepare_journal_vals_from_bulletin(self, bulletin):
        """
        Prepare journal values from bulletin data
        :param bulletin: softy.bulletin record
        :return: Dictionary of values for journal creation
        """
        # Calculate individual cotisations from total
        cotisations = self._calculate_cotisations_from_bulletin(bulletin)
        
        # Calculate base salary (excluding indemnities)
        salaire_base = bulletin.salaire_brut - bulletin.indemnites_imposables - bulletin.indemnites_non_imposables
        
        # Get CNSS number from employee affiliations
        n_aff_cnss = ''
        if bulletin.employe_id and bulletin.employe_id.affiliation_ids:
            cnss_aff = bulletin.employe_id.affiliation_ids.filtered(
                lambda a: a.aff_type_id.type_aff == 'cnss'
            )
            n_aff_cnss = cnss_aff[0].n_aff if cnss_aff else ''
        
        return {
            'bulletin_id': bulletin.id,
            'employe_id': bulletin.employe_id.id,
            'mois': bulletin.mois,
            'annee': bulletin.annee,
            'n_aff_cnss': n_aff_cnss,
            'categorie': 'nombre_j',  # Default category
            'nbr_ded': 0,  # Default to 0 as per your requirement
            
            # Salary components
            'salaire_base': salaire_base,
            'jours_normaux': bulletin.nbr_j,
            'jours_conge': bulletin.nbr_j_conge,
            'heures_sup': 0.0,  # You may need to get this from pointage if needed
            'indemnites_imposables': bulletin.indemnites_imposables,
            'indemnites_non_imposables': bulletin.indemnites_non_imposables,
            
            # Cotisations (calculated from bulletin total)
            'cnss_salarie': cotisations.get('cnss_salarie', 0.0),
            'amo_salarie': cotisations.get('amo_salarie', 0.0),
            'amc_salarie': cotisations.get('amc_salarie', 0.0),
            'cnss_patronale': cotisations.get('cnss_patronale', 0.0),
            'amo_patronale': cotisations.get('amo_patronale', 0.0),
            'amc_patronale': cotisations.get('amc_patronale', 0.0),
            
            # Other components
            'frais_professionnels': bulletin.frais_pro,
            'impot_revenu': bulletin.ir,
            'autres_retenues': 0.0,
            'avances': 0.0,
            'contributions': 0.0,
            'net_a_payer': bulletin.salaire_net_payer,
        }

    def _calculate_cotisations_from_bulletin(self, bulletin):
        """
        Calculate individual cotisation amounts from bulletin
        :param bulletin: softy.bulletin record
        :return: Dictionary with cotisation amounts
        """
        cotisations = {
            'cnss_salarie': 0.0,
            'amo_salarie': 0.0,
            'amc_salarie': 0.0,
            'cnss_patronale': 0.0,
            'amo_patronale': 0.0,
            'amc_patronale': 0.0,
        }
        
        if not bulletin.employe_id or not bulletin.employe_id.affiliation_ids:
            return cotisations
        
        salaire_brut_imp = bulletin.salaire_brut_imp
        
        for affiliation in bulletin.employe_id.affiliation_ids:
            aff_type = affiliation.aff_type_id.type_aff
            taux_decimal = (affiliation.aff_type_id.taux or 0.0) / 100.0
            plafond = affiliation.aff_type_id.plafond or 0.0
            
            # Calculate base (same logic as in bulletin)
            if plafond <= 0:
                base_cotisation = salaire_brut_imp
            else:
                base_cotisation = min(salaire_brut_imp, plafond)
            
            cotisation_amount = base_cotisation * taux_decimal
            
            # Assign to appropriate fields based on type
            if aff_type == 'cnss':
                cotisations['cnss_salarie'] = cotisation_amount
                # Patronale is typically same rate for CNSS
                cotisations['cnss_patronale'] = cotisation_amount
            elif aff_type == 'amo':
                cotisations['amo_salarie'] = cotisation_amount
                cotisations['amo_patronale'] = cotisation_amount
            elif aff_type == 'amc':
                cotisations['amc_salarie'] = cotisation_amount
                cotisations['amc_patronale'] = cotisation_amount
        
        return cotisations

    @api.model
    def action_generate_journal_from_bulletins(self):
        """Action method to generate journal entries from existing bulletins"""
        result = self.generate_journal_from_bulletins()
        
        if result['success']:
            message = f"Génération réussie! {result['created_count']} journal(aux) créé(s)"
            if result['errors']:
                message += f"\n{len(result['errors'])} erreur(s) rencontrée(s)"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Génération des Journaux',
                    'message': message,
                    'type': 'success',
                    'sticky': True,
                }
            }
        else:
            error_message = result['message']
            if result['errors']:
                error_message += "\n" + "\n".join(result['errors'][:3])  # Show first 3 errors
                if len(result['errors']) > 3:
                    error_message += f"\n... et {len(result['errors']) - 3} autres erreurs"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur de Génération',
                    'message': error_message,
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.model
    def action_generate_journal_for_period(self, periode=None, mois=None, annee=None):
        """
        Generate journal entries for specific period
        :param periode: 'current' or 'previous'
        :param mois: specific month (1-12)
        :param annee: specific year
        """
        domain = []
        
        if periode:
            domain.append(('periode', '=', periode))
        if mois:
            domain.append(('mois', '=', str(mois)))
        if annee:
            domain.append(('annee', '=', annee))
        
        bulletins = self.env['softy.bulletin'].search(domain)
        
        if not bulletins:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Information',
                    'message': "Aucun bulletin trouvé pour la période spécifiée.",
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        result = self.generate_journal_from_bulletins(bulletins.ids)
        
        # Return appropriate notification
        if result['success']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Génération Réussie',
                    'message': f"{result['created_count']} journal(aux) créé(s) pour la période",
                    'type': 'success',
                    'sticky': True,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Génération Échouée',
                    'message': result['message'],
                    'type': 'warning',
                    'sticky': True,
                }
            }

    def action_view_bulletin(self):
        """View related bulletin"""
        if not self.bulletin_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Information',
                    'message': 'Aucun bulletin associé à ce journal.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
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
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': 'Impossible d\'accéder à l\'employé, données manquantes.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'name': 'Employé',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.employe',
            'res_id': self.employe_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_print_journal_report(self):
        """Action to print journal de paie report for selected records"""
        return self.env.ref('softy_hr.report_journal_paie_document').report_action(self)

    @api.model
    def generate_journal_recap(self, journal_ids=None, periode=None, mois=None, annee=None):
        """
        Generate a summary/recap of journal entries by rubrique codes
        :param journal_ids: List of journal IDs to process. If None, use domain filters
        :param periode: 'current' or 'previous'
        :param mois: specific month (1-12)
        :param annee: specific year
        :return: Dictionary with recap data
        """
        # Determine which journals to process
        if journal_ids:
            journals = self.browse(journal_ids)
        else:
            # Build domain based on filters
            domain = []
            if periode:
                # Get all journals for the specified period
                bulletins = self.env['softy.bulletin'].search([('periode', '=', periode)])
                journal_bulletin_ids = bulletins.mapped('id')
                domain.append(('bulletin_id', 'in', journal_bulletin_ids))
            if mois:
                domain.append(('mois', '=', str(mois)))
            if annee:
                domain.append(('annee', '=', annee))
            
            journals = self.search(domain)
        
        if not journals:
            return {
                'success': False,
                'message': "Aucun journal trouvé pour générer le récapitulatif.",
                'data': {}
            }
        
        # Initialize recap data structure
        recap_data = {
            'company_info': {},
            'period_info': {},
            'gains': [],
            'retenues': [],
            'totals': {
                'total_gains': 0.0,
                'total_retenues': 0.0,
                'net_a_payer': 0.0,
                'effectif': 0
            }
        }
        
        # Get company info from first journal
        first_journal = journals[0]
        if first_journal.societe_id:
            recap_data['company_info'] = {
                'name': first_journal.societe_id.rs or 'Société',
                'address': first_journal.societe_id.address or '',
                'i_fiscale': first_journal.societe_id.i_fiscale or '',
                'n_cnss': first_journal.societe_id.n_cnss or '',
                'logo': first_journal.societe_id.logo
            }
        
        # Get period info
        if first_journal.mois and first_journal.annee:
            month_names = ['', 'JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN',
                          'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']
            recap_data['period_info'] = {
                'mois': month_names[int(first_journal.mois)] if int(first_journal.mois) <= 12 else 'INCONNU',
                'annee': first_journal.annee
            }
        
        # Calculate effectif
        recap_data['totals']['effectif'] = len(journals.mapped('employe_id'))
        
        # Prepare gains mapping - both from salary components and indemnities
        gains_mapping = {}
        
        # Standard salary components (hardcoded)
        if sum(journals.mapped('salaire_base')):
            gains_mapping['10'] = {
                'code': '10',
                'designation': 'SALAIRE DE BASE',
                'montant': sum(journals.mapped('salaire_base'))
            }
        
        # Process indemnities from employee appointments and pointage
        indemnites_gains = {}
        
        for journal in journals:
            # From employee appointments (app_ids)
            if journal.employe_id and journal.employe_id.app_ids:
                for appointment in journal.employe_id.app_ids:
                    if appointment.indemnite_id.type_ind == 'gain':
                        code = appointment.indemnite_id.code or appointment.indemnite_id.codeir
                        if code:
                            if code not in indemnites_gains:
                                indemnites_gains[code] = {
                                    'code': code,
                                    'designation': appointment.indemnite_id.des_indem.upper(),
                                    'montant': 0.0
                                }
                            
                            # Calculate amount (same logic as in bulletin)
                            nbr_j = journal.jours_normaux or 0
                            nbr_j_conge = journal.jours_conge or 0
                            mult = (nbr_j + nbr_j_conge) if appointment.indemnite_id.j else 1
                            amount = appointment.montant * mult
                            indemnites_gains[code]['montant'] += amount
            
            # From pointage indemnities (if bulletin exists and has pointage)
            if journal.bulletin_id and journal.bulletin_id.pointagem_id:
                pointage = journal.bulletin_id.pointagem_id
                for ind_point in pointage.ind_point_ids:
                    if ind_point.indemnite_id.type_ind == 'gain':
                        code = ind_point.indemnite_id.code or ind_point.indemnite_id.codeir
                        if code:
                            if code not in indemnites_gains:
                                indemnites_gains[code] = {
                                    'code': code,
                                    'designation': ind_point.indemnite_id.des_indem.upper(),
                                    'montant': 0.0
                                }
                            
                            # Calculate amount
                            nbr_j = journal.jours_normaux or 0
                            nbr_j_conge = journal.jours_conge or 0
                            mult = (nbr_j + nbr_j_conge) if ind_point.indemnite_id.j else 1
                            amount = ind_point.montant * mult
                            indemnites_gains[code]['montant'] += amount
        
        # Add indemnities to gains mapping
        gains_mapping.update(indemnites_gains)
        
        # Add special calculated items
        total_salaire_base = sum(journals.mapped('salaire_base'))
        total_indemnites = sum([item['montant'] for item in indemnites_gains.values()])
        
        if total_salaire_base + total_indemnites:
            gains_mapping['205'] = {
                'code': '205',
                'designation': 'SALAIRE BRUT',
                'montant': total_salaire_base + total_indemnites
            }
        
        # Process retenues (deductions)
        retenues_mapping = {}
        
        # Standard deductions with codes
        deductions = [
            ('210', 'COTISATION CNSS', 'cnss_salarie'),
            ('213', "Cotisation à l'indemnité pour perte d'emploi", None),  # Not in current model
            ('219', 'ASSURANCE MALADIE OBLIGATOIRE', 'amo_salarie'),
            ('225', 'IMPOT SUR LE REVENU', 'impot_revenu'),
        ]
        
        for code, designation, field_name in deductions:
            if field_name:
                total_amount = sum(journals.mapped(field_name))
                if total_amount:
                    retenues_mapping[code] = {
                        'code': code,
                        'designation': designation,
                        'montant': total_amount
                    }
        
        # Process other retenues from indemnities
        indemnites_retenues = {}
        
        for journal in journals:
            # From employee appointments
            if journal.employe_id and journal.employe_id.app_ids:
                for appointment in journal.employe_id.app_ids:
                    if appointment.indemnite_id.type_ind == 'retenu':
                        code = appointment.indemnite_id.code or appointment.indemnite_id.codeir
                        if code:
                            if code not in indemnites_retenues:
                                indemnites_retenues[code] = {
                                    'code': code,
                                    'designation': appointment.indemnite_id.des_indem.upper(),
                                    'montant': 0.0
                                }
                            
                            # Calculate amount
                            nbr_j = journal.jours_normaux or 0
                            nbr_j_conge = journal.jours_conge or 0
                            mult = (nbr_j + nbr_j_conge) if appointment.indemnite_id.j else 1
                            amount = appointment.montant * mult
                            indemnites_retenues[code]['montant'] += amount
            
            # From pointage indemnities
            if journal.bulletin_id and journal.bulletin_id.pointagem_id:
                pointage = journal.bulletin_id.pointagem_id
                for ind_point in pointage.ind_point_ids:
                    if ind_point.indemnite_id.type_ind == 'retenu':
                        code = ind_point.indemnite_id.code or ind_point.indemnite_id.codeir
                        if code:
                            if code not in indemnites_retenues:
                                indemnites_retenues[code] = {
                                    'code': code,
                                    'designation': ind_point.indemnite_id.des_indem.upper(),
                                    'montant': 0.0
                                }
                            
                            # Calculate amount
                            nbr_j = journal.jours_normaux or 0
                            nbr_j_conge = journal.jours_conge or 0
                            mult = (nbr_j + nbr_j_conge) if ind_point.indemnite_id.j else 1
                            amount = ind_point.montant * mult
                            indemnites_retenues[code]['montant'] += amount
        
        # Add indemnities retenues to retenues mapping
        retenues_mapping.update(indemnites_retenues)
        
        # Sort and prepare final lists
        recap_data['gains'] = sorted(gains_mapping.values(), key=lambda x: x['code'])
        recap_data['retenues'] = sorted(retenues_mapping.values(), key=lambda x: x['code'])
        
        # Calculate totals
        recap_data['totals']['total_gains'] = sum([item['montant'] for item in recap_data['gains']])
        recap_data['totals']['total_retenues'] = sum([item['montant'] for item in recap_data['retenues']])
        recap_data['totals']['net_a_payer'] = sum(journals.mapped('net_a_payer'))
        
        return {
            'success': True,
            'message': f"Récapitulatif généré avec succès pour {len(journals)} journal(aux)",
            'data': recap_data
        }

    def action_generate_journal_recap(self):
        """Action method to generate and display journal recap"""
        # Use self.ids if called from list view, otherwise use context
        journal_ids = self.ids if self else self.env.context.get('active_ids', [])
        
        if not journal_ids:
            # If no specific journals selected, get all current journals
            journals = self.search([])
            journal_ids = journals.ids
        
        if not journal_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Aucun Journal',
                    'message': 'Aucun journal trouvé pour générer le récapitulatif.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Generate recap data and store it in context
        result = self.generate_journal_recap(journal_ids=journal_ids)
        
        if not result['success']:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur de Génération',
                    'message': result['message'],
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        # Try to find the report action
        try:
            report_action = self.env.ref('softy_hr.report_journal_recap_document')
            return report_action.with_context(recap_data=result['data']).report_action(self.browse(journal_ids))
        except ValueError:
            # If report not found, show error message
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur de Rapport',
                    'message': 'Le rapport de récapitulatif n\'est pas configuré correctement. Vérifiez que le fichier XML est bien chargé.',
                    'type': 'danger',
                    'sticky': True,
                }
            }
    def test_recap_data(self):
        """Simple test method to check if recap generation works"""
        journal_ids = self.ids if self else []
        if not journal_ids:
            journals = self.search([], limit=5)  # Get first 5 journals for testing
            journal_ids = journals.ids
            
        result = self.generate_journal_recap(journal_ids=journal_ids)
        
        # Show the data structure for debugging
        gains_count = len(result.get('data', {}).get('gains', []))
        retenues_count = len(result.get('data', {}).get('retenues', []))
        effectif = result.get('data', {}).get('totals', {}).get('effectif', 0)
        
        message = f"""
Test Récapitulatif:
- Succès: {result['success']}
- Message: {result['message']}
- Gains trouvés: {gains_count}
- Retenues trouvées: {retenues_count}
- Effectif: {effectif}
        """
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test Récapitulatif',
                'message': message,
                'type': 'success' if result['success'] else 'warning',
                'sticky': True,
            }
        }

    def debug_show_recap_data(self):
        """Debug method to show raw recap data"""
        journal_ids = self.ids if self else []
        if not journal_ids:
            journals = self.search([], limit=3)
            journal_ids = journals.ids
            
        result = self.generate_journal_recap(journal_ids=journal_ids)
        
        if result['success']:
            data = result['data']
            import json
            
            # Format the data for display
            debug_info = {
                'effectif': data.get('totals', {}).get('effectif', 0),
                'total_gains': data.get('totals', {}).get('total_gains', 0),
                'total_retenues': data.get('totals', {}).get('total_retenues', 0),
                'gains_items': len(data.get('gains', [])),
                'retenues_items': len(data.get('retenues', [])),
                'company_name': data.get('company_info', {}).get('name', 'N/A'),
                'period': f"{data.get('period_info', {}).get('mois', 'N/A')} {data.get('period_info', {}).get('annee', 'N/A')}"
            }
            
            message = f"Debug Info:\n{json.dumps(debug_info, indent=2)}"
        else:
            message = f"Erreur: {result['message']}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Debug Récapitulatif',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }    
    