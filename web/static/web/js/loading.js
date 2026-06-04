/**
 * UNI Open Source - Global Form Loading Interceptor
 * Intercepts form submissions to show immediate visual feedback on buttons
 * and prevent duplicate requests / database corruption.
 */
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('submit', function(event) {
        const form = event.target;
        
        // Skip if submission was already prevented or if the form is marked to ignore loading state
        if (event.defaultPrevented || form.classList.contains('no-loading')) {
            return;
        }

        // Validate standard browser validation first
        if (typeof form.checkValidity === 'function' && !form.checkValidity()) {
            return;
        }

        // Find all submit buttons in the form
        const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"], .btn-submit');
        
        submitButtons.forEach(button => {
            // Avoid double application
            if (button.classList.contains('btn-loading') || button.classList.contains('no-loading')) {
                return;
            }

            // Apply loading class (this handles visual state: spinner, opacity, pointer-events)
            button.classList.add('btn-loading');

            // Prevent double-clicking via pointer-events (CSS does this too, but JS is extra safety)
            button.style.pointerEvents = 'none';

            // Disable the button to prevent keyboard re-submission (e.g. hitting Enter again)
            // We use setTimeout to allow the browser's submit process to register the button values
            // before it becomes disabled (disabling a button synchronously during submit can sometimes
            // prevent its name/value from being sent in the POST request).
            setTimeout(() => {
                button.disabled = true;
            }, 10);
        });
    }, { passive: true });
});
