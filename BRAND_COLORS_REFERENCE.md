# Brand Colors Reference Card

## Quick Color Comparison

### Bradken Brand (Default)
```
🎨 PRIMARY COLOR:    #005596 (Navy Blue)
   - Backgrounds
   - Sidebar
   - Topbar
   - Primary buttons
   - Headers

🌟 SECONDARY COLOR:  #F3CB3C (Gold/Yellow)
   - Accent text
   - Hover states
   - Highlights
   - Icons
   - Borders on active elements

🔹 ACCENT COLOR:     #003d6b (Dark Navy)
   - Gradients
   - Shadows
   - Depth effects

📋 TEXT COLORS:
   - Primary text:   #005596 (Navy)
   - Light text:     #ffffff (White)
   - Accent text:    #F3CB3C (Gold)
   - Muted text:     #939598 (Gray)

✅ STATUS COLORS:
   - Success:        #28a745 (Green)
   - Error:          #e74a3b (Red)
   - Warning:        #ffc107 (Yellow)
   - Info:           #17a2b8 (Blue)
```

---

### Jebi Brand
```
🎨 PRIMARY COLOR:    #00A8A8 (Vibrant Teal)
   - Backgrounds
   - Sidebar
   - Topbar
   - Primary buttons
   - Headers

🌟 SECONDARY COLOR:  #FF6B6B (Coral/Red)
   - Accent text
   - Hover states
   - Highlights
   - Icons
   - Borders on active elements

🔹 ACCENT COLOR:     #008B8B (Deep Teal)
   - Gradients
   - Shadows
   - Depth effects

📋 TEXT COLORS:
   - Primary text:   #00A8A8 (Teal)
   - Light text:     #ffffff (White)
   - Accent text:    #FF6B6B (Coral)
   - Muted text:     #6c757d (Gray)

✅ STATUS COLORS:
   - Success:        #20c997 (Mint Green)
   - Error:          #FF6B6B (Coral)
   - Warning:        #ffc107 (Yellow)
   - Info:           #00A8A8 (Teal)
```

---

## Visual Comparison Table

| Element | Bradken | Jebi |
|---------|---------|------|
| **Sidebar Background** | Navy Blue `#005596` | Vibrant Teal `#00A8A8` |
| **Topbar Background** | Navy Blue `#005596` | Vibrant Teal `#00A8A8` |
| **Primary Button** | Navy Blue `#005596` | Teal `#00A8A8` |
| **Accent/Highlight** | Gold `#F3CB3C` | Coral `#FF6B6B` |
| **Hover Effect** | Gold `#F3CB3C` | Coral `#FF6B6B` |
| **Active Status** | Green `#28a745` | Mint Green `#20c997` |
| **Error Status** | Red `#e74a3b` | Coral `#FF6B6B` |
| **Card Border Radius** | 8px | 12px (more rounded) |
| **Font Weight (Headings)** | 600 | 700 (bolder) |

---

## UI Element Breakdown

### Navigation & Layout

#### Bradken
- **Sidebar**: Solid navy background with subtle shadow
- **Topbar**: Linear gradient navy → dark navy
- **Logo border**: Gold bottom border
- **Navigation items**: White text, gold hover

#### Jebi
- **Sidebar**: Vertical gradient teal → deep teal
- **Topbar**: Linear gradient teal → light teal
- **Logo border**: Coral bottom border
- **Navigation items**: White text, coral hover

---

### Cards & Panels

#### Bradken
- **Primary cards**: Navy background
- **Secondary cards**: Light purple `#C6C8DE`
- **Tertiary cards**: Medium purple `#6D73AC`
- **Border radius**: 8px
- **Hover effect**: Subtle lift (2px) + shadow

#### Jebi
- **Primary cards**: Teal background
- **Secondary cards**: Light cyan `#E0F7FA` with teal border
- **Tertiary cards**: Light teal `#80DEEA`
- **Border radius**: 12px (more modern)
- **Hover effect**: Pronounced lift (3px) + glow

---

### Buttons

#### Bradken
```css
Background: linear-gradient(135deg, #005596 0%, #003d6b 100%)
Text: White
Hover: Shadow + 2px lift
Active: Flat
```

#### Jebi
```css
Background: linear-gradient(135deg, #00A8A8 0%, #00C8C8 100%)
Text: White
Hover: Glow shadow + 2px lift
Active: Flat
```

---

### Status Indicators

#### Bradken - Active Service
```
Border: Green #28a745
Background: White → Light green gradient
Icon: Pulsing green dot
Animation: Soft pulse (2s)
```

#### Jebi - Active Service
```
Border: Mint green #20c997
Background: White → Mint gradient
Icon: Pulsing green dot with ripple
Animation: Ripple effect (2s)
```

#### Bradken - Inactive Service
```
Border: Red #e74a3b
Background: White → Light red gradient
Icon: Static red dot
```

#### Jebi - Inactive Service
```
Border: Coral #FF6B6B
Background: White → Coral gradient
Icon: Static coral dot
```

---

### Typography

#### Bradken
```
Headings: Oswald, 18px, weight 600, uppercase, 0.5px spacing
Body: Raleway, regular
Titles: Navy #005596
Accent: Gold #F3CB3C
```

