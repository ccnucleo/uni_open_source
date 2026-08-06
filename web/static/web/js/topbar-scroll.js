(function () {
    function updateTopbarScroll() {
        const topbar = document.querySelector('.topbar');
        if (!topbar) return;

        // Verificar si la página actual tiene un hero-banner
        const hasHero = document.querySelector('.hero-banner');
        if (!hasHero) {
            topbar.classList.remove('topbar-transparent');
            return;
        }

        if (window.scrollY <= 10) {
            topbar.classList.add('topbar-transparent');
        } else {
            topbar.classList.remove('topbar-transparent');
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        updateTopbarScroll();
        window.addEventListener('scroll', updateTopbarScroll, { passive: true });
    });
})();
