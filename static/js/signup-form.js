document.addEventListener('DOMContentLoaded', function() {
    // --- Multi-course dropdown logic (from signup-courses.js) ---
    const coursesDropdownsDiv = document.getElementById('courses-dropdowns');
    const addBtn = document.getElementById('add-course-btn');
    const errorDiv = document.getElementById('courses-error');
    if (coursesDropdownsDiv && addBtn) {
        function getSelectedCourses() {
            return Array.from(coursesDropdownsDiv.querySelectorAll('select[name="courses"]')).map(sel => sel.value).filter(v => v);
        }
        function buildDropdown(selected) {
            const select = document.createElement('select');
            select.name = 'courses';
            select.className = 'form-control mb-2';
            select.required = true;
            const options = [
                '',
                'Basics EST', 'Basics DSAT', 'Basics SAT', 'Basics L2 EST', 'Basics L2 DSAT', 'Basics L2 ACT',
                'Real Exams + Explain Basics EST', 'Real Exams + Explain Basics DSAT', 'Real Exams + Explain Basics ACT',
                'Advanced L1 EST', 'Advanced L1 DSAT', 'Advanced L1 ACT',
                'Advanced L2 EST', 'Advanced L2 DSAT', 'Advanced L2 ACT', 'EST2 Full Course'
            ];
            options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt ? opt : 'Select your course';
                if (selected === opt) option.selected = true;
                select.appendChild(option);
            });
            // Remove button
            if (coursesDropdownsDiv.childElementCount > 0) {
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn btn-link text-danger px-2';
                removeBtn.innerHTML = '<i class="fas fa-times"></i>';
                removeBtn.onclick = function() {
                    select.parentNode.remove();
                    updateDropdownOptions();
                };
                const wrapper = document.createElement('div');
                wrapper.className = 'd-flex align-items-center';
                wrapper.appendChild(select);
                wrapper.appendChild(removeBtn);
                return wrapper;
            }
            return select;
        }
        function updateDropdownOptions() {
            const selected = getSelectedCourses();
            Array.from(coursesDropdownsDiv.querySelectorAll('select[name="courses"]')).forEach(sel => {
                const current = sel.value;
                Array.from(sel.options).forEach(opt => {
                    if (opt.value === '' || opt.value === current) {
                        opt.disabled = false;
                    } else {
                        opt.disabled = selected.includes(opt.value);
                    }
                });
            });
        }
        addBtn.onclick = function() {
            const dropdown = buildDropdown('');
            coursesDropdownsDiv.appendChild(dropdown);
            updateDropdownOptions();
        };
        coursesDropdownsDiv.addEventListener('change', function(e) {
            if (e.target.tagName === 'SELECT') {
                updateDropdownOptions();
            }
        });
        // On submit, check for at least one course
        const signupForm = document.getElementById('signupForm');
        if (signupForm) {
            signupForm.addEventListener('submit', function(e) {
                if (getSelectedCourses().length === 0) {
                    e.preventDefault();
                    if (errorDiv) {
                        errorDiv.textContent = 'Please select at least one course.';
                        errorDiv.style.display = 'block';
                    }
                } else if (errorDiv) {
                    errorDiv.style.display = 'none';
                }
            });
        }
    }
    // --- End multi-course dropdown logic ---

    // 1. Phone Input Initialization (with all original features)
    const initPhoneInputs = function() {
        const studentPhone = document.getElementById('id_student_mobile');
        const parentPhone = document.getElementById('id_parent_mobile');
        
        if (!studentPhone || !parentPhone) return null;

        // Initialize with all original options
        const initTelInput = (input) => {
            // Create wrapper if needed
            if (!input.parentElement.classList.contains('input-phone-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'input-phone-wrapper position-relative';
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);
            }

            const iti = window.intlTelInput(input, {
                utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
                separateDialCode: true,
                preferredCountries: ['eg', 'us', 'sa', 'ae'],
                initialCountry: "eg",
                nationalMode: false,
                autoPlaceholder: "aggressive"
            });

            // Original dropdown width adjustment
            const updateDropdownWidth = () => {
                const dropdown = input.closest('.iti')?.querySelector('.iti__country-list');
                if (dropdown) {
                    dropdown.style.width = input.offsetWidth + 'px';
                    dropdown.style.left = '0';
                }
            };

            setTimeout(updateDropdownWidth, 100);
            window.addEventListener('resize', updateDropdownWidth);
            input.addEventListener('focus', updateDropdownWidth);

            return iti;
        };

        const studentIti = initTelInput(studentPhone);
        const parentIti = initTelInput(parentPhone);

        // Original non-numeric input prevention
        const preventNonNumeric = function(e) {
            const allowedKeys = ['Tab', 'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
            if (allowedKeys.includes(e.key)) return;
            if (e.ctrlKey || e.metaKey) return;
            if (!/^\d+$/.test(e.key)) {
                e.preventDefault();
            }
        };

        studentPhone.addEventListener('keydown', preventNonNumeric);
        parentPhone.addEventListener('keydown', preventNonNumeric);

        return { studentIti, parentIti };
    };

    // 2. Error Handling (Fixed to clear properly)
    const showError = (field, message) => {
        const container = field.closest('.form-group') || 
                         field.closest('.input-phone-wrapper') || 
                         field.parentElement;
        
        let errorElement = container.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback d-flex align-items-center';
            container.appendChild(errorElement);
        }

        errorElement.innerHTML = `<i class="fas fa-exclamation-circle m-1"></i> ${message}`;
        errorElement.style.display = 'flex';
        field.classList.add('is-invalid');
    };

    const clearError = (field) => {
        const container = field.closest('.form-group') || 
                         field.closest('.input-phone-wrapper') || 
                         field.parentElement;
        
        field.classList.remove('is-invalid');

        // Remove error message element entirely
        const errorElement = container?.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }

        // Remove any error icon if exists (also covers custom icon classes)
        const errorIcons = container?.querySelectorAll('.input-error-icon, .fa-exclamation-circle');
        if (errorIcons && errorIcons.length) {
            errorIcons.forEach(icon => icon.remove());
        }
    };

    // 3. Field Validation
    const validateField = (field, phoneInstances) => {
        let isValid = true;
        let errorMessage = '';
        
        if (field.hasAttribute('required') && !field.value.trim()) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        else if (field.type === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
        else if (field.hasAttribute('data-intl-tel-input') && field.value.trim()) {
            try {
                const iti = window.intlTelInputGlobals?.getInstance(field);
                if (iti && !iti.isValidNumber()) {
                    isValid = false;
                    errorMessage = 'Please enter a valid phone number';
                }
            } catch (e) {
                isValid = false;
                errorMessage = 'Please enter a valid phone number';
            }
        }
        else if (field.id === 'id_password2' && field.value) {
            const password1 = document.getElementById('id_password1');
            if (password1 && password1.value !== field.value) {
                isValid = false;
                errorMessage = 'Passwords do not match';
            }
        }
        else if ((field.id === 'id_grade_level' || field.id === 'id_course') && !field.value) {
            isValid = false;
            errorMessage = 'Please select an option';
        }
        
        if (!isValid) {
            showError(field, errorMessage);
        } else {
            clearError(field);
        }
        
        return isValid;
    };

    // 4. Form Setup with Fixed Event Handling
    const setupForm = function() {
        const form = document.getElementById('signupForm');
        if (!form) return;

        const phoneInstances = initPhoneInputs();
        const fields = form.querySelectorAll('input, select');
        
        // Clear errors immediately when typing (FIXED)
        fields.forEach(field => {
            field.addEventListener('input', function() {
                // Clear both border and error message immediately
                clearError(this);
                
                // For phone fields, validate as user types
                if (this.hasAttribute('data-intl-tel-input')) {
                    validateField(this, phoneInstances);
                }
            });
            
            // Validate on blur
            field.addEventListener('blur', function() {
                validateField(this, phoneInstances);

                // Live uniqueness validation for username, email, student_mobile
                if (this.id === 'id_username') {
                    const val = this.value.trim();
                    if (val) {
                        fetch('/accounts/ajax/check-username/?username=' + encodeURIComponent(val))
                            .then(res => res.json())
                            .then(data => {
                                if (data.exists) {
                                    showError(this, 'This username is already taken');
                                } else {
                                    clearError(this);
                                }
                            });
                    }
                } else if (this.id === 'id_email') {
                    const val = this.value.trim();
                    if (val) {
                        fetch('/accounts/ajax/check-email/?email=' + encodeURIComponent(val))
                            .then(res => res.json())
                            .then(data => {
                                if (data.invalid) {
                                    showError(this, 'Please enter a valid email address');
                                } else if (data.exists) {
                                    showError(this, 'This email is already registered');
                                } else {
                                    clearError(this);
                                }
                            });
                    }
                } else if (this.id === 'id_student_mobile') {
                    const val = this.value.trim();
                    if (val) {
                        fetch('/accounts/ajax/check-student-number/?student_mobile=' + encodeURIComponent(val))
                            .then(res => res.json())
                            .then(data => {
                                if (data.exists) {
                                    showError(this, 'This student number is already used');
                                } else {
                                    clearError(this);
                                }
                            });
                    }
                }
            });
        });

        // Form submission
        form.addEventListener('submit', function(e) {
            let isValid = true;
            let firstInvalidField = null;
            
            fields.forEach(field => {
                if (!validateField(field, phoneInstances)) {
                    if (!firstInvalidField) firstInvalidField = field;
                    isValid = false;
                }
            });

            // Format phone numbers before submission
            if (phoneInstances) {
                const studentPhone = document.getElementById('id_student_mobile');
                const parentPhone = document.getElementById('id_parent_mobile');
                studentPhone.value = phoneInstances.studentIti.isValidNumber() ? 
                    phoneInstances.studentIti.getNumber() : studentPhone.value;
                parentPhone.value = phoneInstances.parentIti.isValidNumber() ? 
                    phoneInstances.parentIti.getNumber() : parentPhone.value;
            }

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

    // 5. Initialize with Dependency Check
    function checkDependencies() {
        if (window.intlTelInput && window.intlTelInputGlobals) {
            setupForm();
        } else {
            setTimeout(checkDependencies, 100);
        }
    }

    // Load intl-tel-input if not available
    if (!window.intlTelInput) {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/intlTelInput.min.js';
        document.body.appendChild(script);
    }
    
    checkDependencies();
});