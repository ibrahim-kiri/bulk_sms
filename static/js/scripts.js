document.addEventListener('DOMContentLoaded', function() {
    // Form placeholder handling
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    // Add interactive form behaviors
    if (usernameInput) {
        usernameInput.addEventListener('focus', function() {
            this.classList.add('focused');
        });

        usernameInput.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('focus', function() {
            this.classList.add('focused');
        });

        passwordInput.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    }

    // Simple form validation
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            if (username === '' || password === '') {
                event.preventDefault();
                alert('Please enter both username and password');
            }
        });
    }

    // Responsive menu toggle (though Bootstrap handles most of this)
    const navToggler = document.querySelector('.navbar-toggler');
    const navMenu = document.getElementById('mainNavbar');

    if (navToggler && navMenu) {
        navToggler.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
    }
});