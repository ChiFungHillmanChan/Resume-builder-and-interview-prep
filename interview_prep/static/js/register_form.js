document.addEventListener('DOMContentLoaded', function() {
    // Get password input, confirm password input and requirements container
    const passwordInput = document.querySelector('#id_password1');
    const confirmPasswordInput = document.querySelector('#id_password2');
    const requirementsContainer = document.querySelector('#passwordRequirements');
    const confirmPasswordMessage = document.querySelector('#confirmPasswordMessage');
    
    // Define password requirements with validation functions
    const requirements = {
        length: {
            validate: password => password.length >= 8,
            message: '• Must contain at least 8 characters'
        },
        numeric: {
            validate: password => !/^\d+$/.test(password),
            message: '• Can\'t be entirely numeric'
        },
        common: {
            validate: password => {
                const commonPasswords = [
                    'password', '12345678', 'qwerty', 'admin123',
                    'letmein', 'welcome', 'monkey123', 'football'
                ];
                return !commonPasswords.includes(password.toLowerCase());
            },
            message: '• Can\'t be a commonly used password'
        }
    };

    // Create requirement elements dynamically
    Object.entries(requirements).forEach(([key, { message }]) => {
        const requirementDiv = document.createElement('div');
        requirementDiv.className = 'requirement';
        requirementDiv.setAttribute('data-requirement', key);
        requirementDiv.innerHTML = `<span class="text-red-500">${message}</span>`;
        requirementsContainer.appendChild(requirementDiv);
    });

    function validatePassword() {
        const password = passwordInput.value;
        
        // Show requirements only when user starts typing
        if (password) {
            requirementsContainer.classList.remove('hidden');
        } else {
            requirementsContainer.classList.add('hidden');
        }

        Object.entries(requirements).forEach(([requirement, { validate }]) => {
            const requirementElement = document.querySelector(`[data-requirement="${requirement}"]`);
            if (!requirementElement) return;

            const span = requirementElement.querySelector('span');
            
            if (validate(password)) {
                span.className = 'text-green-500';
            } else {
                span.className = 'text-red-500';
            }
        });

        // Validate confirm password when main password changes
        if (confirmPasswordInput.value) {
            validateConfirmPassword();
        }
    }

    function validateConfirmPassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Show confirmation message only when user starts typing in confirm password field
        if (confirmPassword) {
            confirmPasswordMessage.classList.remove('hidden');
            if (password === confirmPassword) {
                confirmPasswordMessage.className = 'text-green-500 text-sm mt-1';
                confirmPasswordMessage.textContent = 'Passwords match';
            } else {
                confirmPasswordMessage.className = 'text-red-500 text-sm mt-1';
                confirmPasswordMessage.textContent = 'Passwords do not match';
            }
        } else {
            confirmPasswordMessage.classList.add('hidden');
        }
    }

    // Event listeners for password input
    passwordInput.addEventListener('input', validatePassword);
    passwordInput.addEventListener('blur', () => {
        if (!passwordInput.value) {
            requirementsContainer.classList.add('hidden');
        }
    });

    // Event listeners for confirm password
    confirmPasswordInput.addEventListener('input', validateConfirmPassword);

    // Style all form inputs (remains the same)
    const formInputs = document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"]');
    formInputs.forEach(input => {
        input.classList.add(
            'appearance-none',
            'block',
            'w-full',
            'px-3',
            'py-2',
            'rounded-md',
            'border',
            'border-gray-300',
            'shadow-sm',
            'placeholder-gray-400',
            'focus:ring-blue-500',
            'focus:border-blue-500',
            'focus:outline-none',
            'sm:text-sm'
        );

        // Add placeholder text based on input name
        if (input.name === 'email') {
            input.placeholder = 'Enter your email';
        } else if (input.name === 'username') {
            input.placeholder = 'Choose a username';
        } else if (input.name === 'password1') {
            input.placeholder = 'Enter password';
        } else if (input.name === 'password2') {
            input.placeholder = 'Confirm password';
        }
    });
});