// ============================================
// SISTEMA DE TEMAS — UNI OPEN SOURCE
// ============================================

(function () {
    const THEMES = [
        { id: 'light',  label: 'Light',  icon: '☀️',  dot: 'theme-dot-light'  },
        { id: 'dark',   label: 'Dark',   icon: '🌙',  dot: 'theme-dot-dark'   },
        { id: 'ocean',  label: 'Ocean',  icon: '🌊',  dot: 'theme-dot-ocean'  },
        { id: 'forest', label: 'Forest', icon: '🌿',  dot: 'theme-dot-forest' },
    ];

    // Aplicar tema al body
    function applyTheme(themeId) {
        // Quitar todas las clases de tema
        document.body.classList.remove('theme-light', 'theme-dark', 'theme-ocean', 'theme-forest');
        // Aplicar la nueva clase de tema
        document.body.classList.add('theme-' + themeId);
        // Guardar en localStorage
        localStorage.setItem('theme', themeId);
        // Actualizar estado activo en el dropdown
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === themeId);
        });
        // Actualizar ícono del botón
        const current = THEMES.find(t => t.id === themeId) || THEMES[0];
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) themeBtn.innerHTML = current.icon;
    }

    // Inicializar al cargar
    document.addEventListener('DOMContentLoaded', function () {
        const saved = localStorage.getItem('theme') || 'light';
        applyTheme(saved);

        const dropdown = document.getElementById('theme-dropdown');
        const themeBtn = document.getElementById('theme-toggle-btn');

        if (!themeBtn || !dropdown) return;

        // Abrir/cerrar dropdown
        themeBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Cerrar al hacer click fuera
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.theme-selector')) {
                dropdown.classList.remove('open');
            }
        });

        // Cerrar con Escape
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') dropdown.classList.remove('open');
        });

        // Click en cada opción
        document.querySelectorAll('.theme-option').forEach(btn => {
            btn.addEventListener('click', function () {
                applyTheme(this.dataset.theme);
                dropdown.classList.remove('open');
            });
        });
    });

    // Aplicar tema inmediatamente (antes del DOMContentLoaded)
    // para evitar el flash de tema incorrecto
    const savedEarly = localStorage.getItem('theme');
    if (savedEarly) {
        document.documentElement.classList.add('theme-' + savedEarly + '-early');
        document.addEventListener('DOMContentLoaded', function () {
            document.documentElement.classList.remove('theme-' + savedEarly + '-early');
        });
    }
})();
