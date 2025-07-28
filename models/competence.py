from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Competence(models.Model):
    _name = 'softy.competence'
    _description = 'Compétence'
    _rec_name = 'type_competence'

    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')
    
    date_validation= fields.Date(string="Date de Validation", required=True)
    degre_maitrise = fields.Selection([
        ("bonne","Bonne"),
        ("excellete","Excellete"),
        ("indeterminee","Indéterminée"),
        ("insuffisante","Insuffisante"),
        ("moyenne","Moyenne"),
    ], string="Degré de Maitrise",required=True)

    type_competence = fields.Selection([
        ("anciennetegrade","Ancienneté dans le Grade"),
        ("ancienneteresponsabilite","Ancienneté dans le Responsabilité"),
        ("communication","Communication"),
        ("cotacteinterneexterne","Contact Interne et Externe"),
        ("management","Managment"),
    ],required=True,string="Type Competence")

    