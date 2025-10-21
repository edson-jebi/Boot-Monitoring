/**
 * Theme Manager
 * Handles dynamic brand theme loading based on configuration
 */

class ThemeManager {
    constructor() {
        this.themes = {
            'BRADKEN': {
                name: 'Bradken',
                css: '/static/css/theme-bradken.css',
                coreCSS: '/static/core.css',
                colorCSS: '/static/color.css',
                colors: {
                    primary: '#005596',
                    secondary: '#F3CB3C',
                    accent: '#003d6b'
                },
                logo: '/static/bradken_log.png'
            },
            'JEBI': {
                name: 'Jebi',
                css: '/static/css/theme-jebi.css',
                coreCSS: '/static/core_jebi.css',
                colorCSS: '/static/color_jebi.css',
                colors: {
                    primary: '#5f0f07ff',
                    secondary: '#FF6B6B',
                    accent: '#8b2a00ff'
                },
                logo: '/static/logo_jebi.png'
            }
        };

        this.currentTheme = null;
    }

    /**
     * Initialize theme based on configuration
     * @param {string} brandName - Brand name from config (BRADKEN or JEBI)
     */
    init(brandName = 'BRADKEN') {
        const brand = brandName.toUpperCase();

        if (!this.themes[brand]) {
            console.warn(`Unknown brand: ${brand}, defaulting to BRADKEN`);
            this.loadTheme('BRADKEN');
            return;
        }

        this.loadTheme(brand);
    }

    /**
     * Load theme CSS dynamically
     * @param {string} brandKey - Brand key (BRADKEN or JEBI)
     */
    loadTheme(brandKey) {
        const theme = this.themes[brandKey];

        if (!theme) {
            console.error(`Theme not found: ${brandKey}`);
            return;
        }

        // Update core.css
        const coreCSS = document.getElementById('core-css') ||
                        document.querySelector('link[href*="core.css"], link[href*="core_jebi.css"]');
        if (coreCSS && theme.coreCSS) {
            coreCSS.href = theme.coreCSS;
            if (!coreCSS.id) coreCSS.id = 'core-css';
            console.log(`Core CSS updated to: ${theme.coreCSS}`);
        }

        // Update color.css
        const colorCSS = document.getElementById('color-css') ||
                         document.querySelector('link[href*="color.css"], link[href*="color_jebi.css"]');
        if (colorCSS && theme.colorCSS) {
            colorCSS.href = theme.colorCSS;
            if (!colorCSS.id) colorCSS.id = 'color-css';
            console.log(`Color CSS updated to: ${theme.colorCSS}`);
        }

        // Remove old theme link if exists
        const oldThemeLink = document.getElementById('theme-css');
        if (oldThemeLink) {
            oldThemeLink.remove();
        }

        // Create and append new theme link
        const themeLink = document.createElement('link');
        themeLink.id = 'theme-css';
        themeLink.rel = 'stylesheet';
        themeLink.href = theme.css;

        // Insert after color.css or at the end of head
        const colorCssElement = document.querySelector('link[href*="color"]');
        if (colorCssElement) {
            colorCssElement.parentNode.insertBefore(themeLink, colorCssElement.nextSibling);
        } else {
            document.head.appendChild(themeLink);
        }

        this.currentTheme = brandKey;

        // Store in localStorage for persistence
        localStorage.setItem('selectedTheme', brandKey);

        // Update logo if element exists
        this.updateLogo(theme.logo);

        // Dispatch theme loaded event
        window.dispatchEvent(new CustomEvent('themeLoaded', {
            detail: {
                brand: brandKey,
                theme: theme
            }
        }));

        console.log(`Theme loaded: ${theme.name}`);
        console.log(`  - Core CSS: ${theme.coreCSS}`);
        console.log(`  - Color CSS: ${theme.colorCSS}`);
        console.log(`  - Theme CSS: ${theme.css}`);
        console.log(`  - Logo: ${theme.logo}`);
    }

