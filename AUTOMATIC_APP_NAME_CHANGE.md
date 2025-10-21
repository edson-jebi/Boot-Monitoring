# Automatic APP_NAME Configuration

## Overview

The Boot Monitoring system automatically sets the `APP_NAME` to match the `APP_BRAND` value. This means when you change the brand, both the visual theme AND the application name change automatically.

---

## How It Works

### Configuration Logic

In [config.py](config.py:24-26):

```python
APP_BRAND: str = os.environ.get('APP_BRAND') or "BRADKEN"
# APP_NAME automatically matches APP_BRAND unless explicitly overridden
APP_NAME: str = os.environ.get('APP_NAME') or os.environ.get('APP_BRAND') or "BRADKEN"
```

**Priority Order:**
1. If `APP_NAME` is explicitly set in `.env` → Use that value
2. Else if `APP_BRAND` is set → Use `APP_BRAND` value for `APP_NAME`
3. Else → Default to "BRADKEN"

---

## What Changes Automatically

### When you set `APP_BRAND=JEBI`:

| Configuration | Value |
|---------------|-------|
| **APP_BRAND** | JEBI |
| **APP_NAME** | JEBI (automatic) |
| **Page Title** | JEBI |
| **Browser Tab** | JEBI |
| **Header Text** | JEBI |
| **Core CSS** | core_jebi.css |
| **Color CSS** | color_jebi.css |
| **Theme CSS** | theme-jebi.css |
| **Logo** | logo_jebi.png |
| **Colors** | Teal (#00A8A8) + Coral (#FF6B6B) |

### When you set `APP_BRAND=BRADKEN`:

| Configuration | Value |
|---------------|-------|
| **APP_BRAND** | BRADKEN |
| **APP_NAME** | BRADKEN (automatic) |
| **Page Title** | BRADKEN |
| **Browser Tab** | BRADKEN |
| **Header Text** | BRADKEN |
| **Core CSS** | core.css |
| **Color CSS** | color.css |
| **Theme CSS** | theme-bradken.css |
| **Logo** | bradken_log.png |
| **Colors** | Navy Blue (#005596) + Gold (#F3CB3C) |

---

## Usage Examples

### Example 1: Simple Brand Switch (Automatic Name)

**.env file:**
```bash
APP_BRAND=JEBI
# APP_NAME is NOT set, so it automatically becomes "JEBI"
```

**Result:**
- Application name: **JEBI**
- Page title: **JEBI**
- All Jebi branding applied

---

### Example 2: Custom Name Override

**.env file:**
```bash
APP_BRAND=JEBI
APP_NAME=My Company Name
```

**Result:**
- Application name: **My Company Name**
- Page title: **My Company Name**
- Visual theme: **Jebi** (Teal colors)
- Logo: **logo_jebi.png**

**Use Case:** You want Jebi's visual style but with your own company name.

---

### Example 3: Development Testing

```bash
# Terminal 1 - Test Bradken
export APP_BRAND=BRADKEN
python web.py
# APP_NAME will be "BRADKEN"

# Terminal 2 - Test Jebi
export APP_BRAND=JEBI
python web.py
# APP_NAME will be "JEBI"
```

---

## Where APP_NAME is Used

The `APP_NAME` configuration appears in:

### 1. Page Titles

**[templates/base.html](templates/base.html:7)**
```html
<title>{% block title %}{{ config.APP_NAME }}{% endblock %}</title>
```

**Result:** Browser tab shows the APP_NAME

### 2. Login Page

**[templates/login.html](templates/login.html)**
```html
<h1>{{ config.APP_NAME }}</h1>
```

**Result:** Login page header displays the APP_NAME

### 3. Page Headers

Various templates use:
```jinja2
<h2>{{ config.APP_NAME }} - Dashboard</h2>
```

### 4. Navigation

```jinja2
<div class="navbar-brand">{{ config.APP_NAME }}</div>
```

---

## Visual Examples

### Bradken Configuration

```bash
APP_BRAND=BRADKEN
# APP_NAME automatically = "BRADKEN"
```

**Browser Tab:**
```
[🌐] BRADKEN
```

**Login Page:**
```
╔════════════════════════╗
║                        ║
║      BRADKEN           ║  ← Navy Blue (#005596)
║                        ║
║  [bradken_log.png]     ║
║                        ║
║  Username: [_______]   ║
║  Password: [_______]   ║
║                        ║
║      [Login Button]    ║  ← Navy Blue
║                        ║
╚════════════════════════╝
```

---

### Jebi Configuration

```bash
APP_BRAND=JEBI
# APP_NAME automatically = "JEBI"
```

**Browser Tab:**
```
[🌐] JEBI
```

**Login Page:**
```
╔════════════════════════╗
║                        ║
║        JEBI            ║  ← Teal (#00A8A8)
║                        ║
║  [logo_jebi.png]       ║
║                        ║
║  Username: [_______]   ║
║  Password: [_______]   ║
║                        ║
║      [Login Button]    ║  ← Teal
║                        ║
╚════════════════════════╝
```

---

## Configuration Scenarios

### Scenario 1: Default Installation

**No .env file or configuration**

```python
# Defaults in config.py
APP_BRAND = "BRADKEN"
APP_NAME = "BRADKEN"
```

**Result:** Full Bradken branding

---

### Scenario 2: Switch to Jebi

**.env:**
```bash
APP_BRAND=JEBI
```

**Result:**
```python
APP_BRAND = "JEBI"
APP_NAME = "JEBI"  # Automatic!
```

---

### Scenario 3: Jebi Colors with Custom Name

**.env:**
```bash
APP_BRAND=JEBI
APP_NAME=Industrial Solutions Inc.
```

**Result:**
```python
APP_BRAND = "JEBI"  # Determines colors/theme
APP_NAME = "Industrial Solutions Inc."  # Displayed name
```

**Use Case:** White-label deployment with custom branding

---

### Scenario 4: Development Environment

```bash
# Development .env
APP_BRAND=JEBI
FLASK_ENV=development
DEBUG=true
```

**Result:**
- APP_NAME: **JEBI**
- Debug mode enabled
- Development database used

---

## Testing

### Verify APP_NAME Configuration

**Python Console:**
```bash
python -c "from config import Config; print(f'Brand: {Config.APP_BRAND}, Name: {Config.APP_NAME}')"
```

**Expected Output (JEBI):**
```
Brand: JEBI, Name: JEBI
```

**Expected Output (Custom):**
```
Brand: JEBI, Name: My Custom Name
```

---

### Browser Console Check

```javascript
// Check page title
console.log(document.title);
// Output: "JEBI" or "BRADKEN"

// Check data attributes
console.log(document.body.dataset.brand);
// Output: "JEBI" or "BRADKEN"
```

---

### Visual Verification

1. **Browser Tab:** Check the tab title
2. **Login Page:** Check the header text
3. **Dashboard:** Check page titles and headers
4. **About/Footer:** Check application name references

---

## Best Practices

### 1. Simple Deployments

**Recommended:**
```bash
# Just set the brand
APP_BRAND=JEBI
```

**Don't set APP_NAME** unless you need a custom name.

---

### 2. White-Label Deployments

**Recommended:**
```bash
# Set both for custom branding
APP_BRAND=JEBI  # For colors and theme
APP_NAME=Your Company Name  # For displayed name
```

---

### 3. Multi-Environment Setup

**Production (.env):**
```bash
APP_BRAND=JEBI
FLASK_ENV=production
```

**Staging (.env.staging):**
```bash
APP_BRAND=JEBI
APP_NAME=JEBI - Staging
FLASK_ENV=production
```

**Development (.env.development):**
```bash
APP_BRAND=JEBI
APP_NAME=JEBI - Dev
FLASK_ENV=development
```

---

## Migration Guide

### Migrating from Old Configuration

**Old way (required both):**
```bash
APP_BRAND=JEBI
APP_NAME=JEBI  # Had to set manually
```

**New way (automatic):**
```bash
APP_BRAND=JEBI
# APP_NAME automatically becomes "JEBI"
```

**No changes needed!** Both configurations work the same.

---

## Troubleshooting

### Issue: APP_NAME Shows "BRADKEN" but Expected "JEBI"

**Cause:** APP_NAME is explicitly set in .env file

**Solution:**
```bash
# Check .env file
cat /home/pi/Boot-Monitoring/.env | grep APP_NAME

# If you see: APP_NAME=BRADKEN
# Remove that line or change it to:
# APP_NAME=JEBI
```

---

### Issue: APP_NAME is Empty or Undefined

**Cause:** Configuration not loaded properly

**Solution:**
```bash
# Verify .env file exists
ls -la /home/pi/Boot-Monitoring/.env

# Check configuration
python -c "from config import Config; print(Config.APP_NAME)"

# Restart service
sudo systemctl restart boot-monitoring
```

---

### Issue: Different Environments Show Different Names

**Expected Behavior:** This is intentional if you have multiple .env files

**To Synchronize:**
```bash
# Production
echo "APP_BRAND=JEBI" > /home/pi/Boot-Monitoring/.env

# Development
echo "APP_BRAND=JEBI" > /home/pi/Boot-Monitoring/.env.development
```

---

## Summary

### Simple Rule:

```
If you only set APP_BRAND=JEBI
Then APP_NAME automatically becomes "JEBI"
```

### Override Rule:

```
If you set both:
  APP_BRAND=JEBI
  APP_NAME=Custom Name
Then APP_NAME will be "Custom Name"
```

### Benefits:

✅ **Less Configuration** - Only set APP_BRAND in most cases
✅ **Consistency** - Name matches brand automatically
✅ **Flexibility** - Can override when needed
✅ **No Breaking Changes** - Old configs still work

---

## Quick Reference

| Scenario | Configuration | Result APP_NAME |
|----------|--------------|-----------------|
| Default | Nothing set | "BRADKEN" |
| Set brand only | `APP_BRAND=JEBI` | "JEBI" |
| Set name only | `APP_NAME=Custom` | "Custom" |
| Set both | `APP_BRAND=JEBI`<br>`APP_NAME=Custom` | "Custom" |
| Override | `APP_BRAND=JEBI`<br>`APP_NAME=` | "" (empty) |

---

**Related Files:**
- [config.py](config.py) - Configuration logic
- [.env.example](.env.example) - Example configuration
- [templates/base.html](templates/base.html) - Page title template
- [templates/login.html](templates/login.html) - Login page usage

**Last Updated:** 2025-10-21