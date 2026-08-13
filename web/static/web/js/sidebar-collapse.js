(function () {
    const STORAGE_KEY = "uos-sidebar-collapsed";

    function isMobile() {
        return window.innerWidth <= 768;
    }

    function applySidebarState(isCollapsed) {
        if (!isMobile()) {
            document.body.classList.toggle("sidebar-collapsed", isCollapsed);
        }
        const toggleButton = document.getElementById("sidebar-toggle-btn");
        if (toggleButton) {
            toggleButton.setAttribute("aria-expanded", String(!isCollapsed));
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        const toggleButton = document.getElementById("sidebar-toggle-btn");
        const backdrop = document.getElementById("sidebar-mobile-backdrop");
        const sidebarNav = document.getElementById("sidebar-nav");

        if (!toggleButton) {
            return;
        }

        const savedState = localStorage.getItem(STORAGE_KEY) === "true";
        applySidebarState(savedState);

        function closeMobileSidebar() {
            document.body.classList.remove("mobile-sidebar-open");
        }

        toggleButton.addEventListener("click", function (e) {
            e.stopPropagation();
            if (isMobile()) {
                document.body.classList.toggle("mobile-sidebar-open");
            } else {
                const isCurrentlyCollapsed = document.body.classList.contains("sidebar-collapsed");
                const nextState = !isCurrentlyCollapsed;
                applySidebarState(nextState);
                localStorage.setItem(STORAGE_KEY, String(nextState));
            }
        });

        if (backdrop) {
            backdrop.addEventListener("click", closeMobileSidebar);
        }

        if (sidebarNav) {
            sidebarNav.querySelectorAll("a").forEach(link => {
                link.addEventListener("click", () => {
                    if (isMobile()) {
                        closeMobileSidebar();
                    }
                });
            });
        }

        window.addEventListener("resize", function () {
            if (!isMobile()) {
                document.body.classList.remove("mobile-sidebar-open");
                const isCollapsed = localStorage.getItem(STORAGE_KEY) === "true";
                document.body.classList.toggle("sidebar-collapsed", isCollapsed);
            } else {
                document.body.classList.remove("sidebar-collapsed");
            }
        });
    });
})();

