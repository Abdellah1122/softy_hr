from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Contrat(models.Model):
    _name = 'softy.contrat'
    _description = 'Contrat'
    _rec_name = 'ref'

    employe_id = fields.Many2one(
        'softy.employe',
        string='Employé',
        required=True,
        ondelete='cascade'
    )

    ref = fields.Char(string='Réf. Contrat')
    date_debut = fields.Date(string="Date Début")
    date_fin = fields.Date(string="Date Fin")
    date_signature = fields.Date(string="Date de Signature")
    debut_administration = fields.Date(string="Début Administration")
    debut_anciennete = fields.Date(string="Début Ancienneté")
    
    duree_mois = fields.Integer(
        string="Durée (mois)",
        compute="_compute_duree_mois",
        store=True,
    )
    
    salaire = fields.Float(string="Salaire", required=True)
    
    periodicite = fields.Selection([
        ('semaine', 'Semaine'),
        ('quinzaine', 'Quinzaine'),
        ('mois', 'Mois Entier'),
    ], string='Périodicité', required=True, default='mois')
    
    type_payment = fields.Selection([
        ('mensuel', 'Mensuel'),
        ('horaire', 'Horaire'),
    ], string='Type de paiement', required=True, default='mensuel')
    
    type_contrat = fields.Selection([
        ('cdd', 'CDD'),
        ('anapec', 'Anapec'),
        ('cdd3', 'CDD 3 Mois'),
        ('cdd2', 'CDD 2 Mois'),
        ('cdd6', 'CDD 6 Mois'),
        ('cdd11', 'CDD 11 Mois'),
        ('cdi', 'CDI'),
        ('cdt', 'Contrat à Durée de Tâche'),
    ], string='Type de contrat', required=True)

    _sql_constraints = [
        ('ref_uniq', 'unique(ref)', 'La référence du contrat doit être unique.'),
        ('employe_uniq', 'unique(employe_id)', 'Un employé ne peut avoir qu\'un seul contrat.'),
        ('salaire_positive', 'check(salaire > 0)', 'Le salaire doit être positif.'),
    ]

    @api.model
    def create(self, vals):
        """Override create to automatically link contract to employee"""
        # Create the contract first
        contract = super(Contrat, self).create(vals)
        
        # Automatically set this contract to the employee
        if contract.employe_id:
            # Remove any existing contract from the employee first
            if contract.employe_id.contrat_id and contract.employe_id.contrat_id.id != contract.id:
                old_contract = contract.employe_id.contrat_id
                # This will trigger a constraint error if there's already a contract
                # But we handle it gracefully
                pass
            
            # Link the contract to the employee
            contract.employe_id.write({'contrat_id': contract.id})
        
        return contract

    @api.model_create_multi
    def create(self, vals_list):
        """Alternative create method for multiple records"""
        contracts = super(Contrat, self).create(vals_list)
        
        for contract in contracts:
            if contract.employe_id:
                # Link the contract to the employee
                contract.employe_id.write({'contrat_id': contract.id})
        
        return contracts

    def write(self, vals):
        """Override write to handle employee changes"""
        # Store old employee_id before update
        old_employes = {}
        for contract in self:
            if contract.employe_id:
                old_employes[contract.id] = contract.employe_id
        
        # Perform the write operation
        result = super(Contrat, self).write(vals)
        
        # Handle employee changes after write
        if 'employe_id' in vals:
            for contract in self:
                # Remove contract from old employee if it exists
                old_employe = old_employes.get(contract.id)
                if old_employe and old_employe.exists():
                    # Only remove if the old employee's contract is this contract
                    if old_employe.contrat_id and old_employe.contrat_id.id == contract.id:
                        old_employe.write({'contrat_id': False})
                
                # Set contract to new employee
                if contract.employe_id:
                    # Remove any existing contract from the new employee
                    if contract.employe_id.contrat_id and contract.employe_id.contrat_id.id != contract.id:
                        # The new employee already has a different contract
                        # The unique constraint will handle this, but we can also handle it here
                        pass
                    
                    contract.employe_id.write({'contrat_id': contract.id})
        
        return result

    def unlink(self):
        """Override unlink to remove contract reference from employee"""
        # Store employees before deletion
        employes_to_update = []
        for contract in self:
            if contract.employe_id and contract.employe_id.contrat_id == contract:
                employes_to_update.append(contract.employe_id)
        
        # Delete the contracts
        result = super(Contrat, self).unlink()
        
        # Remove contract reference from employees
        for employe in employes_to_update:
            if employe.exists():
                employe.write({'contrat_id': False})
        
        return result

    @api.depends('date_debut', 'date_fin')
    def _compute_duree_mois(self):
        for rec in self:
            if rec.date_debut and rec.date_fin:
                # Calculer la différence en mois
                delta = relativedelta(rec.date_fin, rec.date_debut)
                rec.duree_mois = delta.months + (delta.years * 12)
            else:
                rec.duree_mois = 0

    @api.onchange('type_contrat', 'date_debut')
    def _onchange_type_contrat_date_debut(self):
        """
        Calcule automatiquement la date de fin selon le type de contrat et la date de début
        """
        if self.date_debut and self.type_contrat:
            if self.type_contrat == 'cdd3':
                # CDD 3 mois: date_fin = date_debut + 3 mois
                self.date_fin = self.date_debut + relativedelta(months=3)
            elif self.type_contrat == 'cdd2':
                # CDD 2 mois: date_fin = date_debut + 2 mois
                self.date_fin = self.date_debut + relativedelta(months=2)
            elif self.type_contrat == 'cdd6':
                # CDD 6 mois: date_fin = date_debut + 6 mois
                self.date_fin = self.date_debut + relativedelta(months=6)
            elif self.type_contrat == 'cdd11':
                # CDD 11 mois: date_fin = date_debut + 11 mois
                self.date_fin = self.date_debut + relativedelta(months=11)
            elif self.type_contrat in ['cdi', 'cdt']:
                # CDI et Contrat à Durée de Tâche: pas de date de fin automatique
                self.date_fin = False
            # Pour les autres types (cdd, anapec), on laisse l'utilisateur saisir manuellement

    @api.constrains('date_debut', 'date_fin', 'type_contrat')
    def _check_dates(self):
        for rec in self:
            if rec.date_fin and rec.date_debut and rec.date_fin < rec.date_debut:
                raise ValidationError("La date de fin doit être postérieure à la date de début.")
            
            # Validation spécifique pour les CDD avec durée fixe
            if rec.type_contrat == 'cdd3' and rec.date_debut and rec.date_fin:
                expected_date_fin = rec.date_debut + relativedelta(months=3)
                if rec.date_fin != expected_date_fin:
                    raise ValidationError(f"Pour un CDD 3 mois, la date de fin doit être exactement 3 mois après la date de début ({expected_date_fin.strftime('%d/%m/%Y')}).")
            
            elif rec.type_contrat == 'cdd2' and rec.date_debut and rec.date_fin:
                expected_date_fin = rec.date_debut + relativedelta(months=2)
                if rec.date_fin != expected_date_fin:
                    raise ValidationError(f"Pour un CDD 2 mois, la date de fin doit être exactement 2 mois après la date de début ({expected_date_fin.strftime('%d/%m/%Y')}).")
            
            elif rec.type_contrat == 'cdd6' and rec.date_debut and rec.date_fin:
                expected_date_fin = rec.date_debut + relativedelta(months=6)
                if rec.date_fin != expected_date_fin:
                    raise ValidationError(f"Pour un CDD 6 mois, la date de fin doit être exactement 6 mois après la date de début ({expected_date_fin.strftime('%d/%m/%Y')}).")
            
            elif rec.type_contrat == 'cdd11' and rec.date_debut and rec.date_fin:
                expected_date_fin = rec.date_debut + relativedelta(months=11)
                if rec.date_fin != expected_date_fin:
                    raise ValidationError(f"Pour un CDD 11 mois, la date de fin doit être exactement 11 mois après la date de début ({expected_date_fin.strftime('%d/%m/%Y')}).")

    @api.constrains('date_signature', 'date_debut')
    def _check_date_signature(self):
        for rec in self:
            if rec.date_signature and rec.date_debut and rec.date_signature > rec.date_debut:
                raise ValidationError("La date de signature ne peut pas être postérieure à la date de début du contrat.")

    @api.constrains('debut_administration', 'date_debut')
    def _check_debut_administration(self):
        for rec in self:
            if rec.debut_administration and rec.date_debut and rec.debut_administration < rec.date_debut:
                raise ValidationError("Le début d'administration ne peut pas être antérieur à la date de début du contrat.")

    @api.constrains('debut_anciennete', 'date_debut')
    def _check_debut_anciennete(self):
        for rec in self:
            if rec.debut_anciennete and rec.date_debut and rec.debut_anciennete > rec.date_debut:
                raise ValidationError("Le début d'ancienneté ne peut pas être postérieur à la date de début du contrat.")