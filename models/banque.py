from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Banque(models.Model):
    _name = 'softy.banque'
    _description = 'Banque'
    
    code = fields.Char(string='Code Banque', required=True)
    logo = fields.Binary(string="Logo")
    name = fields.Selection([
        ("albarid", "Al Barid"),
        ("awb", "AWB"),
        ("bmce", "BMCE"),
        ("bmci", "BMCI"),
        ("bp", "Banque Populaire"),
        ("bqassafa", "Banque Assafa"),
        ("cam", "CAM"),
        ("cfg", "Banque CFG"),
        ("cih", "Banque CIH"),
        ("cm", "Banque CM"),
        ("sgmb", "Banque SGMB"),
        ("umnia", "Banque Umnia"),
        ("wafacash", "Wafa Cash"),
    ], required=True, string="Nom Banque")
    libelle = fields.Char(string='Libellé Complet du Banque', required=True)
    agence = fields.Char(string='Agence', required=True)
    n_compte = fields.Char(string='N° Compte', required=True)
    lib_societe = fields.Char(string='Libelle Societé', required=True)
    ref = fields.Char(string='Reference du Banque', required=True)
    address = fields.Char(string='Address de la banque')
    email = fields.Char(string='Email Banque')
    tel = fields.Char(string='Tel Banque')
    responsable = fields.Char(string='Responsable')
    active = fields.Boolean(string='Active', default=True)

    # One2many relationship to get the societe(s) that reference this banque
    societe_ids = fields.One2many(
        comodel_name='softy.societe',
        inverse_name='banque_id',
        string='Sociétés',
        readonly=True,
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Le code de la Banque doit être unique.'),
    ]

    @api.constrains('societe_ids')
    def _check_unique_societe(self):
        """Ensure each banque is associated with only one societe"""
        for rec in self:
            if len(rec.societe_ids) > 1:
                raise ValidationError(
                    "Une banque ne peut être associée qu'à une seule société. "
                    f"Cette banque est actuellement liée à {len(rec.societe_ids)} sociétés."
                )

    def write(self, vals):
        """Override write to prevent breaking one-to-one constraint"""
        result = super().write(vals)
        # Trigger constraint check after write
        self._check_unique_societe()
        return result