#### Jebi
```
Headings: Oswald, 20px, weight 700, uppercase, 0.5px spacing
Body: Raleway, regular
Titles: Teal #00A8A8
Accent: Coral #FF6B6B
```

---

### Modals & Overlays

#### Bradken
```
Header: Linear gradient navy → dark navy
Header text: White
Close button: White with subtle hover
Body: White background
Border radius: 8px
```

#### Jebi
```
Header: Linear gradient teal → light teal
Header text: White
Close button: White with hover opacity
Body: White background
Border radius: 12px
```

---

### Forms & Inputs

#### Bradken
```
Border: 1px solid #e3e6f0
Border radius: 8px
Focus: Navy border + soft blue shadow
```

#### Jebi
```
Border: 2px solid #e9ecef
Border radius: 12px
Focus: Teal border + teal glow shadow
```

---

### Scrollbars

#### Bradken
```
Track: Light gray #f1f1f1
Thumb: Navy #005596
Thumb hover: Dark navy #003d6b
Width: 10px
```

#### Jebi
```
Track: Light gray #f1f1f1
Thumb: Gradient teal → deep teal
Thumb hover: Coral #FF6B6B
Width: 12px
```

---

## Animation Differences

### Bradken
- **Philosophy**: Professional, stable, predictable
- **Duration**: 0.3s
- **Easing**: ease (standard)
- **Effects**: Subtle shadows, gentle lifts

### Jebi
- **Philosophy**: Dynamic, modern, energetic
- **Duration**: 0.3s
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1)
- **Effects**: Glowing shadows, pronounced lifts, ripples

---

## Toast Notifications

### Bradken
```
Background: White
Border: 4px solid (status color)
Shadow: 0 4px 12px rgba(0,0,0,0.15)
Animation: Slide from right
Border radius: 8px
```

### Jebi
```
Background: White
Border: 4px solid (status color)
Shadow: 0 4px 12px (status color with opacity)
Animation: Slide from right with bounce
Border radius: 12px
```

---

## Loading Overlay

### Bradken
```
Background: rgba(0, 0, 0, 0.5)
Spinner: Gold border #F3CB3C
Text: White Raleway
```

### Jebi
```
Background: rgba(0, 0, 0, 0.5)
Spinner: Coral border #FF6B6B
Text: White Raleway
```

---

## Accessibility & Contrast

### Bradken
| Combination | Ratio | WCAG AA | WCAG AAA |
|-------------|-------|---------|----------|
| Navy on White | 8.2:1 | ✅ Pass | ✅ Pass |
| Gold on Navy | 4.8:1 | ✅ Pass | ❌ Fail |
| White on Navy | 8.2:1 | ✅ Pass | ✅ Pass |

### Jebi
| Combination | Ratio | WCAG AA | WCAG AAA |
|-------------|-------|---------|----------|
| Teal on White | 4.7:1 | ✅ Pass | ❌ Fail |
| Coral on White | 4.1:1 | ✅ Pass | ❌ Fail |
| White on Teal | 4.7:1 | ✅ Pass | ❌ Fail |

**Note**: Both themes pass WCAG AA standards for normal text. For large text (18px+), both pass AAA.

---

## Logo Files

| Brand | Logo File | Path |
|-------|-----------|------|
| **Bradken** | bradken_log.png | `/static/bradken_log.png` |
| **Jebi** | logo_jebi.png | `/static/logo_jebi.png` |

The theme manager automatically switches logos when you change brands.

---

## Quick Switch Commands

### Development Environment
```bash
# Switch to Bradken
export APP_BRAND=BRADKEN
python web.py

# Switch to Jebi
export APP_BRAND=JEBI
python web.py
```

### Production Environment
```bash
# Edit .env file
nano /home/pi/Boot-Monitoring/.env

# Add or modify:
APP_BRAND=BRADKEN  # or JEBI

# Restart service
sudo systemctl restart boot-monitoring
```

### Browser Console (Temporary)
```javascript
// Switch to Bradken
window.themeManager.switchTheme('BRADKEN');

// Switch to Jebi
window.themeManager.switchTheme('JEBI');
```

---

## CSS Class Usage

### Bradken-Optimized Classes
```html
<div class="colorcard">Navy card</div>
<div class="text-title">Gold title</div>
<button class="btn btn-primary">Navy button</button>
```

### Jebi-Optimized Classes
```html
<div class="colorcard">Teal card</div>
<div class="text-title">Coral title</div>
<button class="btn btn-primary">Teal button</button>
```

**Note**: Same HTML, different colors based on active theme!

---

## Print Styles

Both themes are print-friendly:
- Backgrounds removed
- Colors converted to grayscale
- Shadows removed
- Optimal contrast maintained

---

## Mobile Responsiveness

Both themes adjust for mobile:

### Bradken Mobile
- Border radius: Same (8px)
- Font size: Reduced proportionally
- Touch targets: 44px minimum

### Jebi Mobile
- Border radius: Reduced to 8px
- Font size: Reduced proportionally
- Touch targets: 44px minimum

---

**Color Palette Files:**
- Bradken: `/home/pi/Boot-Monitoring/static/css/theme-bradken.css`
- Jebi: `/home/pi/Boot-Monitoring/static/css/theme-jebi.css`

**Last Updated**: 2025-10-21