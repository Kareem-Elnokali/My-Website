document.addEventListener('DOMContentLoaded', function() {
    // Helper function to create error message elements
    const createErrorElements = function(field) {
        const fieldContainer = field.closest('.form-group');
        if (!fieldContainer.querySelector('.invalid-feedback')) {
            const errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            fieldContainer.appendChild(errorElement);
        }
    };

    // Field validation function with error messages
    const validateField = function(field) {
        const fieldContainer = field.closest('.form-group');
        if (!fieldContainer) return true;
        
        const errorElement = fieldContainer.querySelector('.invalid-feedback');
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (field.hasAttribute('required') && !field.value.trim()) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Email format validation (if the field is email)
        else if (field.type === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
        
        // Update field appearance and error message
        if (errorElement) {
            if (!isValid) {
                errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${errorMessage}`;
                errorElement.style.display = 'block';
                field.classList.add('is-invalid');
            } else {
                errorElement.style.display = 'none';
                field.classList.remove('is-invalid');
            }
        }
        
        return isValid;
    };

    // Initialize form validation
    const initFormValidation = function() {
        const form = document.getElementById('loginForm');
        if (!form) return;

        // Get all required fields
        const requiredFields = form.querySelectorAll('[required]');
        
        // Add event listeners to all fields
        requiredFields.forEach(field => {
            createErrorElements(field);
            
            // Validate on input (clear errors)
            field.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                const errorElement = this.closest('.form-group').querySelector('.invalid-feedback');
                if (errorElement) errorElement.style.display = 'none';
            });
            
            // Validate on blur
            field.addEventListener('blur', function() {
                validateField(this);
            });
        });

        // Form submission validation
        form.addEventListener('submit', function(e) {
            let isValid = true;
            let firstInvalidField = null;

            requiredFields.forEach(field => {
                if (!validateField(field)) {
                    if (!firstInvalidField) firstInvalidField = field;
                    isValid = false;
                }
            });

            if (!isValid) {
                e.preventDefault();
                if (firstInvalidField) {
                    firstInvalidField.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                    firstInvalidField.focus();
                }
            }
        });
    };

    // Initialize form validation on load
    initFormValidation();
});