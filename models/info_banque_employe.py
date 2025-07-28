from odoo import api, fields, models
from odoo.exceptions import ValidationError

class InfoBanqueEmploye(models.Model):
    _name = 'softy.info_banque_employe'
    _description = 'Information Banque Employé'
    _rec_name = 'n_acc'

    

    n_acc=fields.Char(string="N° Compte Banquaire Employée",required=True)
    agence=fields.Char(string="Agence de Banque")
    n_carte=fields.Char(string="N° Carte Banquaire Employé")
    name=fields.Selection([
        ("albarid","Al Barid"),
        ("awb","AWB"),
        ("bmce","BMCE"),
        ("bmci","BMCI"),
        ("bp","Banque Populaire"),
        ("bqassafa","Banque Assafa"),
        ("cam","CAM"),
        ("cfg","Banque CFG"),
        ("cih","Banque CIH"),
        ("cm","Banque CM"),
        ("sgmb","Banque SGMB"),
        ("umnia","Banque Umnia"),
        ("wafacash","Wafa Cash"),
    ], required=True,string="Nom Banque")
    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')
    