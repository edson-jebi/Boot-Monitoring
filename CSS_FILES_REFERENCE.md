# CSS Files Reference - Brand-Specific Stylesheets

## Overview

The Boot Monitoring system uses brand-specific CSS files to ensure complete visual customization for each brand (Bradken and Jebi). Each brand has its own set of CSS files that are automatically loaded based on the `APP_BRAND` configuration.

---

## CSS File Structure

### Bradken Brand Files

| File | Path | Purpose |
|------|------|---------|
| **core.css** | `/static/core.css` | Base Bootstrap framework styles and structure |
| **color.css** | `/static/color.css` | Bradken color overrides and brand-specific colors |
| **theme-bradken.css** | `/static/css/theme-bradken.css` | Additional Bradken theme enhancements |

### Jebi Brand Files

| File | Path | Purpose |
|------|------|---------|
| **core_jebi.css** | `/static/core_jebi.css` | Base Bootstrap framework styles (Jebi variant) |
| **color_jebi.css** | `/static/color_jebi.css` | Jebi color overrides and brand-specific colors |
| **theme-jebi.css** | `/static/css/theme-jebi.css` | Additional Jebi theme enhancements |

---

## How CSS Files are Loaded

### Static Loading (Server-Side)

When the page initially loads, the correct CSS files are included based on the `APP_BRAND` configuration in [templates/base.html](templates/base.html):

```jinja2
<!-- For BRADKEN -->
<link id="core-css" rel="stylesheet" href="/static/core.css">
<link id="color-css" rel="stylesheet" href="/static/color.css">

<!-- For JEBI -->
<link id="core-css" rel="stylesheet" href="/static/core_jebi.css">
<link id="color-css" rel="stylesheet" href="/static/color_jebi.css">
```

### Dynamic Loading (Client-Side)

The Theme Manager can dynamically switch CSS files without page reload using JavaScript:

```javascript
// Theme Manager automatically loads correct CSS files
window.themeManager.switchTheme('JEBI');
// Loads: core_jebi.css + color_jebi.css + theme-jebi.css

window.themeManager.switchTheme('BRADKEN');
// Loads: core.css + color.css + theme-bradken.css
```

---

## CSS Loading Order

The CSS files are loaded in this specific order to ensure proper cascading:

1. **Core CSS** (`core.css` or `core_jebi.css`)
   - Base Bootstrap framework
   - Layout and grid system
   - Typography fundamentals
   - Component structures

2. **Color CSS** (`color.css` or `color_jebi.css`)
   - Brand-specific color overrides
   - Primary/secondary colors
   - Background colors
   - Text colors

3. **Theme CSS** (`theme-bradken.css` or `theme-jebi.css`)
   - Advanced theme features
   - CSS variables
   - Animations and transitions
   - Additional visual enhancements

---

## File Size Comparison

| Brand | Core CSS | Color CSS | Theme CSS | Total |
|-------|----------|-----------|-----------|-------|
| **Bradken** | 204 KB | 1.5 KB | 7.2 KB | ~212 KB |
| **Jebi** | 204 KB | 1.5 KB | 10.1 KB | ~215 KB |

**Note**: Core CSS files are identical in size but contain brand-specific customizations.

---

## Configuration

### Setting the Brand

The `APP_BRAND` configuration determines which CSS files are loaded:

**.env file:**
```bash
# For Bradken
APP_BRAND=BRADKEN

# For Jebi
APP_BRAND=JEBI
```

**config.py:**
```python
APP_BRAND: str = os.environ.get('APP_BRAND') or "BRADKEN"
```

---

## CSS File Contents

### core.css vs core_jebi.css

Both files contain the Bootstrap framework, but with brand-specific modifications:

**Bradken (core.css):**
- Standard Bootstrap components
- Professional layout spacing
- Conservative font sizes

**Jebi (core_jebi.css):**
- Modified Bootstrap components
- Modern layout spacing
- Slightly larger font sizes
- Additional modern UI components

### color.css vs color_jebi.css

**Bradken (color.css):**
```css
body {
    background-color: #005596; /* Navy Blue */
}

.colorside {
    background-color: #005596 !important;
}

.text-title {
    color: #F3CB3C !important; /* Gold */
}
```

**Jebi (color_jebi.css):**
```css
body {
    background-color: #00A8A8; /* Teal */
}

.colorside {
    background-color: #00A8A8 !important;
}

.text-title {
    color: #FF6B6B !important; /* Coral */
}
```

### theme-bradken.css vs theme-jebi.css

**Bradken Features:**
- CSS variables for navy blue theme
- Professional animations (0.3s ease)
- 8px border radius
- Subtle shadows
- Gradient: Navy → Dark Navy

**Jebi Features:**
- CSS variables for teal theme
- Dynamic animations (0.3s cubic-bezier)
- 12px border radius (more rounded)
- Pronounced shadows with glow
- Gradient: Teal → Light Teal
- Ripple effects on status indicators

---

## Switching Brands

### Method 1: Environment Variable (Production)

```bash
# Edit .env file
nano /home/pi/Boot-Monitoring/.env

# Change brand
APP_BRAND=JEBI

# Restart service
sudo systemctl restart boot-monitoring
```

**Result:**
- Server loads: `core_jebi.css` + `color_jebi.css`
- Client loads: `theme-jebi.css`
- Logo changes to: `logo_jebi.png`

