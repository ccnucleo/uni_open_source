(function () {
    const STORAGE_KEY = "uos-sidebar-collapsed";

    function applySidebarState(isCollapsed) {
        document.body.classList.toggle("sidebar-collapsed", isCollapsed);

        const toggleButton = document.getElementById("sidebar-toggle-btn");
        if (toggleButton) {
            toggleButton.setAttribute("aria-expanded", String(!isCollapsed));
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        const toggleButton = document.getElementById("sidebar-toggle-btn");
        if (!toggleButton) {
            return;
        }

        const savedState = localStorage.getItem(STORAGE_KEY) === "true";
        applySidebarState(savedState);

        toggleButton.addEventListener("click", function () {
            const isCurrentlyCollapsed = document.body.classList.contains("sidebar-collapsed");
            const nextState = !isCurrentlyCollapsed;
            applySidebarState(nextState);
            localStorage.setItem(STORAGE_KEY, String(nextState));
        });
    });
})();
