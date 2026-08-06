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
});