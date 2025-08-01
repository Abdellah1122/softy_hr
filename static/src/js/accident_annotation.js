/* 
 * Accident Diagram Annotation System for Odoo 18
 * File: static/src/js/accident_annotation.js
 */

(function() {
    'use strict';

    let annotationSystem = {
        canvas: null,
        ctx: null,
        annotations: [],
        annotationMode: false,
        originalImage: null,
        imageLoaded: false,
        initialized: false,

        init: function() {
            if (this.initialized) return;
            
            // Wait for DOM and then initialize
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
            this.initialized = true;
        },

        setup: function() {
            // Use MutationObserver to detect when accident form is loaded
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.addedNodes.length > 0) {
                        this.checkForAccidentForm();
                    }
                });
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            // Also check immediately
            setTimeout(() => this.checkForAccidentForm(), 1000);
        },

        checkForAccidentForm: function() {
            const canvas = document.getElementById('diagram_canvas');
            if (canvas && !this.canvas) {
                console.log('Accident form detected, initializing annotation system...');
                this.initializeCanvas();
                this.bindEvents();
            }
        },

        initializeCanvas: function() {
            this.canvas = document.getElementById('diagram_canvas');
            if (!this.canvas) return;

            this.ctx = this.canvas.getContext('2d');
            this.loadDiagramImage();
        },

        loadDiagramImage: function() {
            // Try to get image from Odoo field
            const imageField = document.querySelector('field[name="diagram_image"] img');
            let imageSrc = null;

            if (imageField) {
                imageSrc = imageField.src;
            } else {
                // Fallback: try to find any image in the illustration container
                const containerImages = document.querySelectorAll('.o_accident_illustration_container img');
                if (containerImages.length > 0) {
                    imageSrc = containerImages[0].src;
                }
            }

            if (imageSrc) {
                const img = new Image();
                img.onload = () => {
                    this.originalImage = img;
                    this.drawImageToCanvas();
                    this.imageLoaded = true;
                    this.loadExistingAnnotations();
                };
                img.crossOrigin = "anonymous";
                img.src = imageSrc;
            } else {
                console.log('No image found, retrying...');
                setTimeout(() => this.loadDiagramImage(), 1000);
            }
        },

        drawImageToCanvas: function() {
            if (!this.originalImage || !this.canvas) return;

            // Set canvas size
            const maxWidth = 800;
            const scale = Math.min(maxWidth / this.originalImage.width, 1);
            
            this.canvas.width = this.originalImage.width * scale;
            this.canvas.height = this.originalImage.height * scale;
            
            // Draw image
            this.ctx.drawImage(this.originalImage, 0, 0, this.canvas.width, this.canvas.height);
            this.redrawAnnotations();
        },

        bindEvents: function() {
            // Annotation mode button
            document.addEventListener('click', (e) => {
                if (e.target.id === 'annotation_mode_btn' || e.target.closest('#annotation_mode_btn')) {
                    e.preventDefault();
                    this.toggleAnnotationMode();
                }
            });

            // Clear annotations button
            document.addEventListener('click', (e) => {
                if (e.target.id === 'clear_annotations_btn' || e.target.closest('#clear_annotations_btn')) {
                    e.preventDefault();
                    this.clearAnnotations();
                }
            });

            // Save annotations button
            document.addEventListener('click', (e) => {
                if (e.target.id === 'save_annotations_btn' || e.target.closest('#save_annotations_btn')) {
                    e.preventDefault();
                    this.saveAnnotations();
                }
            });

            // Canvas click
            document.addEventListener('click', (e) => {
                if (e.target.id === 'diagram_canvas' && this.annotationMode) {
                    this.addAnnotation(e);
                }
            });
        },

        toggleAnnotationMode: function() {
            this.annotationMode = !this.annotationMode;
            const btn = document.getElementById('annotation_mode_btn');
            const status = document.getElementById('annotation_status');
            
            if (btn && status) {
                if (this.annotationMode) {
                    btn.className = btn.className.replace('btn-primary', 'btn-danger');
                    btn.innerHTML = '<i class="fa fa-times"/> Désactiver';
                    this.canvas.style.cursor = 'crosshair';
                    status.style.display = 'block';
                } else {
                    btn.className = btn.className.replace('btn-danger', 'btn-primary');
                    btn.innerHTML = '<i class="fa fa-crosshairs"/> Mode Annotation';
                    this.canvas.style.cursor = 'default';
                    status.style.display = 'none';
                }
            }
        },

        addAnnotation: function(event) {
            if (!this.imageLoaded) return;

            const rect = this.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            // Convert to relative coordinates
            const relX = x / this.canvas.width;
            const relY = y / this.canvas.height;

            this.annotations.push({
                x: relX,
                y: relY,
                timestamp: new Date().toISOString()
            });

            this.drawAnnotation(x, y);
        },

        drawAnnotation: function(x, y) {
            this.ctx.save();
            this.ctx.fillStyle = '#d32f2f';
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            
            this.ctx.beginPath();
            this.ctx.arc(x, y, 8, 0, 2 * Math.PI);
            this.ctx.fill();
            this.ctx.stroke();
            
            this.ctx.restore();
        },

        redrawAnnotations: function() {
            if (!this.annotations.length || !this.canvas) return;

            for (let i = 0; i < this.annotations.length; i++) {
                const annotation = this.annotations[i];
                const x = annotation.x * this.canvas.width;
                const y = annotation.y * this.canvas.height;
                this.drawAnnotation(x, y);
            }
        },

        clearAnnotations: function() {
            this.annotations = [];
            this.drawImageToCanvas();
        },

        loadExistingAnnotations: function() {
            // Try to get annotations from hidden field
            const annotationField = document.querySelector('field[name="diagram_annotations"] input');
            if (annotationField && annotationField.value) {
                try {
                    this.annotations = JSON.parse(annotationField.value);
                    this.redrawAnnotations();
                } catch (e) {
                    console.error('Error loading annotations:', e);
                    this.annotations = [];
                }
            }
        },

        saveAnnotations: function() {
            if (!this.canvas) {
                this.showNotification('Erreur: Canvas non disponible', 'danger');
                return;
            }

            // Get the current record ID from URL or form
            const urlParams = new URLSearchParams(window.location.search);
            const recordId = urlParams.get('id') || this.getRecordIdFromForm();

            if (!recordId) {
                this.showNotification('Erreur: Impossible de déterminer l\'ID de l\'enregistrement', 'danger');
                return;
            }

            // Convert canvas to base64
            const imageData = this.canvas.toDataURL('image/png');

            // Make AJAX call to save
            fetch('/web/dataset/call_kw', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        model: 'softy.accident',
                        method: 'save_annotated_diagram',
                        args: [parseInt(recordId), imageData, this.annotations],
                        kwargs: {}
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.result) {
                    this.showNotification('Annotations sauvegardées avec succès!', 'success');
                    // Update hidden field
                    const annotationField = document.querySelector('field[name="diagram_annotations"] input');
                    if (annotationField) {
                        annotationField.value = JSON.stringify(this.annotations);
                    }
                } else {
                    this.showNotification('Erreur lors de la sauvegarde', 'danger');
                }
            })
            .catch(error => {
                console.error('Save error:', error);
                this.showNotification('Erreur lors de la sauvegarde: ' + error.message, 'danger');
            });
        },

        getRecordIdFromForm: function() {
            // Try different methods to get record ID
            const urlMatch = window.location.pathname.match(/\/(\d+)$/);
            if (urlMatch) return urlMatch[1];

            // Try to find in form data
            const idField = document.querySelector('input[name="id"]');
            if (idField) return idField.value;

            return null;
        },

        showNotification: function(message, type) {
            type = type || 'info';
            const alertClass = 'alert-' + (type === 'danger' ? 'danger' : type === 'success' ? 'success' : 'info');
            
            const notification = document.createElement('div');
            notification.className = `alert ${alertClass} alert-dismissible accident-notification`;
            notification.style.cssText = 'position: fixed; top: 100px; right: 20px; z-index: 9999; max-width: 400px;';
            notification.innerHTML = `
                <button type="button" class="close" onclick="this.parentElement.remove()">&times;</button>
                ${message}
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 5000);
        }
    };

    // Initialize when script loads
    annotationSystem.init();

    // Also initialize on URL changes (for SPA navigation)
    let currentUrl = window.location.href;
    setInterval(() => {
        if (window.location.href !== currentUrl) {
            currentUrl = window.location.href;
            setTimeout(() => annotationSystem.checkForAccidentForm(), 500);
        }
    }, 1000);

})();