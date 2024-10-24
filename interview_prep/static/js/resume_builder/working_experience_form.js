class WorkExperienceForm {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.descriptionContainer = this.form.querySelector('.description-container');
        this.descriptionPoints = [];
        this.setupEventListeners();
        this.setupDescriptionControls();
    }

    setupEventListeners() {
        // Handle real-time updates for basic fields
        this.form.addEventListener('input', (e) => {
            const field = e.target;
            
            switch(field.id) {
                case 'jobTitle':
                    this.updateWithBoldPreserved(
                        document.getElementById('preview-jobTitle'),
                        `${field.value}`
                    );
                    break;
                    
                case 'company':
                    this.updateWithBoldPreserved(
                        document.getElementById('preview-job'),
                        field.value
                    );
                    break;
                    
                case 'city':
                    const locationPreview = document.getElementById('preview-location');
                    if (locationPreview) locationPreview.textContent = field.value;
                    break;
                    
                case 'startDate':
                    this.updateDateField('start', field.value);
                    break;
                    
                case 'endDate':
                    this.updateDateField('end', field.value);
                    break;
            }
        });

        // Handle is_current checkbox
        const currentCheckbox = this.form.querySelector('#is_current');
        if (currentCheckbox) {
            currentCheckbox.addEventListener('change', (e) => {
                const endDateField = this.form.querySelector('#endDate');
                if (endDateField) {
                    endDateField.disabled = e.target.checked;
                    if (e.target.checked) {
                        this.updateDateField('end', 'Current');
                    } else {
                        this.updateDateField('end', endDateField.value || '');
                    }
                }
            });
        }
    }

    setupDescriptionControls() {
        // Add description controls
        const controls = document.createElement('div');
        controls.className = 'description-controls';
        
        const addButton = document.createElement('button');
        addButton.textContent = '+ Add Description';
        addButton.type = 'button';
        addButton.className = 'add-description-btn';
        addButton.addEventListener('click', () => this.addDescriptionField());
        
        controls.appendChild(addButton);
        this.form.appendChild(controls);

        // Add initial description field
        this.addDescriptionField();
    }

    addDescriptionField(value = '') {
        const pointContainer = document.createElement('div');
        pointContainer.className = 'description-point-container';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'description-input';
        input.value = value;
        input.placeholder = 'Enter job description point';

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '×';
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-description-btn';
        deleteBtn.addEventListener('click', () => {
            pointContainer.remove();
            this.updateDescriptionPreview();
        });

        const moveUpBtn = document.createElement('button');
        moveUpBtn.textContent = '↑';
        moveUpBtn.type = 'button';
        moveUpBtn.className = 'move-description-btn';
        moveUpBtn.addEventListener('click', () => this.moveDescriptionPoint(pointContainer, -1));

        const moveDownBtn = document.createElement('button');
        moveDownBtn.textContent = '↓';
        moveDownBtn.type = 'button';
        moveDownBtn.className = 'move-description-btn';
        moveDownBtn.addEventListener('click', () => this.moveDescriptionPoint(pointContainer, 1));

        pointContainer.appendChild(input);
        pointContainer.appendChild(deleteBtn);
        pointContainer.appendChild(moveUpBtn);
        pointContainer.appendChild(moveDownBtn);

        input.addEventListener('input', () => this.updateDescriptionPreview());

        this.descriptionContainer.appendChild(pointContainer);
        this.updateDescriptionPreview();
    }

    moveDescriptionPoint(container, direction) {
        const containers = Array.from(this.descriptionContainer.children);
        const currentIndex = containers.indexOf(container);
        const newIndex = currentIndex + direction;

        if (newIndex >= 0 && newIndex < containers.length) {
            const referenceNode = direction > 0 ? 
                containers[newIndex].nextSibling : 
                containers[newIndex];
            this.descriptionContainer.insertBefore(container, referenceNode);
            this.updateDescriptionPreview();
        }
    }

    updateDescriptionPreview() {
        const previewDescription = document.querySelector('.preview-description');
        if (!previewDescription) return;
        
        previewDescription.innerHTML = '';
        
        const inputs = this.descriptionContainer.querySelectorAll('.description-input');
        inputs.forEach(input => {
            if (input.value.trim()) {
                const bulletPoint = document.createElement('div');
                bulletPoint.className = 'description-point';
                bulletPoint.innerHTML = `<span>&#x2022; ${input.value}</span>`;
                previewDescription.appendChild(bulletPoint);
            }
        });
    }

    updateWithBoldPreserved(element, newText) {
        if (!element) return;
        
        if (element.innerHTML.includes('<b>')) {
            element.innerHTML = `<b>${newText}</b>`;
        } else {
            element.textContent = newText;
        }
    }

    updateDateField(type, value) {
        const preview = document.getElementById(`preview-${type}-date`);
        if (preview) {
            if (type === 'end' && value === 'Current') {
                preview.textContent = 'Current';
            } else {
                // Format date as MM/YYYY
                try {
                    const date = new Date(value);
                    if (!isNaN(date)) {
                        preview.textContent = `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getFullYear()}`;
                    } else {
                        preview.textContent = value;
                    }
                } catch (e) {
                    preview.textContent = value;
                }
            }
        }
    }

    // Method to get form data for submission
    getFormData() {
        const formData = new FormData(this.form);
        const descriptions = [];
        
        this.descriptionContainer.querySelectorAll('.description-input').forEach((input, index) => {
            if (input.value.trim()) {
                descriptions.push({
                    description: input.value.trim(),
                    order: index
                });
            }
        });
        
        formData.append('descriptions', JSON.stringify(descriptions));
        return formData;
    }
}

// Initialize the form
const workExperienceForm = new WorkExperienceForm('experience-form');
