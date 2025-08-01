import os
import base64
import json
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from PIL import Image, ImageDraw
import io

class AccidentTravail(models.Model):
    _name = 'softy.accident'
    _description = 'Accident de travail'
    _rec_name = 'n_dossier'
    _order = 'heure_accident desc'

    # ... (keep all your existing fields) ...
    
    heure_accident = fields.Datetime(
        string="Date et Heure de l'accident", 
        required=True,
        default=fields.Datetime.now
    )
    
    n_dossier = fields.Char(
        string="N° du Dossier", 
        required=True,
        copy=False
    )
    
    # Accident Details
    nature = fields.Selection([
        ("accidentdetravail", "Accident de Travail"),
        ("maladiepro", "Maladie Professionnelle"),
        ("trajet", "Trajet de Travail")
    ], string="Nature Accident", required=True)
    
    degre_gravite = fields.Selection([
        ("faible", "Faible"),
        ("moyen", "Moyen"),
        ("grave", "Grave"),
        ("tresgrave", "Très Grave"),
        ("mortel", "Mortel")
    ], string="Degré de Gravité", required=True)
    
    cause = fields.Selection([
        ("autrep", "À cause d'une autre Personne"),
        ("actiond", "Par action dangereuse"),
        ("conditiond", "Par une condition dangereuse")
    ], string="Cause", required=True)
    
    # Administrative Information
    nbr_j_arret = fields.Integer(
        string="Nombre de Jours d'arrêt", 
        required=True,
        default=0
    )
    
    date_dec_prefecture = fields.Date(
        string="Date de déclaration préfecture", 
        required=True
    )
    
    ref_prefecture = fields.Char(
        string="Référence préfecture", 
        required=True
    )
    
    # Detailed Description
    circonstances = fields.Text(
        string="Circonstances", 
        required=True
    )
    
    avis = fields.Text(
        string="Avis de l'Entreprise", 
        required=True
    )
    
    tem = fields.Text(
        string="Témoignage"
    )
    
    documents = fields.Text(
        string="Liste des Documents"
    )
    
    # Document Attachments
    doc1 = fields.Binary(string="Document 1")
    doc1_name = fields.Char(string="Nom Document 1")
    doc2 = fields.Binary(string="Document 2")
    doc2_name = fields.Char(string="Nom Document 2")
    doc3 = fields.Binary(string="Document 3")
    doc3_name = fields.Char(string="Nom Document 3")
    
    # Basic Information
    employe_id = fields.Many2one(
        comodel_name="softy.employe", 
        string="Employé", 
        required=True,
        ondelete='cascade'
    )
    
    # Computed Fields
    matricule_employe = fields.Char(
        string="Matricule", 
        related='employe_id.matricule', 
        store=True, 
        readonly=True
    )
    
    nom_employe = fields.Char(
        string="Nom Employé", 
        related='employe_id.name', 
        store=True, 
        readonly=True
    )
    
    cin_employe = fields.Char(
        string="CIN Employé", 
        related='employe_id.cin', 
        store=True, 
        readonly=True
    )
    
    @api.model
    def _get_default_diagram_image(self):
        img_path = os.path.join(
            os.path.dirname(__file__),
            '..', 'static', 'src', 'img', 'accident_diagram.png'
        )
        try:
            data = open(img_path, 'rb').read()
            return base64.b64encode(data).decode('utf-8')
        except IOError:
            return False

    diagram_image = fields.Image(
        string="Schéma de l'accident",
        default=_get_default_diagram_image,
        help="Cliquez pour ajouter des annotations"
    )
    
    diagram_annotations = fields.Text(
        string="Annotations du diagramme",
        help="Stocke les coordonnées des annotations sous format JSON",
        default="[]"
    )
    
    diagram_original_image = fields.Image(
        string="Image originale du diagramme",
        default=_get_default_diagram_image,
        help="Image originale sans annotations"
    )
    
    annotation_mode = fields.Boolean(
        string="Mode Annotation",
        default=False,
        help="Active/désactive le mode annotation"
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('n_dossier_uniq', 'unique(n_dossier)', 'Le numéro de dossier doit être unique.'),
    ]
    
    # Validation
    @api.constrains('heure_accident')
    def _check_heure_accident(self):
        for record in self:
            if record.heure_accident > fields.Datetime.now():
                raise ValidationError("La date de l'accident ne peut pas être dans le futur.")
    
    @api.constrains('nbr_j_arret')
    def _check_nbr_j_arret(self):
        for record in self:
            if record.nbr_j_arret < 0:
                raise ValidationError("Le nombre de jours d'arrêt ne peut pas être négatif.")
    
    @api.constrains('date_dec_prefecture', 'heure_accident')
    def _check_date_declaration(self):
        for record in self:
            if record.date_dec_prefecture < record.heure_accident.date():
                raise ValidationError("La date de déclaration ne peut pas être antérieure à la date de l'accident.")
    
    def toggle_annotation_mode(self):
        """Toggle annotation mode"""
        for record in self:
            record.annotation_mode = not record.annotation_mode
            status = "activé" if record.annotation_mode else "désactivé"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Mode Annotation',
                    'message': f'Mode annotation {status}',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def clear_annotations(self):
        """Clear all annotations and restore original image"""
        for record in self:
            record.diagram_annotations = "[]"
            if record.diagram_original_image:
                record.diagram_image = record.diagram_original_image
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Annotations Effacées',
                    'message': 'Image restaurée sans annotations',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def add_sample_annotation(self):
        """Add sample annotation and update image"""
        for record in self:
            import datetime
            
            # Get existing annotations
            try:
                annotations = json.loads(record.diagram_annotations or "[]")
            except:
                annotations = []
            
            # Add new annotation
            sample_annotation = {
                'x': 0.5,
                'y': 0.3,
                'type': 'injury',
                'description': 'Zone d\'impact',
                'timestamp': datetime.datetime.now().isoformat()
            }
            annotations.append(sample_annotation)
            
            # Save annotations
            record.diagram_annotations = json.dumps(annotations, indent=2)
            
            # UPDATE THE IMAGE WITH DOTS
            record.update_image_with_dots()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Point Ajouté',
                    'message': 'Image mise à jour avec le nouveau point rouge',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def update_image_with_dots(self):
        """Update the diagram image with red dots - FIXED for color mode"""
        for record in self:
            try:
                # Get annotations
                annotations = json.loads(record.diagram_annotations or "[]")
                if not annotations:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Aucune Annotation',
                            'message': 'Pas de points à dessiner. Ajoutez d\'abord des points.',
                            'type': 'warning',
                            'sticky': False,
                        }
                    }
                
                # Get original image
                if not record.diagram_original_image:
                    record.diagram_original_image = record.diagram_image
                
                # Decode base64 image
                image_data = base64.b64decode(record.diagram_original_image)
                img = Image.open(io.BytesIO(image_data))
                
                # CONVERT TO RGB MODE TO SUPPORT UNLIMITED COLORS
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create a copy to draw on
                img_with_dots = img.copy()
                draw = ImageDraw.Draw(img_with_dots)
                
                # Draw red dots for each annotation
                dots_drawn = 0
                for annotation in annotations:
                    if 'x' in annotation and 'y' in annotation:
                        # Convert relative coordinates to absolute
                        x = int(annotation['x'] * img.width)
                        y = int(annotation['y'] * img.height)
                        
                        # Draw red circle with white border
                        radius = 12
                        
                        # Draw white outer circle (border)
                        draw.ellipse([x-radius-2, y-radius-2, x+radius+2, y+radius+2], 
                                fill=(255, 255, 255), outline=(0, 0, 0), width=2)
                        
                        # Draw red inner circle
                        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                                fill=(255, 0, 0), outline=(255, 255, 255), width=2)
                        
                        dots_drawn += 1
                
                # Convert back to base64
                buffer = io.BytesIO()
                img_with_dots.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Update the image field
                record.diagram_image = img_base64
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Image Mise à Jour',
                        'message': f'{dots_drawn} point(s) rouge(s) ajouté(s) à l\'image!',
                        'type': 'success',
                        'sticky': False,
                    }
                }
                
            except Exception as e:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Erreur Image',
                        'message': f'Erreur: {str(e)}',
                        'type': 'danger',
                        'sticky': False,
                    }
                }