from odoo import models, fields, api
class Avocat(models.Model):
    _name = 'softy.avocat'
    _description = 'Avocats'
    _rec_name = 'full_name'

    first_name = fields.Char(string="Prénom de l'avocat", required=True)
    last_name = fields.Char(string="Nom de l'avocat", required=True)
    tel = fields.Char(string="Telephone de l'avocat")
    email = fields.Char(string="Email de l'avoact")
    ville_id=fields.Many2one(comodel_name="softy.ville")
    full_name = fields.Char(string="Nom complet", compute="_compute_full_name", store=True)

    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for record in self:
            record.full_name = f"{record.first_name} {record.last_name}".strip()
    
    _sql_constraints = [
    ('unique_email', 'unique(email)', "Un avocat avec cet email existe déjà."),
    ]