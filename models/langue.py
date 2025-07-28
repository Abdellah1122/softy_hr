from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Langue(models.Model):
    _name = 'softy.langue'
    _description = 'Langue'
    _rec_name = 'lang'


    employe_id = fields.Many2one('softy.employe', string='Employé', required=True, ondelete='cascade')

    lang                 = fields.Selection([
                              ('ang','Anglais'), ('ar','Arabe'),
                              ('ber','Berbère'), ('chi','Chinois'),
                              ('esp','Espagnol'), ('fr','Français'),
                              ('it','Italien'), ('jap','Japonais'),
                              ('por','Portugais'), ('thai','Thaïlandais'),
                              ('rus','Russe'),
                            ], required=True)

    nic_conn             = fields.Selection([
                              ('lu','Lu'),
                              ('lecritu','Lu et Écrit'),
                              ('luecritparle','Lu, Écrit et Parlé'),
                              ('parle','Parlé'),
                            ], string="Lecture/Écriture", required=True)

    type_con             = fields.Selection([
                              ('lit','Littéraire'),
                              ('pratique','Pratique Courante'),
                              ('prof','Professionnel'),
                            ], string="Type Connaissance", required=True)

    degre_maitrise       = fields.Selection([
                              ('bonne','Bonne'),
                              ('excellente','Excellente'),
                              ('indeterminee','Indéterminée'),
                              ('insuffisante','Insuffisante'),
                              ('moyenne','Moyenne'),
                            ], string="Degré de Maîtrise", required=True)

    formation            = fields.Boolean(string="Formation", default=False)
    date_debut_formation = fields.Date(string="Date Début Formation")
    date_fin_formation   = fields.Date(string="Date Fin Formation")
    type_formation       = fields.Selection([
                              ('acquisitionperfection','Acquisition – Perfection'),
                              ('adaptationconversion','Adaptation – Conversion'),
                              ('prevention','Prévention'),
                              ('promotionqualifiante','Promotion – Qualifiante'),
                            ], string="Type de Formation")

    @api.constrains('date_debut_formation', 'date_fin_formation')
    def _check_formation_dates(self):
        for rec in self:
            if rec.formation and rec.date_debut_formation and rec.date_fin_formation:
                if rec.date_fin_formation < rec.date_debut_formation:
                    raise ValidationError("La date de fin doit être postérieure ou égale à la date de début.")

    @api.onchange('formation')
    def _onchange_formation(self):
        if not self.formation:
            self.date_debut_formation = False
            self.date_fin_formation   = False
            self.type_formation       = False
