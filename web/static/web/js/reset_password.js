document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // 1. MOSTRAR/OCULTAR CONTRASEÑA (Para múltiples campos)
    // ============================================
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Encuentra el input que está justo al lado de este botón
            const input = this.previousElementSibling;
            if(input) {
                const newType = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', newType);
                
                const icon = this.querySelector('i');
                if (newType === 'text') {
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            }
        });
    });

    // ============================================
    // 2. CERRAR MENSAJE DE ERROR INTERACTIVO
    // ============================================
    const closeErrorBtn = document.querySelector('.close-error');
    const errorAlert = document.getElementById('reset-error');
    if (closeErrorBtn && errorAlert) {
        closeErrorBtn.addEventListener('click', function() {
            errorAlert.style.opacity = '0';
            setTimeout(() => { errorAlert.style.display = 'none'; }, 300); 
        });
    }

    // ============================================
    // 3. VENTANITA SUTIL DE SEGURIDAD Y COINCIDENCIA
    // ============================================
    const passwordInput = document.getElementById('password');
    const pswdConfirm = document.getElementById('password-confirm');
    const pswdChecker = document.getElementById('pswd-checker');
    const matchMsg = document.getElementById('match-msg');
    const btnSubmit = document.getElementById('btn-update-password');
    
    if (passwordInput && pswdChecker) {
        const reqLength = document.getElementById('length');
        const reqNumber = document.getElementById('number');
        const reqUpper = document.getElementById('upper');

        passwordInput.addEventListener('focus', () => { pswdChecker.classList.add('active'); });
        passwordInput.addEventListener('blur', () => { if (passwordInput.value === "") pswdChecker.classList.remove('active'); });

        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            // Validaciones
            const hasLength = val.length >= 8;
            const hasNumber = /\d/.test(val);
            const hasUpper = /[A-Z]/.test(val);

            // Actualizar ventanita
            if (hasLength) { reqLength.classList.add('valid'); reqLength.querySelector('span').innerText = '✔'; } 
            else { reqLength.classList.remove('valid'); reqLength.querySelector('span').innerText = '⬤'; }
            
            if (hasNumber) { reqNumber.classList.add('valid'); reqNumber.querySelector('span').innerText = '✔'; } 
            else { reqNumber.classList.remove('valid'); reqNumber.querySelector('span').innerText = '⬤'; }
            
            if (hasUpper) { reqUpper.classList.add('valid'); reqUpper.querySelector('span').innerText = '✔'; } 
            else { reqUpper.classList.remove('valid'); reqUpper.querySelector('span').innerText = '⬤'; }

            // Si ya escribió algo abajo, verificar coincidencia
            if (pswdConfirm && pswdConfirm.value !== '') {
                checkMatch();
            }
        });
    }

    // Validar coincidencia en vivo
    if (pswdConfirm && passwordInput && matchMsg) {
        pswdConfirm.addEventListener('input', checkMatch);
    }

    function checkMatch() {
        if (pswdConfirm.value === '') {
            matchMsg.style.display = 'none';
            if(btnSubmit) btnSubmit.disabled = false;
        } else if (pswdConfirm.value === passwordInput.value) {
            matchMsg.textContent = '✔ Las contraseñas coinciden';
            matchMsg.style.color = '#22c55e'; // Verde
            matchMsg.style.display = 'block';
            if(btnSubmit) btnSubmit.disabled = false;
        } else {
            matchMsg.textContent = '❌ Las contraseñas no coinciden';
            matchMsg.style.color = '#ef4444'; // Rojo
            matchMsg.style.display = 'block';
            if(btnSubmit) btnSubmit.disabled = true; // Bloquea el botón
        }
    }
});