### Method 2: Development Mode

```bash
export APP_BRAND=JEBI
python web.py
```

### Method 3: Dynamic Browser Switch (Temporary)

```javascript
// In browser console
window.themeManager.switchTheme('JEBI');
```

**Result:**
- Dynamically swaps: `core.css` → `core_jebi.css`
- Dynamically swaps: `color.css` → `color_jebi.css`
- Loads: `theme-jebi.css`
- Updates logo
- No page reload required!

---

## Verification

### Check Loaded CSS Files

**Browser Console:**
```javascript
// Check core CSS
console.log(document.getElementById('core-css').href);
// Should show: /static/core_jebi.css (for Jebi)

// Check color CSS
console.log(document.getElementById('color-css').href);
// Should show: /static/color_jebi.css (for Jebi)

// Check theme CSS
console.log(document.getElementById('theme-css').href);
// Should show: /static/css/theme-jebi.css (for Jebi)
```

**Browser DevTools Network Tab:**
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by CSS
4. Refresh page
5. Verify correct files are loaded

---

## Customization

### Creating Custom CSS for a Brand

1. **Copy existing files:**
```bash
cd /home/pi/Boot-Monitoring/static
cp core.css core_mybrand.css
cp color.css color_mybrand.css
cp css/theme-bradken.css css/theme-mybrand.css
```

2. **Edit the files with your brand colors:**
```bash
nano core_mybrand.css
nano color_mybrand.css
nano css/theme-mybrand.css
```

3. **Update theme-manager.js:**
```javascript
'MYBRAND': {
    name: 'My Brand',
    css: '/static/css/theme-mybrand.css',
    coreCSS: '/static/core_mybrand.css',
    colorCSS: '/static/color_mybrand.css',
    colors: {
        primary: '#FF0000',
        secondary: '#00FF00',
        accent: '#0000FF'
    },
    logo: '/static/mybrand_logo.png'
}
```

4. **Set environment variable:**
```bash
APP_BRAND=MYBRAND
```

---

## Troubleshooting

### CSS Not Loading

**Problem:** CSS files return 404 error

**Solution:**
```bash
# Verify files exist
ls -la /home/pi/Boot-Monitoring/static/*.css
ls -la /home/pi/Boot-Monitoring/static/css/*.css

# Check permissions
chmod 644 /home/pi/Boot-Monitoring/static/*.css
chmod 644 /home/pi/Boot-Monitoring/static/css/*.css

# Restart service
sudo systemctl restart boot-monitoring
```

### Wrong CSS Files Loading

**Problem:** Jebi brand loads Bradken CSS

**Solutions:**
1. Clear browser cache (Ctrl + Shift + Delete)
2. Hard refresh (Ctrl + Shift + R)
3. Check .env file:
   ```bash
   cat /home/pi/Boot-Monitoring/.env | grep APP_BRAND
   ```
4. Verify config:
   ```bash
   python -c "from config import Config; print(f'Brand: {Config.APP_BRAND}')"
   ```

### CSS Changes Not Reflecting

**Problem:** Updated CSS but changes don't appear

**Solutions:**
1. Clear browser cache
2. Add version parameter (development):
   ```html
   <link rel="stylesheet" href="/static/core_jebi.css?v=2">
   ```
3. Check browser console for CSS errors
4. Verify CSS file was saved correctly

---

## Performance Considerations

### Caching

**Production:** CSS files are cached by browser (304 responses)
```
Cache-Control: public, max-age=31536000
```

**Development:** Disable caching for testing
```python
# In Flask config
SEND_FILE_MAX_AGE_DEFAULT = 0
```

### File Size Optimization

**Before deployment, consider:**
1. Minifying CSS files
2. Combining CSS files (if needed)
3. Using CDN for Google Fonts
4. Enabling gzip compression

```bash
# Minify CSS (example with clean-css)
npm install -g clean-css-cli
cleancss -o core_jebi.min.css core_jebi.css
```

---

## Best Practices

1. **Always test both brands** after making CSS changes
2. **Use CSS variables** for easy color customization
3. **Maintain consistent naming** between brand files
4. **Document custom changes** in CSS comments
5. **Version control** all CSS files
6. **Test responsive design** on mobile devices

---

## Quick Reference

| Action | Command/Code |
|--------|--------------|
| Check current brand | `console.log(document.body.dataset.brand)` |
| Check core CSS | `console.log(document.getElementById('core-css').href)` |
| Check color CSS | `console.log(document.getElementById('color-css').href)` |
| Switch to Jebi | `window.themeManager.switchTheme('JEBI')` |
| Switch to Bradken | `window.themeManager.switchTheme('BRADKEN')` |
| List CSS files | `ls -la /home/pi/Boot-Monitoring/static/*.css` |

---

## Related Documentation

- [UI_IMPROVEMENTS_GUIDE.md](UI_IMPROVEMENTS_GUIDE.md) - Complete UI enhancement guide
- [BRAND_COLORS_REFERENCE.md](BRAND_COLORS_REFERENCE.md) - Color specifications
- [QUICK_START_BRAND_SWITCHING.md](QUICK_START_BRAND_SWITCHING.md) - Quick start guide
- [templates/base.html](templates/base.html) - Template with CSS loading logic
- [static/js/theme-manager.js](static/js/theme-manager.js) - Theme management JavaScript

---

**Last Updated**: 2025-10-21
**Version**: 1.0