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
});