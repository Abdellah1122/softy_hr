from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Document(models.Model):
    _name = 'softy.document'
    _description = 'Document'
    _rec_name = 'ref'

    # Employee relationship (many documents for one employee)
    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')

    ref = fields.Char(string='Réf. Document', required=True)
    titre = fields.Char(string='Titre', required=True)
    date_livraison = fields.Date(string='Date Livraison', required=True)
    doc = fields.Binary(string="Document", required=True)
    langue = fields.Selection([
        ('ar', 'Arabe'),
        ('fr', 'Français'),
        ('ang', 'Anglais'),
    ], string='Langue', required=True)
    authorite = fields.Char(string='Autorité')

    _sql_constraints = [
        ('ref_uniq', 'unique(ref)', 'La référence du document doit être unique.'),
    ]