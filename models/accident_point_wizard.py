from odoo import models, fields, api
import json

class AccidentPointWizard(models.TransientModel):
    _name = 'softy.accident.point.wizard'
    _description = 'Wizard for placing points on accident diagram'

    # Link to the accident record
    accident_id = fields.Many2one(
        'softy.accident',
        string='Accident Record',
        required=True
    )
    
    # Display the image (read-only)
    diagram_image = fields.Image(
        string="Diagram",
        related='accident_id.diagram_original_image',
        readonly=True
    )
    
    # Add view selection first
    body_view = fields.Selection([
        ('front', 'Vue de Face'),
        ('side_left', 'Profil Gauche'),
        ('side_right', 'Profil Droit'), 
        ('back', 'Vue de Dos'),
    ], string='Vue du Corps', required=True)
    
    # COMPREHENSIVE body parts with ALL possible positions
    body_part = fields.Selection([
        # HEAD & NECK
        ('forehead', 'Front'),
        ('temples', 'Tempes'),
        ('eyes', 'Yeux'),
        ('nose', 'Nez'),
        ('mouth', 'Bouche'),
        ('chin', 'Menton'),
        ('jaw', 'Mâchoire'),
        ('ears', 'Oreilles'),
        ('head_top', 'Sommet de la Tête'),
        ('head_back', 'Arrière de la Tête'),
        ('neck_front', 'Cou (Avant)'),
        ('neck_side', 'Cou (Côté)'),
        ('neck_back', 'Nuque'),
        ('throat', 'Gorge'),
        
        # TORSO - FRONT
        ('chest_upper', 'Poitrine Haute'),
        ('chest_middle', 'Poitrine Milieu'),
        ('chest_lower', 'Poitrine Basse'),
        ('breast_left', 'Sein Gauche'),
        ('breast_right', 'Sein Droit'),
        ('ribs_left', 'Côtes Gauches'),
        ('ribs_right', 'Côtes Droites'),
        ('abdomen_upper', 'Abdomen Haut'),
        ('abdomen_middle', 'Abdomen Milieu'),
        ('abdomen_lower', 'Abdomen Bas'),
        ('stomach', 'Estomac'),
        ('navel', 'Nombril'),
        ('pelvis', 'Bassin'),
        ('groin', 'Aine'),
        
        # TORSO - BACK
        ('upper_back', 'Haut du Dos'),
        ('middle_back', 'Milieu du Dos'),
        ('lower_back', 'Bas du Dos'),
        ('spine_upper', 'Colonne Haute'),
        ('spine_middle', 'Colonne Milieu'),
        ('spine_lower', 'Colonne Basse'),
        ('shoulder_blades_left', 'Omoplate Gauche'),
        ('shoulder_blades_right', 'Omoplate Droite'),
        ('kidney_area', 'Zone Rénale'),
        ('tailbone', 'Coccyx'),
        
        # SHOULDERS & ARMS
        ('shoulder_left', 'Épaule Gauche'),
        ('shoulder_right', 'Épaule Droite'),
        ('shoulder_top_left', 'Dessus Épaule Gauche'),
        ('shoulder_top_right', 'Dessus Épaule Droite'),
        ('armpit_left', 'Aisselle Gauche'),
        ('armpit_right', 'Aisselle Droite'),
        
        # UPPER ARM
        ('upper_arm_left', 'Bras Haut Gauche'),
        ('upper_arm_right', 'Bras Haut Droit'),
        ('bicep_left', 'Biceps Gauche'),
        ('bicep_right', 'Biceps Droit'),
        ('tricep_left', 'Triceps Gauche'),
        ('tricep_right', 'Triceps Droit'),
        
        # ELBOW & FOREARM
        ('elbow_left', 'Coude Gauche'),
        ('elbow_right', 'Coude Droit'),
        ('elbow_inner_left', 'Coude Interne Gauche'),
        ('elbow_inner_right', 'Coude Interne Droit'),
        ('forearm_left', 'Avant-bras Gauche'),
        ('forearm_right', 'Avant-bras Droit'),
        ('forearm_inner_left', 'Avant-bras Interne Gauche'),
        ('forearm_inner_right', 'Avant-bras Interne Droit'),
        
        # WRIST & HANDS
        ('wrist_left', 'Poignet Gauche'),
        ('wrist_right', 'Poignet Droit'),
        ('hand_left', 'Main Gauche'),
        ('hand_right', 'Main Droite'),
        ('palm_left', 'Paume Gauche'),
        ('palm_right', 'Paume Droite'),
        ('thumb_left', 'Pouce Gauche'),
        ('thumb_right', 'Pouce Droit'),
        ('fingers_left', 'Doigts Gauches'),
        ('fingers_right', 'Doigts Droits'),
        ('knuckles_left', 'Jointures Gauches'),
        ('knuckles_right', 'Jointures Droites'),
        
        # HIPS & PELVIS
        ('hip_left', 'Hanche Gauche'),
        ('hip_right', 'Hanche Droite'),
        ('buttock_left', 'Fesse Gauche'),
        ('buttock_right', 'Fesse Droite'),
        
        # UPPER LEG
        ('thigh_left', 'Cuisse Gauche'),
        ('thigh_right', 'Cuisse Droite'),
        ('thigh_inner_left', 'Cuisse Interne Gauche'),
        ('thigh_inner_right', 'Cuisse Interne Droite'),
        ('thigh_outer_left', 'Cuisse Externe Gauche'),
        ('thigh_outer_right', 'Cuisse Externe Droite'),
        ('thigh_back_left', 'Arrière Cuisse Gauche'),
        ('thigh_back_right', 'Arrière Cuisse Droite'),
        
        # KNEE
        ('knee_left', 'Genou Gauche'),
        ('knee_right', 'Genou Droit'),
        ('knee_cap_left', 'Rotule Gauche'),
        ('knee_cap_right', 'Rotule Droite'),
        ('knee_back_left', 'Arrière Genou Gauche'),
        ('knee_back_right', 'Arrière Genou Droit'),
        
        # LOWER LEG
        ('shin_left', 'Tibia Gauche'),
        ('shin_right', 'Tibia Droit'),
        ('calf_left', 'Mollet Gauche'),
        ('calf_right', 'Mollet Droit'),
        ('calf_inner_left', 'Mollet Interne Gauche'),
        ('calf_inner_right', 'Mollet Interne Droit'),
        
        # ANKLE & FEET
        ('ankle_left', 'Cheville Gauche'),
        ('ankle_right', 'Cheville Droite'),
        ('ankle_inner_left', 'Cheville Interne Gauche'),
        ('ankle_inner_right', 'Cheville Interne Droite'),
        ('foot_left', 'Pied Gauche'),
        ('foot_right', 'Pied Droit'),
        ('foot_top_left', 'Dessus Pied Gauche'),
        ('foot_top_right', 'Dessus Pied Droit'),
        ('foot_sole_left', 'Plante Pied Gauche'),
        ('foot_sole_right', 'Plante Pied Droite'),
        ('heel_left', 'Talon Gauche'),
        ('heel_right', 'Talon Droit'),
        ('toes_left', 'Orteils Gauches'),
        ('toes_right', 'Orteils Droits'),
        ('big_toe_left', 'Gros Orteil Gauche'),
        ('big_toe_right', 'Gros Orteil Droit'),
        
    ], string='Partie du Corps')
    
    # Type of injury
    injury_type = fields.Selection([
        ('injury', 'Blessure'),
        ('impact', 'Point d\'Impact'),
        ('pain', 'Douleur'),
        ('fracture', 'Fracture'),
        ('cut', 'Coupure'),
        ('burn', 'Brûlure'),
        ('bruise', 'Bleu/Contusion'),
        ('scratch', 'Égratignure'),
        ('puncture', 'Perforation'),
        ('strain', 'Élongation'),
        ('sprain', 'Entorse'),
        ('swelling', 'Gonflement'),
    ], string='Type de Blessure', default='injury')
    
    # Description
    description = fields.Char(string='Description', default='Zone touchée')
    
    # Method to get available body parts based on selected view
    @api.model
    def _get_available_body_parts_by_view(self):
        """Return which body parts are visible for each view"""
        return {
            'front': [
                # HEAD & NECK (front visible)
                'forehead', 'temples', 'eyes', 'nose', 'mouth', 'chin', 'jaw', 'ears', 'head_top',
                'neck_front', 'throat',
                
                # TORSO - FRONT
                'chest_upper', 'chest_middle', 'chest_lower', 'breast_left', 'breast_right',
                'ribs_left', 'ribs_right', 'abdomen_upper', 'abdomen_middle', 'abdomen_lower',
                'stomach', 'navel', 'pelvis', 'groin',
                
                # SHOULDERS & ARMS (front view)
                'shoulder_left', 'shoulder_right', 'shoulder_top_left', 'shoulder_top_right',
                'armpit_left', 'armpit_right',
                'upper_arm_left', 'upper_arm_right', 'bicep_left', 'bicep_right',
                'elbow_left', 'elbow_right', 'elbow_inner_left', 'elbow_inner_right',
                'forearm_left', 'forearm_right', 'forearm_inner_left', 'forearm_inner_right',
                'wrist_left', 'wrist_right', 'hand_left', 'hand_right', 'palm_left', 'palm_right',
                'thumb_left', 'thumb_right', 'fingers_left', 'fingers_right', 'knuckles_left', 'knuckles_right',
                
                # HIPS & LEGS (front view)
                'hip_left', 'hip_right',
                'thigh_left', 'thigh_right', 'thigh_inner_left', 'thigh_inner_right',
                'knee_left', 'knee_right', 'knee_cap_left', 'knee_cap_right',
                'shin_left', 'shin_right', 'calf_inner_left', 'calf_inner_right',
                'ankle_left', 'ankle_right', 'ankle_inner_left', 'ankle_inner_right',
                'foot_left', 'foot_right', 'foot_top_left', 'foot_top_right',
                'toes_left', 'toes_right', 'big_toe_left', 'big_toe_right',
            ],
            
            'side_left': [
                # HEAD & NECK (side visible)
                'forehead', 'temples', 'ears', 'head_top', 'head_back', 'neck_side', 'jaw', 'chin',
                
                # TORSO (side view)
                'chest_middle', 'ribs_left', 'abdomen_middle', 'pelvis',
                'upper_back', 'middle_back', 'lower_back', 'spine_upper', 'spine_middle', 'spine_lower',
                
                # LEFT SIDE ONLY
                'shoulder_left', 'shoulder_top_left', 'armpit_left',
                'upper_arm_left', 'bicep_left', 'tricep_left',
                'elbow_left', 'forearm_left', 'wrist_left', 'hand_left',
                'hip_left', 'buttock_left',
                'thigh_left', 'thigh_outer_left', 'thigh_back_left',
                'knee_left', 'knee_back_left',
                'shin_left', 'calf_left', 'ankle_left', 'foot_left', 'heel_left',
            ],
            
            'side_right': [
                # HEAD & NECK (side visible)
                'forehead', 'temples', 'ears', 'head_top', 'head_back', 'neck_side', 'jaw', 'chin',
                
                # TORSO (side view)
                'chest_middle', 'ribs_right', 'abdomen_middle', 'pelvis',
                'upper_back', 'middle_back', 'lower_back', 'spine_upper', 'spine_middle', 'spine_lower',
                
                # RIGHT SIDE ONLY
                'shoulder_right', 'shoulder_top_right', 'armpit_right',
                'upper_arm_right', 'bicep_right', 'tricep_right',
                'elbow_right', 'forearm_right', 'wrist_right', 'hand_right',
                'hip_right', 'buttock_right',
                'thigh_right', 'thigh_outer_right', 'thigh_back_right',
                'knee_right', 'knee_back_right',
                'shin_right', 'calf_right', 'ankle_right', 'foot_right', 'heel_right',
            ],
            
            'back': [
                # HEAD & NECK (back visible)
                'head_back', 'neck_back', 'ears', 'head_top',
                
                # TORSO - BACK
                'upper_back', 'middle_back', 'lower_back',
                'spine_upper', 'spine_middle', 'spine_lower',
                'shoulder_blades_left', 'shoulder_blades_right',
                'kidney_area', 'tailbone',
                
                # SHOULDERS & ARMS (back view)
                'shoulder_left', 'shoulder_right', 'shoulder_top_left', 'shoulder_top_right',
                'upper_arm_left', 'upper_arm_right', 'tricep_left', 'tricep_right',
                'elbow_left', 'elbow_right', 'forearm_left', 'forearm_right',
                'wrist_left', 'wrist_right', 'hand_left', 'hand_right',
                
                # HIPS & LEGS (back view)
                'hip_left', 'hip_right', 'buttock_left', 'buttock_right',
                'thigh_back_left', 'thigh_back_right', 'thigh_outer_left', 'thigh_outer_right',
                'knee_back_left', 'knee_back_right',
                'calf_left', 'calf_right', 'ankle_left', 'ankle_right',
                'heel_left', 'heel_right', 'foot_sole_left', 'foot_sole_right',
            ]
        }
    
    # COMPREHENSIVE coordinates for 4-panel body diagram
    @api.model
    def _get_body_part_coordinates(self):
        """
        Coordinates for 4-panel body diagram layout:
        Panel 1 (0.0-0.25): Front view
        Panel 2 (0.25-0.5): Side left view  
        Panel 3 (0.5-0.75): Side right view
        Panel 4 (0.75-1.0): Back view
        """
        return {
            # FRONT VIEW (Panel 1: x = 0.0 to 0.25)
            'front': {
                # HEAD & NECK
                'forehead': {'x': 0.125, 'y': 0.12},
                'temples': {'x': 0.115, 'y': 0.14},
                'eyes': {'x': 0.125, 'y': 0.15},
                'nose': {'x': 0.125, 'y': 0.17},
                'mouth': {'x': 0.125, 'y': 0.19},
                'chin': {'x': 0.125, 'y': 0.21},
                'jaw': {'x': 0.118, 'y': 0.18},
                'ears': {'x': 0.11, 'y': 0.16},
                'head_top': {'x': 0.125, 'y': 0.08},
                'neck_front': {'x': 0.125, 'y': 0.24},
                'throat': {'x': 0.125, 'y': 0.23},
                
                # TORSO - FRONT
                'chest_upper': {'x': 0.125, 'y': 0.32},
                'chest_middle': {'x': 0.125, 'y': 0.38},
                'chest_lower': {'x': 0.125, 'y': 0.44},
                'breast_left': {'x': 0.11, 'y': 0.36},
                'breast_right': {'x': 0.14, 'y': 0.36},
                'ribs_left': {'x': 0.1, 'y': 0.42},
                'ribs_right': {'x': 0.15, 'y': 0.42},
                'abdomen_upper': {'x': 0.125, 'y': 0.5},
                'abdomen_middle': {'x': 0.125, 'y': 0.55},
                'abdomen_lower': {'x': 0.125, 'y': 0.6},
                'stomach': {'x': 0.125, 'y': 0.48},
                'navel': {'x': 0.125, 'y': 0.53},
                'pelvis': {'x': 0.125, 'y': 0.65},
                'groin': {'x': 0.125, 'y': 0.68},
                
                # SHOULDERS & ARMS
                'shoulder_left': {'x': 0.08, 'y': 0.3},
                'shoulder_right': {'x': 0.17, 'y': 0.3},
                'shoulder_top_left': {'x': 0.08, 'y': 0.28},
                'shoulder_top_right': {'x': 0.17, 'y': 0.28},
                'armpit_left': {'x': 0.095, 'y': 0.35},
                'armpit_right': {'x': 0.155, 'y': 0.35},
                
                # UPPER ARM
                'upper_arm_left': {'x': 0.07, 'y': 0.42},
                'upper_arm_right': {'x': 0.18, 'y': 0.42},
                'bicep_left': {'x': 0.075, 'y': 0.4},
                'bicep_right': {'x': 0.175, 'y': 0.4},
                
                # ELBOW & FOREARM
                'elbow_left': {'x': 0.065, 'y': 0.52},
                'elbow_right': {'x': 0.185, 'y': 0.52},
                'elbow_inner_left': {'x': 0.07, 'y': 0.52},
                'elbow_inner_right': {'x': 0.18, 'y': 0.52},
                'forearm_left': {'x': 0.055, 'y': 0.6},
                'forearm_right': {'x': 0.195, 'y': 0.6},
                'forearm_inner_left': {'x': 0.06, 'y': 0.6},
                'forearm_inner_right': {'x': 0.19, 'y': 0.6},
                
                # WRIST & HANDS
                'wrist_left': {'x': 0.045, 'y': 0.68},
                'wrist_right': {'x': 0.205, 'y': 0.68},
                'hand_left': {'x': 0.035, 'y': 0.74},
                'hand_right': {'x': 0.215, 'y': 0.74},
                'palm_left': {'x': 0.04, 'y': 0.72},
                'palm_right': {'x': 0.21, 'y': 0.72},
                'thumb_left': {'x': 0.03, 'y': 0.7},
                'thumb_right': {'x': 0.22, 'y': 0.7},
                'fingers_left': {'x': 0.035, 'y': 0.76},
                'fingers_right': {'x': 0.215, 'y': 0.76},
                'knuckles_left': {'x': 0.035, 'y': 0.73},
                'knuckles_right': {'x': 0.215, 'y': 0.73},
                
                # HIPS & LEGS
                'hip_left': {'x': 0.105, 'y': 0.67},
                'hip_right': {'x': 0.145, 'y': 0.67},
                'thigh_left': {'x': 0.11, 'y': 0.75},
                'thigh_right': {'x': 0.14, 'y': 0.75},
                'thigh_inner_left': {'x': 0.118, 'y': 0.76},
                'thigh_inner_right': {'x': 0.132, 'y': 0.76},
                
                # KNEE
                'knee_left': {'x': 0.11, 'y': 0.84},
                'knee_right': {'x': 0.14, 'y': 0.84},
                'knee_cap_left': {'x': 0.11, 'y': 0.83},
                'knee_cap_right': {'x': 0.14, 'y': 0.83},
                
                # LOWER LEG
                'shin_left': {'x': 0.11, 'y': 0.9},
                'shin_right': {'x': 0.14, 'y': 0.9},
                'calf_inner_left': {'x': 0.115, 'y': 0.88},
                'calf_inner_right': {'x': 0.135, 'y': 0.88},
                
                # ANKLE & FEET
                'ankle_left': {'x': 0.11, 'y': 0.96},
                'ankle_right': {'x': 0.14, 'y': 0.96},
                'ankle_inner_left': {'x': 0.115, 'y': 0.96},
                'ankle_inner_right': {'x': 0.135, 'y': 0.96},
                'foot_left': {'x': 0.105, 'y': 0.98},
                'foot_right': {'x': 0.145, 'y': 0.98},
                'foot_top_left': {'x': 0.105, 'y': 0.97},
                'foot_top_right': {'x': 0.145, 'y': 0.97},
                'toes_left': {'x': 0.1, 'y': 0.99},
                'toes_right': {'x': 0.15, 'y': 0.99},
                'big_toe_left': {'x': 0.105, 'y': 0.99},
                'big_toe_right': {'x': 0.145, 'y': 0.99},
            },
            
            # Add similar comprehensive mappings for other views...
            # SIDE LEFT VIEW (Panel 2: x = 0.25 to 0.5)
            'side_left': {
                # HEAD & NECK
                'forehead': {'x': 0.36, 'y': 0.12},
                'temples': {'x': 0.355, 'y': 0.14},
                'ears': {'x': 0.385, 'y': 0.16},
                'head_top': {'x': 0.375, 'y': 0.08},
                'head_back': {'x': 0.39, 'y': 0.12},
                'neck_side': {'x': 0.375, 'y': 0.24},
                'jaw': {'x': 0.36, 'y': 0.18},
                'chin': {'x': 0.355, 'y': 0.21},
                
                # TORSO
                'chest_middle': {'x': 0.365, 'y': 0.38},
                'ribs_left': {'x': 0.37, 'y': 0.42},
                'abdomen_middle': {'x': 0.37, 'y': 0.55},
                'pelvis': {'x': 0.375, 'y': 0.65},
                'upper_back': {'x': 0.39, 'y': 0.32},
                'middle_back': {'x': 0.395, 'y': 0.45},
                'lower_back': {'x': 0.395, 'y': 0.58},
                'spine_upper': {'x': 0.392, 'y': 0.35},
                'spine_middle': {'x': 0.392, 'y': 0.48},
                'spine_lower': {'x': 0.392, 'y': 0.6},
                
                # LEFT SIDE ONLY
                'shoulder_left': {'x': 0.35, 'y': 0.3},
                'shoulder_top_left': {'x': 0.35, 'y': 0.28},
                'armpit_left': {'x': 0.355, 'y': 0.35},
                'upper_arm_left': {'x': 0.34, 'y': 0.42},
                'bicep_left': {'x': 0.335, 'y': 0.4},
                'tricep_left': {'x': 0.345, 'y': 0.4},
                'elbow_left': {'x': 0.33, 'y': 0.52},
                'forearm_left': {'x': 0.32, 'y': 0.6},
                'wrist_left': {'x': 0.31, 'y': 0.68},
                'hand_left': {'x': 0.3, 'y': 0.74},
                'hip_left': {'x': 0.365, 'y': 0.67},
                'buttock_left': {'x': 0.385, 'y': 0.7},
                'thigh_left': {'x': 0.37, 'y': 0.75},
                'thigh_outer_left': {'x': 0.365, 'y': 0.76},
                'thigh_back_left': {'x': 0.385, 'y': 0.76},
                'knee_left': {'x': 0.37, 'y': 0.84},
                'knee_back_left': {'x': 0.38, 'y': 0.84},
                'shin_left': {'x': 0.365, 'y': 0.9},
                'calf_left': {'x': 0.38, 'y': 0.88},
                'ankle_left': {'x': 0.37, 'y': 0.96},
                'foot_left': {'x': 0.36, 'y': 0.98},
                'heel_left': {'x': 0.375, 'y': 0.98},
            },
            
            # SIDE RIGHT VIEW (Panel 3: x = 0.5 to 0.75) - Mirror of left
            'side_right': {
                # HEAD & NECK
                'forehead': {'x': 0.64, 'y': 0.12},
                'temples': {'x': 0.645, 'y': 0.14},
                'ears': {'x': 0.615, 'y': 0.16},
                'head_top': {'x': 0.625, 'y': 0.08},
                'head_back': {'x': 0.61, 'y': 0.12},
                'neck_side': {'x': 0.625, 'y': 0.24},
                'jaw': {'x': 0.64, 'y': 0.18},
                'chin': {'x': 0.645, 'y': 0.21},
                
                # TORSO
                'chest_middle': {'x': 0.635, 'y': 0.38},
                'ribs_right': {'x': 0.63, 'y': 0.42},
                'abdomen_middle': {'x': 0.63, 'y': 0.55},
                'pelvis': {'x': 0.625, 'y': 0.65},
                'upper_back': {'x': 0.61, 'y': 0.32},
                'middle_back': {'x': 0.605, 'y': 0.45},
                'lower_back': {'x': 0.605, 'y': 0.58},
                'spine_upper': {'x': 0.608, 'y': 0.35},
                'spine_middle': {'x': 0.608, 'y': 0.48},
                'spine_lower': {'x': 0.608, 'y': 0.6},
                
                # RIGHT SIDE ONLY
                'shoulder_right': {'x': 0.65, 'y': 0.3},
                'shoulder_top_right': {'x': 0.65, 'y': 0.28},
                'armpit_right': {'x': 0.645, 'y': 0.35},
                'upper_arm_right': {'x': 0.66, 'y': 0.42},
                'bicep_right': {'x': 0.665, 'y': 0.4},
                'tricep_right': {'x': 0.655, 'y': 0.4},
                'elbow_right': {'x': 0.67, 'y': 0.52},
                'forearm_right': {'x': 0.68, 'y': 0.6},
                'wrist_right': {'x': 0.69, 'y': 0.68},
                'hand_right': {'x': 0.7, 'y': 0.74},
                'hip_right': {'x': 0.635, 'y': 0.67},
                'buttock_right': {'x': 0.615, 'y': 0.7},
                'thigh_right': {'x': 0.63, 'y': 0.75},
                'thigh_outer_right': {'x': 0.635, 'y': 0.76},
                'thigh_back_right': {'x': 0.615, 'y': 0.76},
                'knee_right': {'x': 0.63, 'y': 0.84},
                'knee_back_right': {'x': 0.62, 'y': 0.84},
                'shin_right': {'x': 0.635, 'y': 0.9},
                'calf_right': {'x': 0.62, 'y': 0.88},
                'ankle_right': {'x': 0.63, 'y': 0.96},
                'foot_right': {'x': 0.64, 'y': 0.98},
                'heel_right': {'x': 0.625, 'y': 0.98},
            },
            
            # BACK VIEW (Panel 4: x = 0.75 to 1.0)
            'back': {
                # HEAD & NECK
                'head_back': {'x': 0.875, 'y': 0.12},
                'neck_back': {'x': 0.875, 'y': 0.24},
                'ears': {'x': 0.885, 'y': 0.16},
                'head_top': {'x': 0.875, 'y': 0.08},
                
                # TORSO - BACK
                'upper_back': {'x': 0.875, 'y': 0.32},
                'middle_back': {'x': 0.875, 'y': 0.45},
                'lower_back': {'x': 0.875, 'y': 0.58},
                'spine_upper': {'x': 0.875, 'y': 0.35},
                'spine_middle': {'x': 0.875, 'y': 0.48},
                'spine_lower': {'x': 0.875, 'y': 0.6},
                'shoulder_blades_left': {'x': 0.89, 'y': 0.34},
                'shoulder_blades_right': {'x': 0.86, 'y': 0.34},
                'kidney_area': {'x': 0.875, 'y': 0.54},
                'tailbone': {'x': 0.875, 'y': 0.65},
                
                # SHOULDERS & ARMS (back view - reversed)
                'shoulder_left': {'x': 0.92, 'y': 0.3},
                'shoulder_right': {'x': 0.83, 'y': 0.3},
                'shoulder_top_left': {'x': 0.92, 'y': 0.28},
                'shoulder_top_right': {'x': 0.83, 'y': 0.28},
                'upper_arm_left': {'x': 0.93, 'y': 0.42},
                'upper_arm_right': {'x': 0.82, 'y': 0.42},
                'tricep_left': {'x': 0.925, 'y': 0.4},
                'tricep_right': {'x': 0.825, 'y': 0.4},
                'elbow_left': {'x': 0.935, 'y': 0.52},
                'elbow_right': {'x': 0.815, 'y': 0.52},
                'forearm_left': {'x': 0.945, 'y': 0.6},
                'forearm_right': {'x': 0.805, 'y': 0.6},
                'wrist_left': {'x': 0.955, 'y': 0.68},
                'wrist_right': {'x': 0.795, 'y': 0.68},
                'hand_left': {'x': 0.965, 'y': 0.74},
                'hand_right': {'x': 0.785, 'y': 0.74},
                
                # HIPS & LEGS (back view)
                'hip_left': {'x': 0.895, 'y': 0.67},
                'hip_right': {'x': 0.855, 'y': 0.67},
                'buttock_left': {'x': 0.89, 'y': 0.7},
                'buttock_right': {'x': 0.86, 'y': 0.7},
                'thigh_back_left': {'x': 0.89, 'y': 0.76},
                'thigh_back_right': {'x': 0.86, 'y': 0.76},
                'thigh_outer_left': {'x': 0.895, 'y': 0.75},
                'thigh_outer_right': {'x': 0.855, 'y': 0.75},
                'knee_back_left': {'x': 0.89, 'y': 0.84},
                'knee_back_right': {'x': 0.86, 'y': 0.84},
                'calf_left': {'x': 0.89, 'y': 0.88},
                'calf_right': {'x': 0.86, 'y': 0.88},
                'ankle_left': {'x': 0.89, 'y': 0.96},
                'ankle_right': {'x': 0.86, 'y': 0.96},
                'heel_left': {'x': 0.89, 'y': 0.98},
                'heel_right': {'x': 0.86, 'y': 0.98},
                'foot_sole_left': {'x': 0.885, 'y': 0.99},
                'foot_sole_right': {'x': 0.865, 'y': 0.99},
            }
        }
    
    @api.onchange('body_view')
    def _onchange_body_view(self):
        """Clear body_part when view changes and update domain"""
        if self.body_view:
            self.body_part = False
            # Update the domain for body_part field
            available_parts = self._get_available_body_parts_by_view().get(self.body_view, [])
            return {
                'domain': {
                    'body_part': [('selection', 'in', available_parts)]
                }
            }
        else:
            return {
                'domain': {
                    'body_part': [('id', '=', False)]  # No options until view is selected
                }
            }
    
    def add_point(self):
        """Add the selected point to the accident record"""
        if not self.body_view:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': 'Veuillez d\'abord sélectionner une vue du corps.',
                    'type': 'warning',
                }
            }
            
        if not self.body_part:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': 'Veuillez sélectionner une partie du corps.',
                    'type': 'warning',
                }
            }
        
        # Validate that body_part is available for selected view
        available_parts = self._get_available_body_parts_by_view().get(self.body_view, [])
        if self.body_part not in available_parts:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': f'Cette partie du corps n\'est pas visible dans la vue sélectionnée.',
                    'type': 'warning',
                }
            }
        
        # Get coordinates for selected body part and view
        all_coordinates = self._get_body_part_coordinates()
        view_coords = all_coordinates.get(self.body_view, {})
        coords = view_coords.get(self.body_part)
        
        if not coords:
            coords = {'x': 0.5, 'y': 0.5}  # Fallback
        
        # Get existing annotations
        try:
            annotations = json.loads(self.accident_id.diagram_annotations or "[]")
        except:
            annotations = []
        
        # Create new annotation
        new_annotation = {
            'x': coords['x'],
            'y': coords['y'],
            'type': self.injury_type or 'injury',
            'body_part': self.body_part,
            'body_view': self.body_view,
            'description': self.description or f'{dict(self._fields["body_part"].selection)[self.body_part]}',
            'timestamp': fields.Datetime.now().isoformat()
        }
        
        # Add to annotations
        annotations.append(new_annotation)
        
        # Save to accident record
        self.accident_id.write({
            'diagram_annotations': json.dumps(annotations, indent=2)
        })
        
        # Update the image with dots
        self.accident_id.update_image_with_dots()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Point Ajouté',
                'message': f'Point ajouté sur: {dict(self._fields["body_part"].selection)[self.body_part]} ({dict(self._fields["body_view"].selection)[self.body_view]})',
                'type': 'success',
            }
        }
    
    def save_and_close(self):
        """Save all changes and close wizard"""
        return {
            'type': 'ir.actions.act_window_close'
        }