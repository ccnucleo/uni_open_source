document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // 1. MOSTRAR/OCULTAR CONTRASEÑA
    // ============================================
    const togglePasswordBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', function() {
            const currentType = passwordInput.getAttribute('type');
            const newType = currentType === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', newType);
            
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

    // ============================================
    // 2. CERRAR MENSAJE DE ERROR INTERACTIVO
    // ============================================
    const closeErrorBtn = document.querySelector('.close-error');
    const errorAlert = document.getElementById('register-error');

    if (closeErrorBtn && errorAlert) {
        closeErrorBtn.addEventListener('click', function() {
            errorAlert.style.opacity = '0';
            setTimeout(() => { errorAlert.style.display = 'none'; }, 300); 
        });
    }

    // ============================================
    // 3. VENTANITA SUTIL DE SEGURIDAD (CONTRASEÑA)
    // ============================================
    const pswdChecker = document.getElementById('pswd-checker');
    
    if (passwordInput && pswdChecker) {
        const reqLength = document.getElementById('length');
        const reqNumber = document.getElementById('number');
        const reqUpper = document.getElementById('upper');

        passwordInput.addEventListener('focus', () => { pswdChecker.classList.add('active'); });
        passwordInput.addEventListener('blur', () => { if (passwordInput.value === "") pswdChecker.classList.remove('active'); });

        passwordInput.addEventListener('input', () => {
            const val = passwordInput.value;
            if (val.length >= 8) { reqLength.classList.add('valid'); reqLength.querySelector('span').innerText = '✔'; } 
            else { reqLength.classList.remove('valid'); reqLength.querySelector('span').innerText = '⬤'; }
            
            if (/\d/.test(val)) { reqNumber.classList.add('valid'); reqNumber.querySelector('span').innerText = '✔'; } 
            else { reqNumber.classList.remove('valid'); reqNumber.querySelector('span').innerText = '⬤'; }
            
            if (/[A-Z]/.test(val)) { reqUpper.classList.add('valid'); reqUpper.querySelector('span').innerText = '✔'; } 
            else { reqUpper.classList.remove('valid'); reqUpper.querySelector('span').innerText = '⬤'; }
        });
    }

    // ============================================
    // 4. VERIFICACIÓN DE USUARIO EN TIEMPO REAL
    // ============================================
    const usernameInput = document.getElementById('username');
    const usernameStatus = document.getElementById('username-status');
    
    if (usernameInput && usernameStatus) {
        const statusIcon = usernameStatus.querySelector('.status-icon');
        const statusText = usernameStatus.querySelector('.status-text');
        let typingTimer;

        usernameInput.addEventListener('focus', () => {
            usernameStatus.classList.add('active');
            if (usernameInput.value.trim() === '') setTooltipState('default', 'Escribe un usuario...', '✍️');
        });

        usernameInput.addEventListener('blur', () => {
            if (usernameInput.value.trim() === '') usernameStatus.classList.remove('active');
        });

        usernameInput.addEventListener('input', () => {
            clearTimeout(typingTimer);
            const val = usernameInput.value.trim();

            if (val === '') { setTooltipState('default', 'Escribe un usuario...', '✍️'); return; }
            if (val.length < 3) { setTooltipState('taken', 'Mínimo 3 letras', '❌'); return; }

            setTooltipState('checking', 'Comprobando...', '⏳');

            typingTimer = setTimeout(() => {
                fetch(`/accounts/api/check-username/?username=${val}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.is_taken) {
                            setTooltipState('taken', 'Usuario no disponible', '✖');
                        } else {
                            setTooltipState('available', 'Usuario disponible', '✔');
                        }
                    })
                    .catch(() => setTooltipState('default', 'Error de red', '⚠️'));
            }, 600);
        });

        function setTooltipState(stateClass, text, icon) {
            usernameStatus.className = `username-tooltip active ${stateClass}`;
            statusText.textContent = text;
            statusIcon.textContent = icon;
        }
    }

    // ============================================
    // 5. MODAL DE VERIFICACIÓN (CONECTADO A DJANGO)
    // ============================================
    const stepVerification = document.getElementById('step-verification');
    const stepSuccess = document.getElementById('step-success');
    const btnVerifyCode = document.getElementById('btn-verify-code');
    const codeBoxes = document.querySelectorAll('.code-box');
    const codeInputsContainer = document.getElementById('code-inputs-container');
    const codeErrorMsg = document.getElementById('code-error-msg');

    if (codeBoxes.length > 0) {
        codeBoxes.forEach((box, index) => {
            box.addEventListener('input', function() {
                codeErrorMsg.style.display = 'none';
                codeBoxes.forEach(b => b.classList.remove('error'));

                if (this.value.length === 1 && index < codeBoxes.length - 1) {
                    codeBoxes[index + 1].disabled = false;
                    codeBoxes[index + 1].focus();
                }
            });
            box.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && this.value === '' && index > 0) {
                    codeBoxes[index - 1].focus();
                    codeBoxes[index].disabled = true;
                }
            });
        });
    }

    if (btnVerifyCode && stepVerification && stepSuccess) {
        btnVerifyCode.addEventListener('click', function() {
            let codigoIngresado = '';
            codeBoxes.forEach(box => codigoIngresado += box.value);

            if (codigoIngresado.length < 6) {
                triggerCodeError('Debes ingresar los 6 dígitos');
                return;
            }

            btnVerifyCode.classList.add('btn-loading');

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            // USAMOS EL INPUT OCULTO SEGURO
            const emailValue = document.getElementById('hidden-verification-email').value;

            fetch('/accounts/api/verify-code/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ 
                    code: codigoIngresado,
                    email: emailValue
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    btnVerifyCode.classList.remove('btn-loading');
                    stepVerification.style.display = 'none';
                    stepSuccess.style.display = 'block';
                } else {
                    triggerCodeError(data.error || 'Código incorrecto, ingrese el código de nuevo');
                }
            })
            .catch(() => triggerCodeError('Error de conexión con el servidor'));
        });
    }

    function triggerCodeError(mensaje) {
        btnVerifyCode.classList.remove('btn-loading');

        codeErrorMsg.textContent = mensaje;
        codeErrorMsg.style.display = 'block';
        
        codeInputsContainer.classList.add('shake');
        codeBoxes.forEach(box => {
            box.classList.add('error');
            box.value = '';
            box.disabled = true;
        });
        
        codeBoxes[0].disabled = false;
        codeBoxes[0].focus();

        setTimeout(() => { codeInputsContainer.classList.remove('shake'); }, 400);
    }

    // ============================================
    // 6. LÓGICA DE REENVIAR CÓDIGO (COOLDOWN 60s)
    // ============================================
    const resendLink = document.getElementById('resend-code');
    const resendTimer = document.getElementById('resend-timer');
    let isCooldown = false;

    if (resendLink && resendTimer) {
        resendLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (isCooldown) return;

            isCooldown = true;
            resendLink.style.display = 'none';
            resendTimer.style.display = 'inline';
            let timeLeft = 60;
            resendTimer.textContent = `(Espera ${timeLeft}s)`;

            const timerInterval = setInterval(() => {
                timeLeft--;
                resendTimer.textContent = `(Espera ${timeLeft}s)`;
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    isCooldown = false;
                    resendLink.style.display = 'inline';
                    resendTimer.style.display = 'none';
                }
            }, 1000);

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            // USAMOS EL INPUT OCULTO SEGURO
            const emailValue = document.getElementById('hidden-verification-email').value;

            fetch('/accounts/api/resend-code/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ email: emailValue })
            });
        });
    }
});