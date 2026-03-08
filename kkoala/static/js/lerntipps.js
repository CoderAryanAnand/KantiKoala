document.addEventListener('DOMContentLoaded', () => {
    // Add click event listeners to all accordion toggle buttons
    document.querySelectorAll('.accordion-toggle').forEach(button => {
        button.addEventListener('click', () => {
            // Get the content panel and the chevron icon inside the button
            const content = button.nextElementSibling;
            // Find the chevron icon (prefer class based selection, fallback to first svg for compatibility)
            const icon = button.querySelector('.accordion-chevron') || button.querySelector('svg');

            if (!icon) return; // Guard clause

            // Toggle visibility of the accordion content
            content.classList.toggle('hidden');

            // Rotate the chevron icon based on the content's visibility
            if (content.classList.contains('hidden')) {
                icon.classList.remove('active');
                icon.style.transform = 'rotate(0deg)';
                button.setAttribute('aria-expanded', 'false');
            } else {
                icon.classList.add('active');
                icon.style.transform = 'rotate(180deg)';
                button.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // --- Scroll to Top Button Logic ---
    const scrollTopBtn = document.getElementById('scrollTopBtn');

    if (scrollTopBtn) {
        // Show or hide the scroll-to-top button based on scroll position
        window.onscroll = function() {
            if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
                scrollTopBtn.classList.remove('hidden');
            } else {
                scrollTopBtn.classList.add('hidden');
            }
        };

        // Smoothly scroll to the top when the button is clicked
        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});