document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------
    // LOGIN SOLO ADMIN (login.html)
    // ---------------------------
    const loginFormAdmin = document.getElementById('login-form');
    if (loginFormAdmin) {
        const errorMessage = document.getElementById('error-message');
        const passwordInput = document.getElementById('password');
        const usernameInput = document.getElementById('username');

        // Si ya está logueado como admin, redirigir
        if (sessionStorage.getItem('isAdminAuthenticated') === 'true') {
            window.location.href = 'admin.html';
        }

        loginFormAdmin.addEventListener('submit', (e) => {
            e.preventDefault();

            const username = usernameInput.value.trim();
            const password = passwordInput.value.trim();

            if (username === 'admin' && password === 'admin123') {
                sessionStorage.setItem('isAdminAuthenticated', 'true');
                window.location.href = 'admin.html';
            } else {
                errorMessage.textContent = 'Usuario o contraseña incorrectos.';
                passwordInput.focus();
            }
        });
    }

    // ---------------------------
    // LOGIN GENERAL (index.html)
    // ---------------------------
    const loginFormGeneral = document.getElementById('login-form');
    if (loginFormGeneral && document.getElementById('login-email')) {
        loginFormGeneral.addEventListener('submit', async function (e) {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;

            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();
            if (data.ok) {
                if (data.role === 'admin') {
                    // Si es administrador → ir al panel
                    sessionStorage.setItem('isAdminAuthenticated', 'true');
                    window.location.href = 'admin.html';
                } else {
                    // Si es cliente → a la tienda
                    window.location.href = 'index.html';
                }
            } else {
                const errorEl = document.getElementById('login-error');
                errorEl.textContent = data.error || 'Error al iniciar sesión';
                errorEl.classList.remove('hidden');
            }
        });
    }
});
