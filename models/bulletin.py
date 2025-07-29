import calendar
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class Bulletin(models.Model):
    _name = 'softy.bulletin'
    _description = 'Bulletin de Paie'
    _rec_name = 'lib'
    _order = 'pointagem_id desc'

    lib = fields.Char(string="Libellé", compute="_compute_lib", store=True)
    
    pointagem_id = fields.Many2one(
        comodel_name="softy.pointagem", 
        string="Pointage Mensuel", 
        required=False,
        ondelete='set null'
    )

    # CRITICAL CHANGE: Make these regular fields instead of related fields
    # This way they will be stored permanently even when pointage is deleted
    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string='Employé',
        store=True,
        readonly=True
    )
    
    mois = fields.Selection(
        selection=[(str(i), calendar.month_name[i]) for i in range(1,13)],
        string='Mois',
        store=True,
        readonly=True
    )
    
    annee = fields.Integer(
        string='Année',
        store=True,
        readonly=True
    )

    # Related fields from pointage - also make these regular stored fields
    nbr_j = fields.Integer(
        string='Jours travaillés',
        store=True,
        readonly=True
    )
    
    nbr_j_conge = fields.Integer(
        string='Jours congé',
        store=True,
        readonly=True
    )

    # Période field - also make regular stored field
    periode = fields.Selection(
        selection=[('current', 'Mois Actuel'), ('previous', 'Mois Précédent')],
        string='Période',
        store=True,
        readonly=True
    )

    # Keep computed fields as they are
    salaire_brut = fields.Float(
        string="Salaire Brut", 
        compute="_compute_salaire_brut",
        store=True,
        digits=(10, 2)
    )
    
    salaire_brut_imp = fields.Float(
        string="Salaire Brut Imposable", 
        compute="_compute_salaire_brut_imposable",
        store=True,
        digits=(10, 2)
    )
    
    taux_fp = fields.Float(
        string="Taux Frais Professionnels (%)", 
        compute="_compute_taux_fp",
        store=True,
        digits=(5, 2)
    )
    
    total_cotisation = fields.Float(
        string="Total des Cotisations", 
        compute="_compute_total_cotisation",
        store=True,
        digits=(10, 2)
    )
    
    frais_pro = fields.Float(
        string="Frais Professionnels", 
        compute="_compute_frais_pro",
        store=True,
        digits=(10, 2)
    )
    
    salaire_net_imp = fields.Float(
        string="Salaire Net Imposable", 
        compute="_compute_salaire_net_imp",
        store=True,
        digits=(10, 2)
    )
    
    taux_ir = fields.Float(
        string="Taux Impôt sur Revenu (%)", 
        compute="_compute_taux_ir",
        store=True,
        digits=(5, 2)
    )
    
    deduction_fiscale = fields.Float(
        string="Déduction Fiscale",
        compute="_compute_deduction_fiscale",
        store=True,
        digits=(10, 2)
    )
    
    deduction_charge_famille = fields.Float(
        string="Déduction Charges de Famille",
        compute="_compute_deduction_charge_famille",
        store=True,
        digits=(10, 2)
    )
    
    ir = fields.Float(
        string="Impôt sur Revenu", 
        compute="_compute_ir",
        store=True,
        digits=(10, 2)
    )
    
    salaire_net_payer = fields.Float(
        string="Salaire Net à Payer", 
        compute="_compute_salaire_net_payer",
        store=True,
        digits=(10, 2)
    )

    indemnites_imposables = fields.Float(
        string="Indemnités Imposables",
        compute="_compute_indemnites_detail",
        store=True,
        digits=(10, 2)
    )
    
    indemnites_non_imposables = fields.Float(
        string="Indemnités Non Imposables",
        compute="_compute_indemnites_detail",
        store=True,
        digits=(10, 2)
    )

    # Computed fields for proper grouping and search - make these regular stored fields too
    service_id = fields.Many2one(
        comodel_name="softy.service",
        string='Service',
        store=True,
        readonly=True
    )
    
    departement_id = fields.Many2one(
        comodel_name="softy.departement", 
        string='Département',
        store=True,
        readonly=True
    )
    
    societe_id = fields.Many2one(
        comodel_name="softy.societe",
        string='Société',
        store=True,
        readonly=True
    )

    _sql_constraints = [
        ('unique_bulletin_per_pointage', 'UNIQUE(pointagem_id)', "Un bulletin existe déjà pour ce pointage mensuel."),
    ]

    @api.model
    def create(self, vals):
        """Override create to populate fields from pointage when bulletin is created"""
        if 'pointagem_id' in vals and vals['pointagem_id']:
            pointage = self.env['softy.pointagem'].browse(vals['pointagem_id'])
            if pointage.exists():
                # Populate all the fields from pointage at creation time
                vals.update({
                    'employe_id': pointage.employe_id.id,
                    'mois': pointage.mois,
                    'annee': pointage.annee,
                    'nbr_j': pointage.nbr_j,
                    'nbr_j_conge': pointage.nbr_j_conge,
                    'periode': pointage.periode,
                    'service_id': pointage.employe_id.service_id.id if pointage.employe_id.service_id else False,
                    'departement_id': pointage.employe_id.service_id.departement_id.id if pointage.employe_id.service_id and pointage.employe_id.service_id.departement_id else False,
                    'societe_id': pointage.employe_id.service_id.departement_id.societe_id.id if pointage.employe_id.service_id and pointage.employe_id.service_id.departement_id and pointage.employe_id.service_id.departement_id.societe_id else False,
                })
        
        return super().create(vals)

    def write(self, vals):
        """Override write to update fields when pointage changes"""
        if 'pointagem_id' in vals:
            if vals['pointagem_id']:
                pointage = self.env['softy.pointagem'].browse(vals['pointagem_id'])
                if pointage.exists():
                    # Update all the fields from new pointage
                    vals.update({
                        'employe_id': pointage.employe_id.id,
                        'mois': pointage.mois,
                        'annee': pointage.annee,
                        'nbr_j': pointage.nbr_j,
                        'nbr_j_conge': pointage.nbr_j_conge,
                        'periode': pointage.periode,
                        'service_id': pointage.employe_id.service_id.id if pointage.employe_id.service_id else False,
                        'departement_id': pointage.employe_id.service_id.departement_id.id if pointage.employe_id.service_id and pointage.employe_id.service_id.departement_id else False,
                        'societe_id': pointage.employe_id.service_id.departement_id.societe_id.id if pointage.employe_id.service_id and pointage.employe_id.service_id.departement_id and pointage.employe_id.service_id.departement_id.societe_id else False,
                    })
            # If pointagem_id is set to False/None, keep existing stored values
        
        return super().write(vals)

    @api.depends('pointagem_id', 'employe_id', 'mois', 'annee')
    def _compute_lib(self):
        for rec in self:
            if rec.employe_id and rec.mois and rec.annee:
                month_num = int(rec.mois) if rec.mois else 1
                month_name = calendar.month_name[month_num]
                rec.lib = f"Bulletin {rec.employe_id.name} - {month_name}/{rec.annee}"
            elif rec.employe_id:
                rec.lib = f"Bulletin {rec.employe_id.name} - (Pointage supprimé)"
            else:
                rec.lib = "Bulletin orphelin"

    @api.depends(
        'pointagem_id.employe_id.taux_horaire',
        'pointagem_id.nbr_h',
        'pointagem_id.h_25',
        'pointagem_id.h_50',
        'pointagem_id.h_100',
        'pointagem_id.nbr_j',
        'pointagem_id.nbr_j_conge',
        'pointagem_id.ind_point_ids.montant',
        'pointagem_id.ind_point_ids.indemnite_id.j',
        'employe_id.app_ids.montant',
        'employe_id.app_ids.indemnite_id.j',
    )
    def _compute_salaire_brut(self):
        for rec in self:
            # CRITICAL FIX: If pointage is deleted, don't recalculate - keep stored value
            if not rec.pointagem_id or not rec.pointagem_id.employe_id:
                # Don't reset to 0.0 - keep existing stored value
                continue

            # Partie 1: taux_horaire × nbr_h (heures normales)
            taux_horaire    = rec.pointagem_id.employe_id.taux_horaire or 0.0
            heures_normales = rec.pointagem_id.nbr_h or 0.0
            salaire_base    = taux_horaire * heures_normales

            # Heures supplémentaires
            heures_sup = (
                (rec.pointagem_id.h_25  * 1.25) +
                (rec.pointagem_id.h_50  * 1.50) +
                (rec.pointagem_id.h_100 * 2.00)
            ) * taux_horaire

            # Partie 2: total des indemnités via ind_point_ids (from pointage)
            total_indemnites_pointage = 0.0
            nbr_j = rec.pointagem_id.nbr_j or 0
            nbr_j_conge = rec.pointagem_id.nbr_j_conge or 0
            for line in rec.pointagem_id.ind_point_ids:
                # journalière? multiplier par nbr_j, sinon montant plat
                if line.indemnite_id.j:
                    total_indemnites_pointage += line.montant * (nbr_j + nbr_j_conge)
                else:
                    total_indemnites_pointage += line.montant

            # NEW: Partie 3: Indemnités from employee appointments (app_ids)
            total_indemnites_appointments = 0.0
            if rec.employe_id and rec.employe_id.app_ids:
                for appointment in rec.employe_id.app_ids:
                    # journalière? multiplier par nbr_j + nbr_j_conge, sinon montant plat
                    if appointment.indemnite_id.j:
                        total_indemnites_appointments += appointment.montant * (nbr_j + nbr_j_conge)
                    else:
                        total_indemnites_appointments += appointment.montant

            rec.salaire_brut = salaire_base + heures_sup + total_indemnites_pointage + total_indemnites_appointments

    @api.depends(
        'pointagem_id.nbr_j',
        'pointagem_id.nbr_j_conge',
        'pointagem_id.ind_point_ids.montant',
        'pointagem_id.ind_point_ids.indemnite_id.j',
        'pointagem_id.ind_point_ids.indemnite_id.imposable',
        'employe_id.app_ids.montant',
        'employe_id.app_ids.indemnite_id.j',
        'employe_id.app_ids.indemnite_id.imposable',
    )
    def _compute_indemnites_detail(self):
        for rec in self:
            # CRITICAL FIX: If pointage is deleted, don't recalculate - keep stored values
            if not rec.pointagem_id:
                # Don't reset to 0.0 - keep existing stored values
                continue
                
            total_imp = 0.0
            total_non = 0.0
            
            # Part 1: Indemnités from pointage (existing logic)
            lines = rec.pointagem_id.ind_point_ids or ()
            for line in lines:
                # if journalière, multiply by nbr_j + nbr_j_conge; otherwise flat montant
                mult = (rec.pointagem_id.nbr_j + rec.pointagem_id.nbr_j_conge) if line.indemnite_id.j else 1
                amt  = line.montant * mult
                if line.indemnite_id.imposable:
                    total_imp += amt
                else:
                    total_non += amt

            # NEW: Part 2: Indemnités from employee appointments
            if rec.employe_id and rec.employe_id.app_ids:
                for appointment in rec.employe_id.app_ids:
                    # if journalière, multiply by nbr_j + nbr_j_conge; otherwise flat montant
                    mult = (rec.pointagem_id.nbr_j + rec.pointagem_id.nbr_j_conge) if appointment.indemnite_id.j else 1
                    amt = appointment.montant * mult
                    if appointment.indemnite_id.imposable:
                        total_imp += amt
                    else:
                        total_non += amt
            
            rec.indemnites_imposables     = total_imp
            rec.indemnites_non_imposables = total_non

    @api.depends('salaire_brut', 'indemnites_non_imposables')
    def _compute_salaire_brut_imposable(self):
        for rec in self:
            # Salaire brut Imposable = Salaire brut - somme(indemnite.nonimposable.montant * pointage.nbr_jours)
            rec.salaire_brut_imp = rec.salaire_brut - rec.indemnites_non_imposables

    @api.depends('salaire_brut_imp')
    def _compute_taux_fp(self):
        for rec in self:
            sbi = rec.salaire_brut_imp
            if sbi <= 6500:
                rec.taux_fp = 35.0
            else:
                rec.taux_fp = 25.0

    @api.depends('salaire_brut_imp', 'pointagem_id')
    def _compute_total_cotisation(self):
        """FIXED: Proper cotisation calculation for Moroccan payroll"""
        for rec in self:
            # CRITICAL FIX: If pointage is deleted, don't recalculate - keep stored value
            if not rec.pointagem_id or not rec.pointagem_id.employe_id or not rec.pointagem_id.employe_id.affiliation_ids:
                # Don't reset to 0.0 - keep existing stored value
                continue
                
            total = 0.0
            debug_info = []
            
            debug_info.append(f"=== COTISATION DEBUG for {rec.employe_id.name} ===")
            debug_info.append(f"Salaire Brut Imposable: {rec.salaire_brut_imp} MAD")
            
            for affiliation in rec.pointagem_id.employe_id.affiliation_ids:
                # CRITICAL FIX: Convert percentage to decimal
                taux_percentage = affiliation.aff_type_id.taux or 0.0
                taux_decimal = taux_percentage / 100.0  # Convert 4.48% to 0.0448
                
                plafond = affiliation.aff_type_id.plafond or 0.0
                
                # Handle plafond logic
                if plafond <= 0:
                    # No ceiling (unlimited)
                    base_cotisation = rec.salaire_brut_imp
                    plafond_str = "Illimité"
                else:
                    # Apply ceiling
                    base_cotisation = min(rec.salaire_brut_imp, plafond)
                    plafond_str = f"{plafond} MAD"
                
                # Calculate cotisation
                cotisation_amount = base_cotisation * taux_decimal
                total += cotisation_amount
                
                # Debug logging
                debug_info.append(
                    f"{affiliation.aff_type_id.name}: "
                    f"min({rec.salaire_brut_imp}, {plafond_str}) × {taux_percentage}% = "
                    f"{base_cotisation} × {taux_decimal:.4f} = {cotisation_amount:.2f} MAD"
                )
            
            debug_info.append(f"TOTAL COTISATIONS: {total:.2f} MAD")
            debug_info.append("=" * 50)
            
            # Log debug info (comment out in production)
            for line in debug_info:
                _logger.info(line)
            
            rec.total_cotisation = total

    @api.depends('salaire_brut_imp', 'taux_fp')
    def _compute_frais_pro(self):
        for rec in self:
            # frais professionels = min(salaire brut imposable * taux fp, 2916.67)
            frais_calcules = rec.salaire_brut_imp * (rec.taux_fp / 100)
            rec.frais_pro = min(frais_calcules, 2916.67)

    @api.depends('salaire_brut_imp', 'frais_pro', 'total_cotisation')
    def _compute_salaire_net_imp(self):
        for rec in self:
            # Salaire net imposable = salaire brut imposable - frais professionnels - cotisations
            rec.salaire_net_imp = rec.salaire_brut_imp - rec.frais_pro - rec.total_cotisation

    @api.depends('salaire_net_imp')
    def _compute_taux_ir(self):
        """
        Assigne, selon le salaire net imposable mensuel, 
        le taux IR correspondant au barème 2025.
        """
        for rec in self:
            sni = rec.salaire_net_imp or 0.0

            if sni <= 3333.33:
                rec.taux_ir = 0.0
            elif sni <= 5000.00:
                rec.taux_ir = 10.0
            elif sni <= 6666.67:
                rec.taux_ir = 20.0
            elif sni <= 8333.33:
                rec.taux_ir = 30.0
            elif sni <= 15000.00:
                rec.taux_ir = 34.0
            else:
                rec.taux_ir = 37.0

    @api.depends('salaire_net_imp')
    def _compute_deduction_fiscale(self):
        """
        Assigne la déduction fixe mensuelle à retrancher du
        montant brut IR pour chaque tranche du barème 2025.
        """
        for rec in self:
            sni = rec.salaire_net_imp or 0.0

            if sni <= 3333.33:
                rec.deduction_fiscale = 0.00
            elif sni <= 5000.00:
                rec.deduction_fiscale = 333.33
            elif sni <= 6666.67:
                rec.deduction_fiscale = 833.33
            elif sni <= 8333.33:
                rec.deduction_fiscale = 1500.00
            elif sni <= 15000.00:
                rec.deduction_fiscale = 1833.33
            else:
                rec.deduction_fiscale = 2283.33
    
    @api.depends('pointagem_id', 'employe_id')
    def _compute_deduction_charge_famille(self):
        for rec in self:
            # Use employe_id directly since it's now stored
            if rec.employe_id:
                nbr_enfants = rec.employe_id.nbr_enfant or 0
                rec.deduction_charge_famille = 45 * (nbr_enfants + 1)
            else:
                rec.deduction_charge_famille = 45.0

    @api.depends('salaire_net_imp', 'taux_ir', 'deduction_fiscale', 'deduction_charge_famille')
    def _compute_ir(self):
        for rec in self:
            # CORRECTION: Formule IR selon votre spécification
            # ir = (salaire net imposable * taux ir) - deduction fiscale - 45 * (employee.nbr enfant + 1)
            ir_brut = rec.salaire_net_imp * (rec.taux_ir / 100)
            rec.ir = max(0.0, ir_brut - rec.deduction_fiscale - rec.deduction_charge_famille)

    @api.depends('salaire_brut', 'total_cotisation', 'ir')
    def _compute_salaire_net_payer(self):
        for rec in self:
            # Salaire net a payer = salaire brut - cotisations - ir
            rec.salaire_net_payer = rec.salaire_brut - rec.total_cotisation - rec.ir

    def action_generate_bulletins_current_period(self):
        return self._generate_bulletins_for_period('current')

    def action_generate_bulletins_previous_period(self):
        return self._generate_bulletins_for_period('previous')

    def _generate_bulletins_for_period(self, period):
        pointages_sans_bulletin = self.env['softy.pointagem'].search([('periode', '=', period)])
        existing_bulletin_pointages = self.search([('pointagem_id', '!=', False)]).mapped('pointagem_id.id')
        pointages_to_process = pointages_sans_bulletin.filtered(lambda p: p.id not in existing_bulletin_pointages)
        
        period_name = "actuelle" if period == 'current' else "précédente"
        
        if not pointages_to_process:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Information',
                    'message': f"Aucun pointage sans bulletin trouvé pour la période {period_name}.",
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        bulletins_created = []
        errors = []
        
        for pointage in pointages_to_process:
            try:
                bulletin = self.create({'pointagem_id': pointage.id})
                bulletins_created.append(bulletin)
            except Exception as e:
                errors.append(f"Erreur pour {pointage.employe_id.name}: {str(e)}")
        
        total_created = len(bulletins_created)
        
        if total_created > 0:
            message = f"Génération réussie! {total_created} bulletin(s) créé(s) pour la période {period_name}"
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Génération des Bulletins',
                    'message': message,
                    'type': 'success',
                    'sticky': True,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur de Génération',
                    'message': f"Aucun bulletin n'a pu être créé pour la période {period_name}.",
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def action_view_pointage(self):
        if not self.pointagem_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Information',
                    'message': 'Le pointage associé à ce bulletin a été supprimé.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        return {
            'name': 'Pointage Mensuel',
            'type': 'ir.actions.act_window',
            'res_model': 'softy.pointagem',
            'res_id': self.pointagem_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_employe(self):
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

    def action_print_bulletin(self):
        return self.env.ref('softy_hr.bulletin_paie_report').report_action(self)