document.addEventListener('DOMContentLoaded', function() {
    
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
            viewGeneral.style.display = 'block';
            viewProjects.style.display = 'none';
        });

        btnProy.addEventListener('click', function () {
            btnProy.classList.add('active');
            btnDesc.classList.remove('active');
            viewGeneral.style.display = 'none';
            viewProjects.style.display = 'block';
        });
    }

    // ==========================================
    // LÓGICA DE FILTRADO Y PAGINACIÓN
    // ==========================================
    const searchInput = document.getElementById('search-dev');
    const techInput = document.getElementById('search-tech');
    const cards = Array.from(document.querySelectorAll('.dev-card')); // Convertido a Array
    const noResultsMsg = document.getElementById('no-results-msg');
    
    // Elementos de Paginación
    const selectPerPage = document.getElementById('per-page');
    const resultsCount = document.getElementById('results-count');
    const paginationControls = document.getElementById('pagination-controls');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const pageInfo = document.getElementById('page-info');

    // Variables de estado
    let filteredCards = [];
    let currentPage = 1;
    let itemsPerPage = 6;

    // Función 1: Filtrar la lista
    function filterDevelopers() {
        if (!searchInput || !techInput) return;

        const searchTerm = searchInput.value.toLowerCase().trim();
        const techTerm = techInput.value.toLowerCase().trim();
        
        filteredCards = []; // Reiniciamos los resultados

        cards.forEach(card => {
            const username = card.dataset.username || '';
            const name = card.dataset.name || '';
            const userTechs = card.dataset.techs || '';

            const matchesText = searchTerm === '' || username.includes(searchTerm) || name.includes(searchTerm);
            const matchesTech = techTerm === '' || userTechs.includes(techTerm);

            if (matchesText && matchesTech) {
                filteredCards.push(card);
            } else {
                card.style.display = 'none'; // Ocultamos los que no coinciden de inmediato
            }
        });

        // Al hacer una nueva búsqueda, volvemos a la página 1
        currentPage = 1;
        applyPagination();
    }

    // Función 2: Aplicar Paginación sobre los resultados filtrados
    function applyPagination() {
        const totalItems = filteredCards.length;

        // Caso: Sin resultados
        if (totalItems === 0) {
            noResultsMsg.style.display = 'block';
            paginationControls.style.display = 'none';
            resultsCount.textContent = 'Mostrando 0 resultados';
            return;
        }

        // Hay resultados
        noResultsMsg.style.display = 'none';
        
        // Determinar cuántos por página
        const perPageValue = selectPerPage.value;
        itemsPerPage = perPageValue === 'all' ? totalItems : parseInt(perPageValue);

        const totalPages = Math.ceil(totalItems / itemsPerPage);
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;

        // Mostrar solo los del rango actual
        filteredCards.forEach((card, index) => {
            if (index >= startIndex && index < endIndex) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });

        // Actualizar textos UI
        resultsCount.textContent = `Mostrando ${totalItems} talento(s)`;
        pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;

        // Mostrar/Ocultar controles de paginación inferiores
        if (totalPages > 1) {
            paginationControls.style.display = 'flex';
            btnPrev.disabled = currentPage === 1;
            btnNext.disabled = currentPage === totalPages;
        } else {
            paginationControls.style.display = 'none';
        }
    }

    // ==========================================
    // LISTENERS DE EVENTOS
    // ==========================================
    if (searchInput) {
        // Al escribir en los buscadores
        searchInput.addEventListener('input', filterDevelopers);
        techInput.addEventListener('input', filterDevelopers);

        // Al cambiar la cantidad por página
        selectPerPage.addEventListener('change', function() {
            currentPage = 1; // Volver a pag 1
            applyPagination();
        });

        // Botón Anterior
        btnPrev.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                applyPagination();
            }
        });

        // Botón Siguiente
        btnNext.addEventListener('click', function() {
            const totalPages = Math.ceil(filteredCards.length / itemsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                applyPagination();
            }
        });

        // Ejecutar por primera vez al cargar la página
        filterDevelopers();
    }
});