document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.auth-toggle-pw').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var wrap = btn.closest('.auth-input-wrap');
            var input = wrap ? wrap.querySelector('input') : null;
            if (!input) return;
            var icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                if (icon) {
                    icon.classList.replace('fa-eye', 'fa-eye-slash');
                }
            } else {
                input.type = 'password';
                if (icon) {
                    icon.classList.replace('fa-eye-slash', 'fa-eye');
                }
            }
        });
    });
});