    /**
     * Update logo image
     * @param {string} logoPath - Path to logo image
     */
    updateLogo(logoPath) {
        // Find all logo images by various selectors
        const selectors = [
            'img[src*="logo"]',           // Images with "logo" in src
            'img.brand-logo',             // Images with brand-logo class
            'img.logo',                   // Images with logo class
            '.sidebar-brand img',         // Images in sidebar brand area
            '.navbar-brand img',          // Images in navbar brand area
            '[class*="logo"] img'         // Images inside elements with "logo" in class
        ];

        selectors.forEach(selector => {
            const logoElements = document.querySelectorAll(selector);
            logoElements.forEach(logo => {
                // Update the logo source
                logo.src = logoPath;

                // Also update srcset if present
                if (logo.srcset) {
                    logo.srcset = logoPath;
                }
            });
        });

        // Log for debugging
        console.log(`Logo updated to: ${logoPath}`);
    }

    /**
     * Get current theme colors
     * @returns {Object} Current theme colors
     */
    getColors() {
        if (!this.currentTheme) return null;
        return this.themes[this.currentTheme].colors;
    }

    /**
     * Switch theme dynamically
     * @param {string} brandKey - Brand key to switch to
     */
    switchTheme(brandKey) {
        this.loadTheme(brandKey);

        // Show notification if UI plugin available
        if (window.ui) {
            window.ui.showToast(
                `Theme switched to ${this.themes[brandKey].name}`,
                'info'
            );
        }
    }

    /**
     * Get available themes
     * @returns {Array} List of available theme names
     */
    getAvailableThemes() {
        return Object.keys(this.themes).map(key => ({
            key: key,
            name: this.themes[key].name
        }));
    }

    /**
     * Auto-detect theme from environment or config
     */
    autoDetect() {
        // Try to get from meta tag
        const metaTheme = document.querySelector('meta[name="app-brand"]');
        if (metaTheme) {
            const brand = metaTheme.content;
            this.init(brand);
            return;
        }

        // Try to get from localStorage
        const savedTheme = localStorage.getItem('selectedTheme');
        if (savedTheme && this.themes[savedTheme]) {
            this.loadTheme(savedTheme);
            return;
        }

        // Default to BRADKEN
        this.init('BRADKEN');
    }

    /**
     * Apply theme color to specific element
     * @param {HTMLElement} element - Element to apply color to
     * @param {string} colorType - Type of color (primary, secondary, accent)
     * @param {string} property - CSS property to set (backgroundColor, color, etc.)
     */
    applyColor(element, colorType = 'primary', property = 'backgroundColor') {
        const colors = this.getColors();
        if (colors && colors[colorType]) {
            element.style[property] = colors[colorType];
        }
    }

    /**
     * Create theme switcher UI (optional)
     * @param {string} containerId - ID of container element
     */
    createThemeSwitcher(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const switcher = document.createElement('div');
        switcher.className = 'theme-switcher';
        switcher.innerHTML = `
            <label for="theme-select">Theme:</label>
            <select id="theme-select" class="form-control form-control-sm">
                ${this.getAvailableThemes().map(theme =>
                    `<option value="${theme.key}" ${this.currentTheme === theme.key ? 'selected' : ''}>
                        ${theme.name}
                    </option>`
                ).join('')}
            </select>
        `;

        container.appendChild(switcher);

        // Add event listener
        const select = switcher.querySelector('#theme-select');
        select.addEventListener('change', (e) => {
            this.switchTheme(e.target.value);
        });
    }
}

// Initialize global theme manager instance
window.themeManager = new ThemeManager();

// Auto-detect and load theme when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Check for data attribute on body or html element
        const appBrand = document.body.dataset.brand ||
                        document.documentElement.dataset.brand ||
                        'BRADKEN';
        window.themeManager.init(appBrand);
    });
} else {
    const appBrand = document.body.dataset.brand ||
                    document.documentElement.dataset.brand ||
                    'BRADKEN';
    window.themeManager.init(appBrand);
}