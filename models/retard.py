from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, time

class Retard(models.Model):
    _name = 'softy.retard'
    _description = 'Retard'
    _rec_name = 'motif'

    employe_id = fields.Many2one(
        'softy.employe', string="Employé", required=True, ondelete='cascade'
    )
    motif = fields.Char(string="Motif de Retard", required=True)
    date_retard = fields.Date(string="Date du Retard", required=True)
    heure_arrivee = fields.Datetime(
        string="Heure d'Arrivée", required=True
    )
    heures_retarde = fields.Float(
        string="Heures de Retard", compute='_compute_heures_retarde', store=True
    )

    @api.depends('heure_arrivee', 'date_retard')
    def _compute_heures_retarde(self):
        start_of_day = time(9, 0, 0)   # default start time 09:00
        for rec in self:
            rec.heures_retarde = 0.0
            if rec.date_retard and rec.heure_arrivee:
                scheduled = datetime.combine(rec.date_retard, start_of_day)
                diff = rec.heure_arrivee - scheduled
                rec.heures_retarde = max(diff.total_seconds() / 3600.0, 0.0)

    @api.constrains('heure_arrivee', 'date_retard')
    def _check_date_consistency(self):
        for rec in self:
            if rec.heure_arrivee and rec.date_retard:
                if rec.heure_arrivee.date() != rec.date_retard:
                    raise ValidationError(
                        "La date d'arrivée doit être égale à la date du retard."
                    )
