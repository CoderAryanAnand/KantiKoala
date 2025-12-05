document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const userThemeSetting = document.documentElement.getAttribute('data-theme-setting');

    // Applies the given theme by toggling the 'dark' class on the root element.
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    // Handles system theme changes if user setting is 'system'.
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    function handleSystemThemeChange(e) {
        if (document.documentElement.getAttribute('data-theme-setting') === 'system') {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    }

    // Sets the initial theme based on user setting or system preference.
    if (userThemeSetting === 'dark') {
        applyTheme('dark');
    } else if (userThemeSetting === 'light') {
        applyTheme('light');
    } else {
        // In 'system' mode, use localStorage if set, otherwise use OS preference.
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            applyTheme(savedTheme);
        } else {
            applyTheme(mediaQuery.matches ? 'dark' : 'light');
        }
        // Listen for OS theme changes only in system mode.
        mediaQuery.addEventListener('change', handleSystemThemeChange);
    }

    // Handles the theme toggle button (only in 'system' mode).
    if (themeToggle) {
        if (userThemeSetting !== 'system') {
            // Hide the toggle if a theme is forced.
            themeToggle.style.display = 'none';
        } else {
            themeToggle.addEventListener('click', () => {
                const isDark = document.documentElement.classList.toggle('dark');
                localStorage.setItem('theme', isDark ? 'dark' : 'light');
            });
        }
    }

    // Favicon handling — follows browser/system theme (tab bar), NOT website appearance
    const favicon = document.getElementById('favicon');
    if (favicon) {
        const originalSrc = favicon.getAttribute('data-original-src') || favicon.href;
        const prefersDarkSystem = window.matchMedia('(prefers-color-scheme: dark)');

        function setFaviconOriginal() {
            favicon.href = originalSrc;
        }

        function invertFavicon(src) {
            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.src = src;

            img.onload = () => {
                try {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);

                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;
                    for (let i = 0; i < data.length; i += 4) {
                        data[i] = 255 - data[i];       // Red
                        data[i + 1] = 255 - data[i + 1]; // Green
                        data[i + 2] = 255 - data[i + 2]; // Blue
                        // Alpha unchanged
                    }
                    ctx.putImageData(imageData, 0, 0);
                    favicon.href = canvas.toDataURL('image/png');
                } catch (e) {
                    // Canvas tainted or other error — fall back to original
                    favicon.href = originalSrc;
                }
            };

            img.onerror = () => {
                favicon.href = originalSrc;
            };
        }

        function updateFaviconForSystemTheme() {
            // Check browser/system preference (controls tab bar color)
            if (prefersDarkSystem.matches) {
                // System is dark → invert favicon so it's visible on dark tab bar
                invertFavicon(originalSrc);
            } else {
                // System is light → use original (dark) favicon
                setFaviconOriginal();
            }
        }

        // Initial update
        updateFaviconForSystemTheme();

        // Listen for system theme changes (e.g., user switches Windows/macOS theme)
        prefersDarkSystem.addEventListener('change', updateFaviconForSystemTheme);
    }
});