document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('#id_password1');
    const requirements = {
        length: password => password.length >= 8,
        numeric: password => !/^\d+$/.test(password),
        common: password => {
            // This is a basic check - Django will do the full validation
            const commonPasswords = ['password', '12345678', 'qwerty'];
            return !commonPasswords.includes(password.toLowerCase());
        },
        personal: () => true  // This will be handled by Django's backend validation
    };

    function validatePassword() {
        const password = passwordInput.value;
        
        Object.entries(requirements).forEach(([requirement, validateFn]) => {
            const requirementElement = document.querySelector(`[data-requirement="${requirement}"]`);
            if (!requirementElement) return;

            if (password && !validateFn(password)) {
                requirementElement.style.display = 'block';
                requirementElement.querySelector('span').classList.remove('text-green-600');
                requirementElement.querySelector('span').classList.add('text-red-600');
            } else if (!password) {
                requirementElement.style.display = 'block';
                requirementElement.querySelector('span').classList.remove('text-green-600');
                requirementElement.querySelector('span').classList.add('text-red-600');
            } else {
                requirementElement.style.display = 'none';
            }
        });
    }

    passwordInput.addEventListener('input', validatePassword);
    validatePassword();  // Initial validation

    // Style Django form inputs
    const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
    inputs.forEach(input => {
        input.classList.add('w-full', 'px-4', 'py-2', 'border', 'border-gray-300', 'rounded-lg', 'focus:border-blue-600', 'focus:ring-2', 'focus:ring-blue-600', 'focus:ring-opacity-50', 'focus:outline-none');
    });
});