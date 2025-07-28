from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Pret(models.Model):
    _name = 'softy.pret'
    _description = 'Prêt'
    _rec_name = 'num_dossier'

    employe_id = fields.Many2one(
        'softy.employe', string='Employé', required=True, ondelete='cascade'
    )
    num_dossier = fields.Char(string="N° Dossier", required=True)
    date_attribution = fields.Date(string="Date d'Attribution", required=True)
    montant_pret = fields.Float(string="Montant du Prêt", required=True)
    prelevement_mensuel = fields.Float(string="Prélèvement Mensuel", required=True)
    debut_prelevement = fields.Date(string="Début Prélèvements", required=True)
    fin_prelevement = fields.Date(string="Fin Prélèvements", required=True)
    montant_commu = fields.Float(string="Montant Communal", required=True)
    des_prelevement = fields.Selection([
        ("diacsalaf","Diac Salaf"),
        ("pretaid","Prêt AID"),
        ("sogecredit","Soge Crédit"),
        ("dotationcredit","Dotation Crédit"),
        ("dotationvestimentaire","Dotation Vestimentaire"),
        ("creditmcr","Crédit MCR Groupe"),
        ("allocfam","Trop perçu Allocation Famille"),
        ("pretdivers","Prêt Divers"),
        ("pretespaceinterim","Prêt Espace Intérim"),
        ("pretmoto","Prêt Moto"),
        ("pretrhs","Prêt RHS"),
        ("pretseparator","Prêt Separator"),
        ("retourpret","Retour Prêt"),
    ], string="Type de Prélèvement", required=True)

    nb_prelevements = fields.Integer(
        string="Nbre Prélèvements", compute="_compute_schedule", store=True
    )
    total_rembourse = fields.Float(
        string="Total Remboursé", compute="_compute_schedule", store=True
    )

    _sql_constraints = [
        ('num_dossier_unique', 'unique(num_dossier)', "N° Dossier must be unique."),
    ]

    @api.depends('debut_prelevement', 'fin_prelevement', 'prelevement_mensuel')
    def _compute_schedule(self):
        for rec in self:
            if rec.debut_prelevement and rec.fin_prelevement and rec.prelevement_mensuel:
                rd = rec.debut_prelevement
                rf = rec.fin_prelevement
                # count months difference inclusive
                diff = relativedelta(rf, rd)
                months = diff.years * 12 + diff.months + 1
                rec.nb_prelevements = max(months, 0)
                rec.total_rembourse = rec.nb_prelevements * rec.prelevement_mensuel
            else:
                rec.nb_prelevements = 0
                rec.total_rembourse = 0.0

    @api.constrains('fin_prelevement', 'debut_prelevement')
    def _check_dates(self):
        for rec in self:
            if rec.fin_prelevement < rec.debut_prelevement:
                raise ValidationError(
                    "La date de fin de prélèvements doit être postérieure ou égale au début."
                )
