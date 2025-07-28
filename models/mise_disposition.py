import calendar
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MiseDisposition(models.Model):
    _name = 'softy.mad'
    _description = 'Mise a Disposition'
    _rec_name = 'ref'

    bulletin_id = fields.Many2one(
        comodel_name="softy.bulletin",
        string="Bulletin de paie",
        required=False,  # Changed from True
        ondelete='set null'  # Changed from 'cascade'
    )

    # CHANGED: Convert from related field to regular stored field
    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string='Employé',
        store=True,
        readonly=True
    )
    
    ref = fields.Char(string='Réf. Mise à Disposition', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    
    # CHANGED: Convert all related fields to regular stored fields
    banque = fields.Char(
        string='Banque',
        store=True,
        readonly=True
    )
    
    agent = fields.Char(
        string='Agent',
        store=True,
        readonly=True
    )
    
    montant = fields.Float(
        string='Montant',
        store=True,
        readonly=True,
        digits=(10, 2)
    )

    # Computed field for amount in words
    montant_en_lettres = fields.Char(
        string='Montant en Lettres',
        compute='_compute_montant_en_lettres',
        store=True
    )

    # Filter fields for easy search - CHANGED: Convert from related fields
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

    societe_id = fields.Many2one(
        comodel_name="softy.societe",
        string="Société",
        store=True,
        readonly=True
    )

    departement_id = fields.Many2one(
        comodel_name="softy.departement",
        string="Département",
        store=True,
        readonly=True
    )

    service_id = fields.Many2one(
        comodel_name="softy.service",
        string="Service",
        store=True,
        readonly=True
    )

    # Add payment mode for filtering - CHANGED: Convert from related field
    mode_payment = fields.Selection(
        string="Mode de Paiement",
        selection=[
            ('vir', 'Virement'),
            ('esp', 'Espèces'),
            ('che', 'Chèque'),
            ('Mise a Disposition', 'Mise à Disposition'),
        ],
        store=True,
        readonly=True
    )

    _sql_constraints = [
        ('ref_uniq', 'unique(ref)', 'La référence du document doit être unique.'),
    ]

    @api.model
    def create(self, vals):
        """Override create to populate fields from bulletin when MAD is created"""
        if 'bulletin_id' in vals and vals['bulletin_id']:
            bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
            if bulletin.exists():
                # Populate all the fields from bulletin at creation time
                vals.update({
                    'employe_id': bulletin.employe_id.id if bulletin.employe_id else False,
                    'banque': bulletin.societe_id.banque_id.name if bulletin.societe_id and bulletin.societe_id.banque_id else False,
                    'agent': bulletin.departement_id.agent if bulletin.departement_id else False,
                    'montant': bulletin.salaire_net_payer,
                    'mois': bulletin.mois,
                    'annee': bulletin.annee,
                    'societe_id': bulletin.societe_id.id if bulletin.societe_id else False,
                    'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                    'service_id': bulletin.service_id.id if bulletin.service_id else False,
                    'mode_payment': bulletin.employe_id.mode_payment if bulletin.employe_id else False,
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
                        'banque': bulletin.societe_id.banque_id.name if bulletin.societe_id and bulletin.societe_id.banque_id else False,
                        'agent': bulletin.departement_id.agent if bulletin.departement_id else False,
                        'montant': bulletin.salaire_net_payer,
                        'mois': bulletin.mois,
                        'annee': bulletin.annee,
                        'societe_id': bulletin.societe_id.id if bulletin.societe_id else False,
                        'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                        'service_id': bulletin.service_id.id if bulletin.service_id else False,
                        'mode_payment': bulletin.employe_id.mode_payment if bulletin.employe_id else False,
                    })
            # If bulletin_id is set to False/None, keep existing stored values
        
        return super().write(vals)

    @api.depends('montant')
    def _compute_montant_en_lettres(self):
        for record in self:
            if record.montant:
                record.montant_en_lettres = record._amount_to_words_french(record.montant)
            else:
                record.montant_en_lettres = "ZÉRO DIRHAMS"

    def _amount_to_words_french(self, amount):
        """Convert amount to French words"""
        if not amount:
            return "ZÉRO DIRHAMS"
        
        # Separate integer and decimal parts
        amount_int = int(amount)
        amount_cents = int(round((amount - amount_int) * 100))
        
        # Convert integer part to words
        words = self._number_to_words_french(amount_int)
        
        # Add currency
        if amount_int <= 1:
            words += " DIRHAM"
        else:
            words += " DIRHAMS"
        
        # Add cents if any
        if amount_cents > 0:
            cents_words = self._number_to_words_french(amount_cents)
            if amount_cents <= 1:
                words += f" ET {cents_words} CENTIME"
            else:
                words += f" ET {cents_words} CENTIMES"
        
        return words

    def _number_to_words_french(self, number):
        """Convert a number to French words"""
        if number == 0:
            return "ZÉRO"
        
        # Basic numbers 0-19
        ones = ["", "UN", "DEUX", "TROIS", "QUATRE", "CINQ", "SIX", "SEPT", "HUIT", "NEUF",
                "DIX", "ONZE", "DOUZE", "TREIZE", "QUATORZE", "QUINZE", "SEIZE", 
                "DIX-SEPT", "DIX-HUIT", "DIX-NEUF"]
        
        # Tens
        tens = ["", "", "VINGT", "TRENTE", "QUARANTE", "CINQUANTE", "SOIXANTE", 
                "SOIXANTE", "QUATRE-VINGT", "QUATRE-VINGT"]
        
        def convert_hundreds(n):
            result = ""
            
            # Hundreds
            if n >= 100:
                hundreds = n // 100
                if hundreds == 1:
                    result += "CENT"
                else:
                    result += ones[hundreds] + " CENT"
                    if n % 100 == 0:
                        result += "S"
                n %= 100
                if n > 0:
                    result += " "
            
            # Tens and ones
            if n >= 20:
                tens_digit = n // 10
                ones_digit = n % 10
                
                if tens_digit == 7:  # 70-79
                    result += "SOIXANTE"
                    if ones_digit == 1:
                        result += "-ET-ONZE"
                    elif ones_digit > 1:
                        result += "-" + ones[10 + ones_digit]
                elif tens_digit == 9:  # 90-99
                    result += "QUATRE-VINGT"
                    if ones_digit == 1:
                        result += "-ONZE"
                    elif ones_digit > 1:
                        result += "-" + ones[10 + ones_digit]
                else:
                    result += tens[tens_digit]
                    if ones_digit == 1 and tens_digit != 8:
                        result += "-ET-UN"
                    elif ones_digit == 1 and tens_digit == 8:
                        result += "-UN"
                    elif ones_digit > 1:
                        result += "-" + ones[ones_digit]
            else:
                result += ones[n]
            
            return result
        
        def convert_thousands(n):
            if n < 1000:
                return convert_hundreds(n)
            
            thousands = n // 1000
            remainder = n % 1000
            
            result = ""
            if thousands == 1:
                result = "MILLE"
            else:
                result = convert_hundreds(thousands) + " MILLE"
            
            if remainder > 0:
                result += " " + convert_hundreds(remainder)
            
            return result
        
        def convert_millions(n):
            if n < 1000000:
                return convert_thousands(n)
            
            millions = n // 1000000
            remainder = n % 1000000
            
            result = ""
            if millions == 1:
                result = "UN MILLION"
            else:
                result = convert_hundreds(millions) + " MILLIONS"
            
            if remainder > 0:
                result += " " + convert_thousands(remainder)
            
            return result
        
        return convert_millions(number)

    def generate_mad_from_bulletins(self):
        """Generate Mise à Disposition records from bulletins where employee payment mode is 'Mise a Disposition' only"""
        # Filter bulletins to only include those where employee mode_payment is 'Mise a Disposition'
        bulletins = self.env['softy.bulletin'].search([
            ('employe_id.mode_payment', '=', 'Mise a Disposition')
        ])
        
        created_count = 0
        skipped_count = 0
        
        for bulletin in bulletins:
            # Check if MAD already exists for this bulletin
            existing_mad = self.search([('bulletin_id', '=', bulletin.id)])
            if not existing_mad:
                # Generate reference automatically
                ref = f"MAD-{bulletin.employe_id.matricule or 'UNKNOWN'}-{bulletin.mois}/{bulletin.annee}"
                
                self.create({
                    'bulletin_id': bulletin.id,
                    'ref': ref,
                    'date': fields.Date.context_today(self),
                })
                created_count += 1
            else:
                skipped_count += 1
        
        # Count total bulletins for context
        total_bulletins = self.env['softy.bulletin'].search_count([])
        mad_bulletins = len(bulletins)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Génération Mise à Disposition',
                'message': f'{created_count} enregistrements MAD créés avec succès.\n'
                          f'{skipped_count} déjà existants.\n'
                          f'Traités: {mad_bulletins} bulletins avec mode "Mise à Disposition" sur {total_bulletins} bulletins totaux.',
                'type': 'success',
                'sticky': False,
            }
        }