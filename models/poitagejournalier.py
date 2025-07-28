import calendar
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PointageJournalier(models.Model):
    _name = 'softy.pointagej'
    _description = 'Pointage Journalier'
    _rec_name = 'lib'
    _order = 'annee desc, mois asc, jour desc, employe_id'

    employe_id = fields.Many2one(
        'softy.employe', string='Employé', required=True, ondelete='cascade'
    )
    
    # Related affiliations from employee (One2many related)
    affiliation_ids = fields.One2many(
        related='employe_id.affiliation_ids', 
        string='Affiliations', 
        readonly=True
    )

    # Date fields
    mois = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1,13)],
        string='Mois', required=True
    )
    annee = fields.Integer(
        string='Année', default=lambda self: fields.Date.today().year, required=True
    )
    jour = fields.Selection(
        selection=lambda self: [(str(i), str(i)) for i in range(1, 32)],
        string='Jour', required=True
    )

    # Computed full date
    date_pointage = fields.Date(
        string='Date', compute='_compute_date_pointage', store=True,
        help="Date du pointage journalier"
    )

    nbr_h = fields.Float(
        string='Heures travaillées', required=True,
        help="Total des heures normales."
    )

    h_25 = fields.Float(string='Heures sup. 25%', default=0.0)
    h_50 = fields.Float(string='Heures sup. 50%', default=0.0)
    h_100 = fields.Float(string='Heures sup. 100%', default=0.0)

    indemnite_ids = fields.Many2many(
        'softy.indemnite', string='Indemnités'
    )

    lib = fields.Char(
        string='Libellé', compute='_compute_lib', store=True
    )

    # Computed total hours
    total_heures = fields.Float(
        string='Total Heures', compute='_compute_total_heures', store=True
    )

    _sql_constraints = [
        (
            'unique_pointage_per_day',
            'UNIQUE(employe_id, mois, jour, annee)',
            "Un pointage existe déjà pour cet employé à cette date."
        ),
    ]

    @api.depends('employe_id.name', 'jour', 'mois', 'annee')
    def _compute_lib(self):
        for rec in self:
            if rec.employe_id and rec.jour and rec.mois and rec.annee:
                rec.lib = f"{rec.employe_id.name} - {rec.jour}/{rec.mois}/{rec.annee}"
            else:
                rec.lib = "Nouveau pointage journalier"

    @api.depends('mois', 'jour', 'annee')
    def _compute_date_pointage(self):
        for rec in self:
            if rec.mois and rec.jour and rec.annee:
                try:
                    from datetime import date
                    rec.date_pointage = date(int(rec.annee), int(rec.mois), int(rec.jour))
                except ValueError:
                    rec.date_pointage = False
            else:
                rec.date_pointage = False

    @api.depends('nbr_h', 'h_25', 'h_50', 'h_100')
    def _compute_total_heures(self):
        for rec in self:
            rec.total_heures = rec.nbr_h + rec.h_25 + rec.h_50 + rec.h_100

    @api.onchange('mois', 'annee')
    def _onchange_mois_annee(self):
        """Update day selection based on month and year"""
        if self.mois and self.annee:
            # Get number of days in the selected month
            month_int = int(self.mois)
            year_int = int(self.annee)
            
            # Get the number of days in this month
            days_in_month = calendar.monthrange(year_int, month_int)[1]
            
            # Reset jour if it's not valid for the new month
            if self.jour and int(self.jour) > days_in_month:
                self.jour = False
                
            # Return a warning if the current day is invalid
            if self.jour and int(self.jour) > days_in_month:
                return {
                    'warning': {
                        'title': 'Jour invalide',
                        'message': f'Le jour {self.jour} n\'existe pas dans {calendar.month_name[month_int]} {year_int}. Veuillez sélectionner un jour valide.'
                    }
                }

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Override to provide dynamic day selection"""
        res = super().fields_get(allfields, attributes)
        
        if 'jour' in res:
            # Default to 31 days (will be limited by validation)
            day_options = [(str(i), str(i)) for i in range(1, 32)]
            res['jour']['selection'] = day_options
            
        return res

    @api.constrains('h_25', 'h_50', 'h_100')
    def _check_extra_hours(self):
        for rec in self:
            for field_name in ('h_25', 'h_50', 'h_100'):
                if getattr(rec, field_name) < 0:
                    raise ValidationError(f"{field_name} ne peut pas être négatif.")

    @api.constrains('nbr_h')
    def _check_positive_values(self):
        for rec in self:
            if rec.nbr_h < 0:
                raise ValidationError("Le nombre d'heures ne peut pas être négatif.")
            if rec.nbr_h > 24:
                raise ValidationError("Le nombre d'heures ne peut pas dépasser 24h par jour.")

    @api.constrains('mois', 'jour', 'annee')
    def _check_valid_date(self):
        for rec in self:
            if rec.mois and rec.jour and rec.annee:
                try:
                    from datetime import date
                    # Try to create the date to validate it
                    date(int(rec.annee), int(rec.mois), int(rec.jour))
                except ValueError:
                    raise ValidationError(f"Date invalide: {rec.jour}/{rec.mois}/{rec.annee}")
                    
            if rec.annee and (rec.annee < 1900 or rec.annee > 2100):
                raise ValidationError("L'année doit être comprise entre 1900 et 2100.")