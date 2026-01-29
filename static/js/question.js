// questions.js
document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle sub-question fields
    function toggleSubQuestionFields(checkbox) {
        const name = checkbox.name || checkbox.id;
        const match = name.match(/form-(\d+)-/);
        if (!match) return;
        
        const formIndex = match[1];
        const parentField = document.getElementById(`id_form-${formIndex}-parent_question`);
        const letterField = document.getElementById(`id_form-${formIndex}-sub_question_letter`);
        
        if (!parentField || !letterField) return;
        
        const parentContainer = parentField.closest('.form-group') || parentField.parentElement;
        const letterContainer = letterField.closest('.form-group') || letterField.parentElement;
        
        if (checkbox.checked) {
            if (parentContainer) parentContainer.style.display = 'block';
            if (letterContainer) letterContainer.style.display = 'block';
            if (parentField) parentField.required = true;
            if (letterField) letterField.required = true;
        } else {
            if (parentContainer) parentContainer.style.display = 'none';
            if (letterContainer) letterContainer.style.display = 'none';
            if (parentField) parentField.required = false;
            if (letterField) letterField.required = false;
            if (parentField) parentField.value = '';
            if (letterField) letterField.value = '';
        }
    }
    
    // Initialize all sub-question checkboxes
    document.querySelectorAll('input[type="checkbox"][id*="is_sub_question"]').forEach(function(checkbox) {
        // Initial state
        toggleSubQuestionFields(checkbox);
        
        // Add event listener
        checkbox.addEventListener('change', function() {
            toggleSubQuestionFields(this);
        });
    });
    
    // Image preview functionality
    document.querySelectorAll('input[type="file"][id*="question_image"]').forEach(function(input) {
        const previewId = `preview-${input.name.replace(/[\[\]]/g, '-')}`;
        let previewContainer = document.getElementById(previewId);
        
        // Create preview container if it doesn't exist
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'image-preview-container mt-2';
            previewContainer.id = previewId;
            const previewImg = document.createElement('img');
            previewImg.className = 'image-preview';
            previewImg.style.display = 'none';
            previewContainer.appendChild(previewImg);
            input.parentNode.appendChild(previewContainer);
        }
        
        const previewImg = previewContainer.querySelector('img');
        
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    previewImg.style.display = 'block';
                }
                
                reader.readAsDataURL(this.files[0]);
            } else {
                previewImg.style.display = 'none';
            }
        });
    });
    
    // Update image position description
    document.querySelectorAll('select[id*="question_image_position"]').forEach(function(select) {
        const infoContainer = document.createElement('div');
        infoContainer.className = 'image-position-info mt-1';
        select.parentNode.appendChild(infoContainer);
        
        function updateDescription() {
            const value = select.value;
            let description = '';
            
            switch(value) {
                case 'split':
                    description = '<strong>Split:</strong> First line appears above image, image centered, rest below image';
                    break;
                case 'top':
                    description = '<strong>Top:</strong> Image appears above all text';
                    break;
                case 'middle':
                    description = '<strong>Middle:</strong> Text split equally above and below image';
                    break;
                case 'bottom':
                    description = '<strong>Bottom:</strong> Image appears below all text';
                    break;
                default:
                    description = 'Select image position';
            }
            
            infoContainer.innerHTML = description;
        }
        
        // Initial description
        updateDescription();
        
        // Update on change
        select.addEventListener('change', updateDescription);
    });
    
    // Form validation for sub-question letters
    document.querySelectorAll('input[id*="sub_question_letter"]').forEach(function(input) {
        input.addEventListener('blur', function() {
            const value = this.value.trim();
            if (value && !/^[a-z]$|^[ivx]+$/i.test(value)) {
                alert('Sub-question letter should be a single letter (a, b, c) or Roman numeral (i, ii, iii, iv, etc.)');
                this.focus();
            }
        });
    });
    
    // Auto-fill module outcome based on module
    document.querySelectorAll('select[id*="module"], input[id*="module"]').forEach(function(field) {
        const formIndex = (field.name || field.id).match(/form-(\d+)-/);
        if (!formIndex) return;
        
        const outcomeField = document.getElementById(`id_form-${formIndex[1]}-module_outcome`);
        if (!outcomeField) return;
        
        field.addEventListener('change', function() {
            const moduleNum = this.value;
            if (moduleNum && !outcomeField.value) {
                outcomeField.value = `M${moduleNum}.01`;
            }
        });
    });
    
    // Character counter for question text
    document.querySelectorAll('textarea[id*="question"]').forEach(function(textarea) {
        const counter = document.createElement('small');
        counter.className = 'text-muted float-end';
        counter.textContent = '0 characters';
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            counter.textContent = `${this.value.length} characters`;
        });
        
        // Trigger initial count
        textarea.dispatchEvent(new Event('input'));
    });
});