document.addEventListener('DOMContentLoaded', function() {
    // 1. Mostrar/Ocultar Contraseña
    const togglePasswordBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', function() {
            // Verificamos el tipo actual y lo cambiamos
            const currentType = passwordInput.getAttribute('type');
            const newType = currentType === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', newType);
            
            // Cambiamos el icono de FontAwesome
            const icon = this.querySelector('i');
            if (newType === 'text') {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }

    // 2. Cerrar mensaje de error interactivo
    const closeErrorBtn = document.querySelector('.close-error');
    const errorAlert = document.getElementById('login-error');

    if (closeErrorBtn && errorAlert) {
        closeErrorBtn.addEventListener('click', function() {
            // Desvanece el elemento primero
            errorAlert.style.opacity = '0';
            // Lo oculta del DOM tras terminar la transición
            setTimeout(() => {
                errorAlert.style.display = 'none';
            }, 300); 
        });
    }
});