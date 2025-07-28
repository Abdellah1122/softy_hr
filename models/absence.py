from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class Absence(models.Model):
    _name = 'softy.absence'
    _description = 'Absence'
    _rec_name = 'motif'

    employe_id = fields.Many2one(
        'softy.employe', string="Employé", required=True, ondelete='cascade'
    )
    motif = fields.Char(string="Motif d'Absence", required=True)
    date_absence = fields.Date(string="Date d'Absence", required=True)
    date_reprise = fields.Date(string="Date de Reprise", required=True)
    type_abs = fields.Selection([
        ("absauto","Absence Autorisée"),
        ("absnj","Absence non Justifiée"),
        ("maladie","Maladie"),
    ], string="Type d'Absence", required=True)

    jours = fields.Integer(
        string="Durée (jours)", compute="_compute_jours", store=True
    )

    @api.depends('date_absence', 'date_reprise')
    def _compute_jours(self):
        for rec in self:
            if rec.date_absence and rec.date_reprise:
                rec.jours = (rec.date_reprise - rec.date_absence).days + 1
            else:
                rec.jours = 0

    @api.constrains('date_reprise', 'date_absence')
    def _check_dates(self):
        for rec in self:
            if rec.date_reprise < rec.date_absence:
                raise ValidationError(
                    "La date de reprise doit être postérieure ou égale à la date d'absence."
                )
