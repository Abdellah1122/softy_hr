import calendar
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class PointageMensuel(models.Model):
    _name = 'softy.pointagem'
    _description = 'Pointage Mensuel'
    _rec_name = 'lib'
    _order = 'annee desc, mois asc, employe_id'

    employe_id = fields.Many2one(
        'softy.employe', string='Employé', required=True, ondelete='cascade'
    )
    
    # Related affiliations from employee (One2many related)
    affiliation_ids = fields.One2many(
        related='employe_id.affiliation_ids', 
        string='Affiliations', 
        readonly=True
    )

    nbr_j = fields.Integer(
        string='Jours travaillés', required=True,
        help="Nombre total de jours travaillés dans le mois."
    )
    nbr_j_conge = fields.Integer(
        string='Jours congé', 
        help="Nombre total de jours de congé dans le mois."
    )
    nbr_h = fields.Float(
        string='Heures travaillées', required=True,
        help="Total des heures normales."
    )

    h_25 = fields.Float(string='Heures sup. 25%', default=0.0)
    h_50 = fields.Float(string='Heures sup. 50%', default=0.0)
    h_100 = fields.Float(string='Heures sup. 100%', default=0.0)

    # New period field
    periode = fields.Selection([
        ('current', 'Mois Actuel'),
        ('previous', 'Mois Précédent')
    ], string='Période', required=True, default='current')

    mois = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1,13)],
        string='Mois', required=True, readonly=True
    )
    annee = fields.Integer(
        string='Année', default=lambda self: fields.Date.today().year, 
        required=True, readonly=True
    )

    ind_point_ids = fields.Many2many(
        'softy.ind_point',string='Lignes Indemnités')

    lib = fields.Char(
        string='Libellé', compute='_compute_lib', store=True
    )

    _sql_constraints = [
        (
            'unique_pointage_per_month',
            'UNIQUE(employe_id, mois, annee)',
            "Un pointage existe déjà pour cet employé, ce mois et cette année."
        ),
    ]

    @api.depends('employe_id.name', 'mois', 'annee')
    def _compute_lib(self):
        for rec in self:
            if rec.employe_id and rec.mois and rec.annee:
                rec.lib = f"{rec.employe_id.name} - {rec.mois}/{rec.annee}"
            else:
                rec.lib = "Nouveau pointage"

    def _check_current_period_exists(self):
        """Check if any current period pointages exist"""
        today = date.today()
        current_pointages = self.search([
            ('periode', '=', 'current'),
            ('mois', '=', str(today.month)),
            ('annee', '=', today.year)
        ])
        return len(current_pointages) > 0

    def _is_previous_period_locked(self):
        """Check if previous period is locked (current period has started)"""
        return self._check_current_period_exists()

    @api.onchange('periode')
    def _onchange_periode(self):
        """Update month and year based on selected period"""
        if self.periode:
            today = date.today()
            
            if self.periode == 'current':
                # Current month
                self.mois = str(today.month)
                self.annee = today.year
            elif self.periode == 'previous':
                # Check if previous period is locked
                if self._is_previous_period_locked():
                    # Reset to current period
                    self.periode = 'current'
                    self.mois = str(today.month)
                    self.annee = today.year
                    return {
                        'warning': {
                            'title': 'Période Verrouillée',
                            'message': 'La période précédente est verrouillée car vous avez déjà commencé la période actuelle.'
                        }
                    }
                else:
                    # Previous month
                    previous_month = today - relativedelta(months=1)
                    self.mois = str(previous_month.month)
                    self.annee = previous_month.year

    @api.model
    def default_get(self, fields_list):
        """Set default values when creating new record"""
        defaults = super().default_get(fields_list)
        
        # Check if previous period is locked
        if self._check_current_period_exists():
            # Force current period
            if 'periode' in fields_list:
                defaults['periode'] = 'current'
        else:
            # Allow default selection
            if 'periode' in fields_list:
                defaults['periode'] = 'current'
            
        # Set default month/year based on current period
        today = date.today()
        if 'mois' in fields_list:
            defaults['mois'] = str(today.month)
        if 'annee' in fields_list:
            defaults['annee'] = today.year
            
        return defaults

    @api.model
    def create(self, vals):
        """Override create to ensure month/year are set based on period and check locking"""
        if 'periode' in vals and vals['periode']:
            today = date.today()
            
            if vals['periode'] == 'current':
                vals['mois'] = str(today.month)
                vals['annee'] = today.year
            elif vals['periode'] == 'previous':
                # Check if previous period is locked
                if self._check_current_period_exists():
                    raise ValidationError(
                        "La période précédente est verrouillée car vous avez déjà commencé la période actuelle."
                    )
                previous_month = today - relativedelta(months=1)
                vals['mois'] = str(previous_month.month)
                vals['annee'] = previous_month.year
                
        return super().create(vals)

    def write(self, vals):
        """Override write to update month/year when period changes and check locking"""
        if 'periode' in vals:
            today = date.today()
            
            if vals['periode'] == 'current':
                vals['mois'] = str(today.month)
                vals['annee'] = today.year
            elif vals['periode'] == 'previous':
                # Check if previous period is locked
                if self._check_current_period_exists():
                    raise ValidationError(
                        "La période précédente est verrouillée car vous avez déjà commencé la période actuelle."
                    )
                previous_month = today - relativedelta(months=1)
                vals['mois'] = str(previous_month.month)
                vals['annee'] = previous_month.year
                
        return super().write(vals)

    @api.constrains('periode')
    def _check_period_lock(self):
        """Ensure previous period cannot be modified if current period has started"""
        for rec in self:
            if rec.periode == 'previous':
                if self._check_current_period_exists():
                    raise ValidationError(
                        "La période précédente est verrouillée car vous avez déjà commencé la période actuelle."
                    )

    @api.constrains('h_25', 'h_50', 'h_100')
    def _check_extra_hours(self):
        for rec in self:
            for field_name in ('h_25', 'h_50', 'h_100'):
                if getattr(rec, field_name) < 0:
                    raise ValidationError(f"{field_name} ne peut pas être négatif.")

    @api.constrains('nbr_j', 'nbr_h')
    def _check_positive_values(self):
        for rec in self:
            if rec.nbr_j < 0:
                raise ValidationError("Le nombre de jours ne peut pas être négatif.")
            if rec.nbr_h < 0:
                raise ValidationError("Le nombre d'heures ne peut pas être négatif.")

    @api.constrains('mois', 'annee')
    def _check_month_year(self):
        for rec in self:
            if rec.annee < 1900 or rec.annee > 2100:
                raise ValidationError("L'année doit être comprise entre 1900 et 2100.")