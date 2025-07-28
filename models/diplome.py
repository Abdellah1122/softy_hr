from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Diplome(models.Model):
    _name = 'softy.diplome'
    _description = 'Diplôme'
    _rec_name = 'int_dip'

    #un diplome peux etre assigné a un seul employé sinn l'employé peut avec plusieurs diplome
    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')
    
    int_dip       = fields.Char(string="Intitulé Diplôme", required=True)
    specialite    = fields.Char(string="Spécialité",       required=True)
    etablissement = fields.Char(string="Établissement",     required=True)
    niveau        = fields.Selection([
                      ('3euniv',         '3e Cycle Univ'),
                      ('aucunne_etude',  'Aucune Étude'),
                      ('bac',            'Baccalauréat'),
                      ('deug_equiv',     'DEUG Équivalent'),
                      ('doctorat',       'Doctorat Univ'),
                      ('ecole_ingenieur','École d’Ingénieurs'),
                      ('grandes_ecoles', 'Grandes Écoles'),
                      ('licence',        'Licence'),
                      ('maitrise',       'Maîtrise'),
                      ('primaire',       'Primaires'),
                      ('secondaire',     'Secondaires'),
                    ], string="Niveau", required=True)
    filiere       = fields.Selection([
                      ('informatique', 'Informatique'),
                      ('gestion',      'Gestion'),
                      ('droit',        'Droit'),
                      ('economie',     'Économie'),
                    ], string="Filière", required=True)
    mention       = fields.Selection([
                      ('assez_bien',  'Assez Bien'),
                      ('bien',        'Bien'),
                      ('tres_bien',   'Très Bien'),
                      ('honorable',   'Honorable'),
                      ('passable',    'Passable'),
                      ('sans_mention','Sans Mention'),
                    ], string="Mention", required=True)

    _sql_constraints = [
       
    ]

