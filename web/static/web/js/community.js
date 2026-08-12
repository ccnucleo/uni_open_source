document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // BÚSQUEDA Y FILTRADO SERVIDOR (DEBOUNCE)
    // ==========================================
    const filterForm = document.querySelector('.community-filter-form');
    const searchDevInput = document.getElementById('search-dev');
    const searchTechInput = document.getElementById('search-tech');
    let debounceTimer = null;

    function triggerServerFilter() {
        if (!filterForm) return;
        // Al realizar una nueva búsqueda/filtrado, reseteamos a la página 1
        let pageInput = filterForm.querySelector('input[name="page"]');
        if (pageInput) {
            pageInput.value = '1';
        }
        filterForm.submit();
    }

    function handleDebouncedInput() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            triggerServerFilter();
        }, 700); // 550ms debounce para evitar sobrecarga de peticiones al servidor
    }

    if (searchDevInput) {
        searchDevInput.addEventListener('input', handleDebouncedInput);
    }

    if (searchTechInput) {
        searchTechInput.addEventListener('input', handleDebouncedInput);
    }

    // ==========================================
    // DESPLAZAMIENTO SUAVE EN PAGINACIÓN
    // ==========================================
    const paginationControls = document.getElementById('pagination-controls');
    if (paginationControls) {
        const pageButtons = paginationControls.querySelectorAll('.btn-page:not(.disabled)');
        pageButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                const mainArea = document.querySelector('.community-main') || document.querySelector('.community-grid');
                if (mainArea) {
                    mainArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // ==========================================
    // MANEJO DE FALLBACK EN AVATARES DE DESARROLLADORES
    // ==========================================
    const devAvatars = document.querySelectorAll('.dev-avatar');
    devAvatars.forEach(img => {
        img.addEventListener('error', function () {
            if (this.tagName === 'IMG') {
                this.src = '/static/web/img/avatar.jpg';
            }
        });
    });

    // ==========================================
    // TABS DEL PERFIL PÚBLICO
    // ==========================================
    const btnDesc = document.getElementById('btn-desc');
    const btnProy = document.getElementById('btn-proy');
    const viewGeneral = document.getElementById('view-general');
    const viewProjects = document.getElementById('view-all-projects');

    if (btnDesc && btnProy) {
        btnDesc.addEventListener('click', function () {
            btnDesc.classList.add('active');
            btnProy.classList.remove('active');
            if (viewGeneral) viewGeneral.style.display = 'block';
            if (viewProjects) viewProjects.style.display = 'none';
        });

        btnProy.addEventListener('click', function () {
            btnProy.classList.add('active');
            btnDesc.classList.remove('active');
            if (viewGeneral) viewGeneral.style.display = 'none';
            if (viewProjects) viewProjects.style.display = 'block';
        });
    }

    function getCSRFToken() {
        const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (tokenInput) return tokenInput.value;
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === ('csrftoken=')) {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.padding = '15px 25px';
        toast.style.background = type === 'success' ? '#22c55e' : '#ef4444';
        toast.style.color = 'white';
        toast.style.borderRadius = '8px';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        toast.style.zIndex = '99999';
        toast.style.transition = 'opacity 0.3s ease';
        toast.style.fontWeight = '600';
        toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i> ${message}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // TOGGLE SEGUIMIENTO
    const btnToggleFollow = document.getElementById('btn-toggle-follow');
    const statFollowers = document.getElementById('stat-followers');

    if (btnToggleFollow) {
        btnToggleFollow.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            fetch(`/comunidad/api/follow/${userId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.is_following) {
                        btnToggleFollow.className = 'btn btn-dark';
                        btnToggleFollow.innerHTML = '<i class="fas fa-check"></i> Siguiendo';
                        showToast('Ahora sigues a este desarrollador.');
                    } else {
                        btnToggleFollow.className = 'btn btn-orange';
                        btnToggleFollow.innerHTML = '<i class="fas fa-user-plus"></i> Seguir';
                        showToast('Has dejado de seguir a este desarrollador.');
                    }
                    if (statFollowers) statFollowers.textContent = data.followers_count;
                } else {
                    showToast(data.message || 'Error al actualizar seguimiento.', 'error');
                }
            })
            .catch(() => showToast('Error de conexión.', 'error'));
        });
    }

    // MODAL MENSAJE DIRECTO
    const btnOpenMessageModal = document.getElementById('btn-open-message-modal');
    const modalSendMessage = document.getElementById('modal-send-message');
    const btnCloseMessageModal = document.getElementById('btn-close-message-modal');
    const btnCancelMessageModal = document.getElementById('btn-cancel-message-modal');
    const formSendMessage = document.getElementById('form-send-message');

    if (btnOpenMessageModal && modalSendMessage) {
        btnOpenMessageModal.addEventListener('click', function () {
            modalSendMessage.style.display = 'flex';
        });
    }

    function closeMessageModal() {
        if (modalSendMessage) modalSendMessage.style.display = 'none';
    }

    if (btnCloseMessageModal) btnCloseMessageModal.addEventListener('click', closeMessageModal);
    if (btnCancelMessageModal) btnCancelMessageModal.addEventListener('click', closeMessageModal);

    if (formSendMessage) {
        formSendMessage.addEventListener('submit', function (e) {
            e.preventDefault();
            const userId = formSendMessage.getAttribute('data-user-id');
            const formData = new FormData(formSendMessage);

            fetch(`/comunidad/api/message/${userId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast(data.message || 'Mensaje enviado correctamente.');
                    closeMessageModal();
                    formSendMessage.reset();
                } else {
                    showToast(data.message || 'Error al enviar el mensaje.', 'error');
                }
            })
            .catch(() => showToast('Error de servidor.', 'error'));
        });
    }
});