# models/simt.py
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import calendar

class Simt(models.Model):
    _name = 'softy.simt'
    _description = 'SIMT'

    bulletin_id = fields.Many2one(
        comodel_name="softy.bulletin",
        string="Bulletin de paie",
        required=False,  # Changed from True
        ondelete='set null'  # Add ondelete parameter
    )

    # CHANGED: Convert all related fields to regular stored fields
    employe_id = fields.Many2one(
        comodel_name="softy.employe",
        string='Employé',
        store=True,
        readonly=True
    )

    matricule = fields.Char(
        string="Matricule de l'employé",
        store=True,
        readonly=True
    )

    nom_complet = fields.Char(
        string="Nom complet de l'employé",
        store=True,
        readonly=True
    )

    n_acc_salarie = fields.Char(
        string="N° Compte Salarié",
        store=True,
        readonly=True,
        help="Code banque + agence + numéro compte"
    )

    montant_salarie = fields.Float(
        string="Montant payé au salarié",
        store=True,
        readonly=True
    )

    # Computed field for amount in centimes
    montant_centime = fields.Integer(
        string="Montant en centimes",
        compute='_compute_montant_centime',
        store=True
    )

    mois = fields.Selection(
        selection=[(str(i), calendar.month_name[i]) for i in range(1, 13)],
        string='Mois',
        store=True,
        readonly=True
    )

    annee = fields.Integer(
        string='Année',
        store=True,
        readonly=True
    )

    # Computed field for MM-AAAA format
    date_complete = fields.Char(
        string="Date complète (MM-AAAA)",
        compute='_compute_date_complete',
        store=True
    )

    # Filter fields - CHANGED: Convert from related fields to regular stored fields
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

    # Add mode_payment field for filtering - CHANGED: Convert from related field
    mode_payment = fields.Selection(
        string="Mode de Paiement",
        selection=[
            ('vir', 'Virement'),
            ('esp', 'Espèces'),
            ('che', 'Chèque'),
        ],
        store=True,
        readonly=True
    )

    @api.model
    def create(self, vals):
        """Override create to populate fields from bulletin when simt is created"""
        if 'bulletin_id' in vals and vals['bulletin_id']:
            bulletin = self.env['softy.bulletin'].browse(vals['bulletin_id'])
            if bulletin.exists():
                # Populate all the fields from bulletin at creation time
                vals.update({
                    'employe_id': bulletin.employe_id.id if bulletin.employe_id else False,
                    'matricule': bulletin.employe_id.matricule if bulletin.employe_id else False,
                    'nom_complet': bulletin.employe_id.name if bulletin.employe_id else False,
                    'n_acc_salarie': bulletin.employe_id.n_compte_banque if bulletin.employe_id else False,
                    'montant_salarie': bulletin.salaire_net_payer,
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
                        'matricule': bulletin.employe_id.matricule if bulletin.employe_id else False,
                        'nom_complet': bulletin.employe_id.name if bulletin.employe_id else False,
                        'n_acc_salarie': bulletin.employe_id.n_compte_banque if bulletin.employe_id else False,
                        'montant_salarie': bulletin.salaire_net_payer,
                        'mois': bulletin.mois,
                        'annee': bulletin.annee,
                        'societe_id': bulletin.societe_id.id if bulletin.societe_id else False,
                        'departement_id': bulletin.departement_id.id if bulletin.departement_id else False,
                        'service_id': bulletin.service_id.id if bulletin.service_id else False,
                        'mode_payment': bulletin.employe_id.mode_payment if bulletin.employe_id else False,
                    })
            # If bulletin_id is set to False/None, keep existing stored values
        
        return super().write(vals)

    @api.depends('montant_salarie')
    def _compute_montant_centime(self):
        """Convert montant_salarie from euros to centimes"""
        for record in self:
            if record.montant_salarie:
                record.montant_centime = int(record.montant_salarie * 100)
            else:
                record.montant_centime = 0

    @api.depends('mois', 'annee')
    def _compute_date_complete(self):
        """Format date as MM-AAAA"""
        for record in self:
            if record.mois and record.annee:
                record.date_complete = f"{record.mois.zfill(2)}-{record.annee}"
            else:
                record.date_complete = False

    def generate_simt_from_bulletins(self):
        """Generate SIMT records from bulletins where employee payment mode is 'virement' only"""
        # Filter bulletins to only include those where employee mode_payment is 'vir' (virement)
        bulletins = self.env['softy.bulletin'].search([
            ('employe_id.mode_payment', '=', 'vir')
        ])
        created_count = 0
        skipped_count = 0
        
        for bulletin in bulletins:
            # Check if SIMT already exists for this bulletin
            existing_simt = self.search([('bulletin_id', '=', bulletin.id)])
            if not existing_simt:
                self.create({
                    'bulletin_id': bulletin.id,
                })
                created_count += 1
            else:
                skipped_count += 1
        
        # Count total bulletins for context
        total_bulletins = self.env['softy.bulletin'].search_count([])
        virement_bulletins = len(bulletins)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Génération SIMT (Virement uniquement)',
                'message': f'{created_count} enregistrements SIMT créés avec succès.\n'
                          f'{skipped_count} déjà existants.\n'
                          f'Traités: {virement_bulletins} bulletins avec mode virement sur {total_bulletins} bulletins totaux.',
                'type': 'success',
                'sticky': False,
            }
        }

    def generate_simt_txt_file(self):
        """Generate SIMT .txt file for bank transfer - only for currently filtered records with virement payment mode
        
        Format SIMT:
        - 36 chiffres numero du compte: employe_id.n_compte_banque
        - Montant: En centimes (ex. 00000084500 = 845,00 MAD)
        - Mois et année: MM-YYYY (ex. 11-2022)
        - Matricule: employe_id.matricule (ex. I0884)
        - Nom employé: employe_id.name en majuscules
        - Compte société: societe.banque_id.n_compte
        """
        import base64
        from datetime import datetime
        
        # Filter current recordset to only include virement payment mode
        simt_records = self.filtered(lambda r: r.mode_payment == 'vir')  # Use stored field instead of related
        
        if not simt_records:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': 'Aucun enregistrement SIMT trouvé avec mode de paiement "Virement" dans les filtres actuels.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Check if any records were filtered out
        total_selected = len(self)
        virement_count = len(simt_records)
        filtered_out = total_selected - virement_count
        
        # Group by month-year (Format MM-YYYY)
        grouped_records = {}
        for simt in simt_records:
            key = f"{simt.mois.zfill(2)}-{simt.annee}"  # MM-YYYY
            if key not in grouped_records:
                grouped_records[key] = []
            grouped_records[key].append(simt)
        
        txt_content = ""
        
        for period, records in grouped_records.items():
            # Header line (01) - Using societe.banque_id.n_compte
            total_amount_centimes = sum(record.montant_centime for record in records)
            total_records = len(records)
            
            # Get company bank account (societe.banque_id.n_compte)
            first_record = records[0]
            company_bank_account = ""
            if first_record.societe_id and first_record.societe_id.banque_id:
                company_bank_account = first_record.societe_id.banque_id.n_compte or ""
            
            # Use company bank account or default
            if company_bank_account:
                bank_account_part = company_bank_account[:32]  # Take first 32 chars
            else:
                bank_account_part = "01225780009912601651010756000001"  # Default
            
            header_line = (
                bank_account_part +                     # societe.banque_id.n_compte (32 chars)
                f"{total_amount_centimes:015d}" +       # Montant total en centimes (15)
                f"{total_records:05d}" +                # Nombre d'enregistrements (5)
                f"Paie : {period}".ljust(28)            # Libellé avec mois MM-YYYY (28)
            )
            txt_content += header_line + "\n"
            
            # Detail lines (02) - Using stored employee fields
            for record in records:
                # 36 chiffres numero du compte (stored n_acc_salarie)  
                employee_account = (record.n_acc_salarie or "").replace(" ", "").replace("-", "")
                employee_account = employee_account[:36].ljust(36, '0')  # 36 digits
                
                # Matricule (stored matricule)
                matricule = f"I{record.matricule or '0000'}"
                matricule = matricule[:10].ljust(10)
                
                # Nom employé (stored nom_complet en majuscules)
                employee_name = (record.nom_complet or "").upper().strip()
                employee_name = employee_name[:32].ljust(32)
                
                detail_line = (
                    "02" +                                  # Type enregistrement (2)
                    employee_account +                      # 36 chiffres numero du compte (36)
                    f"{period} {matricule}".ljust(17) +     # MM-YYYY + matricule (17)
                    employee_name                           # Nom employé majuscules (32)
                )
                
                # Ligne de 80 caractères exactement (2+36+17+32 = 87, truncate to 80)
                detail_line = detail_line[:80].ljust(80)
                txt_content += detail_line + "\n"
        
        # Create attachment with info about filtered records
        filename = f"SIMT_Virement_{virement_count}records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(txt_content.encode('utf-8')),
            'res_model': 'softy.simt',
            'res_id': False,
            'mimetype': 'text/plain',
        })
        
        # Show success message with count and filtering info
        message = f'Fichier SIMT généré avec {virement_count} enregistrements (mode Virement uniquement)'
        if filtered_out > 0:
            message += f'\n{filtered_out} enregistrements exclus (autres modes de paiement)'
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }