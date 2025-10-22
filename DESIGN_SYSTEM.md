# Boot-Monitoring Design System

Version: 1.0.0

## Overview

The Boot-Monitoring Design System provides a comprehensive, consistent, and accessible UI foundation for the application. It's built with a mobile-first approach and supports multiple brand themes (Bradken and Jebi).

## Architecture

The design system is structured in three layers:

1. **Design System Base** (`design-system.css`) - Core utilities, typography, spacing, and layout
2. **Component Library** (`components.css`) - Reusable UI components
3. **Brand Themes** (`theme-bradken.css`, `theme-jebi.css`) - Brand-specific colors and styles

## Table of Contents

- [Typography](#typography)
- [Spacing System](#spacing-system)
- [Color System](#color-system)
- [Components](#components)
- [Layout Utilities](#layout-utilities)
- [Accessibility](#accessibility)
- [JavaScript API](#javascript-api)
- [Best Practices](#best-practices)

---

## Typography

### Font Scale

The system uses a rem-based font scale (16px base):

```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */
```

### Usage Examples

```html
<h1 class="text-4xl font-bold">Main Title</h1>
<h2 class="text-2xl font-semibold">Section Title</h2>
<p class="text-base leading-normal">Body text content</p>
<span class="text-sm text-muted">Helper text</span>
```

### Font Weights

- `font-light` (300)
- `font-normal` (400)
- `font-medium` (500)
- `font-semibold` (600)
- `font-bold` (700)
- `font-extrabold` (800)

### Line Heights

- `leading-tight` (1.25)
- `leading-normal` (1.5)
- `leading-relaxed` (1.75)

---

## Spacing System

The spacing system follows an 8px base scale:

| Class | Value | px  |
|-------|-------|-----|
| `m-0`, `p-0` | 0 | 0px |
| `m-1`, `p-1` | 0.25rem | 4px |
| `m-2`, `p-2` | 0.5rem | 8px |
| `m-3`, `p-3` | 0.75rem | 12px |
| `m-4`, `p-4` | 1rem | 16px |
| `m-6`, `p-6` | 1.5rem | 24px |
| `m-8`, `p-8` | 2rem | 32px |

### Directional Spacing

```html
<!-- Margin -->
<div class="mt-4">Margin top</div>
<div class="mb-6">Margin bottom</div>
<div class="mx-auto">Margin horizontal auto (centered)</div>

<!-- Padding -->
<div class="pt-4">Padding top</div>
<div class="px-6">Padding horizontal (left + right)</div>
<div class="py-4">Padding vertical (top + bottom)</div>
```

---

## Color System

Colors are defined in the brand theme files and use CSS custom properties:

### Brand Colors (Bradken Example)

```css
--brand-primary: #005596;     /* Navy Blue */
--brand-secondary: #F3CB3C;   /* Gold */
--brand-accent: #003d6b;      /* Dark Navy */
```

### Status Colors

```css
--status-success: #28a745;    /* Green */
--status-error: #e74a3b;      /* Red */
--status-warning: #ffc107;    /* Amber */
--status-info: #17a2b8;       /* Cyan */
```

### Usage in Components

Colors automatically adapt to the active brand theme. Always use CSS variables:

```css
.my-component {
    background-color: var(--brand-primary);
    color: var(--text-light);
}
```

---

## Components

### Buttons

```html
<!-- Standard button -->
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary Action</button>

<!-- Button sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>

<!-- Full width button -->
<button class="btn btn-primary btn-block">Full Width</button>

<!-- Button with icon -->
<button class="btn btn-primary btn-icon">
    <svg>...</svg>
    <span>With Icon</span>
</button>

<!-- Icon-only button -->
<button class="icon-button">
    <svg>...</svg>
</button>

<!-- Button group -->
<div class="button-group">
    <button class="btn">First</button>
    <button class="btn">Second</button>
    <button class="btn">Third</button>
</div>
```

### Cards

```html
<!-- Basic card -->
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
        <p class="card-subtitle">Optional subtitle</p>
    </div>
    <div class="card-body">
        <p>Card content goes here</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>

<!-- Interactive card (hover effect) -->
<div class="card card-interactive">
    <div class="card-body">
        Hover me!
    </div>
</div>
```

### Device Control Cards

```html
<div class="device-card">
    <div class="device-card-header">
        <h3 class="device-card-title">RevPi Device 01</h3>
        <div class="device-card-status">
            <span class="status-dot status-dot-active"></span>
            <span class="status-badge status-badge-active">Active</span>
        </div>
    </div>
    <div class="device-card-body">
        <div class="device-info-grid">
            <div class="device-info-item">
                <span class="device-info-label">IP Address</span>
                <span class="device-info-value">192.168.1.100</span>
            </div>
            <div class="device-info-item">
                <span class="device-info-label">Status</span>
                <span class="device-info-value">Online</span>
            </div>
        </div>
    </div>
    <div class="device-card-footer">
        <div class="device-card-actions">
            <button class="btn btn-primary btn-sm">Control</button>
            <button class="btn btn-secondary btn-sm">Details</button>
        </div>
    </div>
</div>
```

### Forms

```html
<div class="form-group">
    <label class="form-label form-label-required" for="username">
        Username
    </label>
    <input type="text" id="username" class="form-control" placeholder="Enter username">
    <span class="form-helper-text">Your unique username</span>
</div>

<!-- Form with error -->
<div class="form-group">
    <label class="form-label" for="email">Email</label>
    <input type="email" id="email" class="form-control" aria-invalid="true">
    <span class="form-error">Please enter a valid email address</span>
</div>

<!-- Checkbox -->
<div class="form-check">
    <input type="checkbox" id="agree" class="form-check-input">
    <label for="agree" class="form-check-label">I agree to the terms</label>
</div>

<!-- Toggle switch -->
<div class="toggle-switch">
    <input type="checkbox" id="toggle1">
    <span class="toggle-slider"></span>
</div>
```

### Status Indicators

```html
<!-- Status badges -->
<span class="status-badge status-badge-active">
    <span class="status-dot status-dot-active"></span>
    Active
</span>

<span class="status-badge status-badge-inactive">
    <span class="status-dot status-dot-inactive"></span>
    Inactive
</span>

<span class="status-badge status-badge-unknown">
    <span class="status-dot status-dot-unknown"></span>
    Unknown
</span>
```

### Service Monitor Components

```html
<div class="service-list">
    <div class="service-item">
        <div class="service-item-header">
            <div class="service-item-info">
                <span class="status-dot status-dot-active"></span>
                <div>
                    <h4 class="service-item-name">Web Server</h4>
                    <p class="service-item-description">Nginx web server</p>
                </div>
            </div>
            <div class="service-item-actions">
                <button class="btn btn-sm btn-primary">Restart</button>
                <button class="btn btn-sm btn-secondary">Stop</button>
            </div>
        </div>
        <div class="service-metrics">
            <div class="service-metric">
                <span class="service-metric-value">99.9%</span>
                <span class="service-metric-label">Uptime</span>
            </div>
            <div class="service-metric">
                <span class="service-metric-value">24ms</span>
                <span class="service-metric-label">Response</span>
            </div>
        </div>
    </div>
</div>
```

### Data Tables

```html
<table class="data-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Device 01</td>
            <td><span class="status-badge status-badge-active">Active</span></td>
            <td>
                <div class="table-actions">
                    <button class="icon-button icon-button-sm">Edit</button>
                    <button class="icon-button icon-button-sm">Delete</button>
                </div>
            </td>
        </tr>
    </tbody>
</table>
```

### Alerts

```html
<div class="alert alert-success">
    <div class="alert-title">Success!</div>
    Operation completed successfully.
</div>

<div class="alert alert-error">
    <div class="alert-title">Error</div>
    Something went wrong. Please try again.
</div>

<div class="alert alert-warning">
    <div class="alert-title">Warning</div>
    This action cannot be undone.
</div>

<div class="alert alert-info">
    <div class="alert-title">Info</div>
    New updates are available.
</div>
```

### Badges

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-secondary">Secondary</span>
<span class="badge badge-lg">Large Badge</span>
```

### Loading States

```html
<!-- Spinner -->
<div class="spinner"></div>
<div class="spinner spinner-sm"></div>
<div class="spinner spinner-lg"></div>

<!-- Skeleton loader -->
<div class="skeleton skeleton-title"></div>
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-card"></div>

<!-- Loading overlay (add to any container) -->
<div class="card" style="position: relative;">
    <div class="card-body">Content</div>
    <div class="loading-overlay">
        <div class="spinner"></div>
    </div>
</div>
```

### Empty States

```html
<div class="empty-state">
    <div class="empty-state-icon">📭</div>
    <h3 class="empty-state-title">No items found</h3>
    <p class="empty-state-description">
        There are no items to display at this time.
    </p>
    <button class="btn btn-primary">Add New Item</button>
</div>
```

---

## Layout Utilities

### Flexbox

```html
<!-- Flex container -->
<div class="flex items-center justify-between gap-4">
    <div>Item 1</div>
    <div>Item 2</div>
</div>

<!-- Flex direction -->
<div class="flex flex-col">...</div>
<div class="flex flex-row">...</div>

<!-- Alignment -->
<div class="flex items-center">...</div>    <!-- Align items vertically centered -->
<div class="flex justify-center">...</div>  <!-- Justify content horizontally centered -->
<div class="flex items-center justify-between">...</div>
```

### Grid

```html
<!-- Grid with 3 columns -->
<div class="grid grid-cols-3 gap-4">
    <div>Column 1</div>
    <div>Column 2</div>
    <div>Column 3</div>
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div>Item 1</div>
    <div>Item 2</div>
    <div>Item 3</div>
    <div>Item 4</div>
</div>

<!-- Spanning columns -->
<div class="grid grid-cols-6 gap-4">
    <div class="col-span-4">Main content (4 columns)</div>
    <div class="col-span-2">Sidebar (2 columns)</div>
</div>
```

### Responsive Breakpoints

| Breakpoint | Min Width | Prefix |
|------------|-----------|--------|
| Mobile | 0px | (none) |
| Small | 640px | `sm:` |
| Medium | 768px | `md:` |
| Large | 1024px | `lg:` |
| XLarge | 1280px | `xl:` |

```html
<!-- Hidden on mobile, visible on desktop -->
<div class="hidden md:flex">Desktop only</div>

<!-- Different layouts per breakpoint -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    ...
</div>
```

---

## Accessibility

### Features

1. **Screen Reader Support**: `.sr-only` class for screen reader-only content
2. **Focus Management**: Visible focus indicators for keyboard navigation
3. **ARIA Attributes**: Proper roles, labels, and states
4. **Keyboard Navigation**: Full keyboard support for all interactive components
5. **Color Contrast**: WCAG 2.1 AA compliant color ratios
6. **Reduced Motion**: Respects `prefers-reduced-motion` media query

### Best Practices

```html
<!-- Skip to content link -->
<a href="#main-content" class="skip-to-content">Skip to content</a>

<!-- Proper button labeling -->
<button class="icon-button" aria-label="Close dialog">
    <svg>×</svg>
</button>

<!-- Form labels -->
<label for="email">Email Address</label>
<input type="email" id="email" aria-required="true" aria-describedby="email-help">
<span id="email-help" class="form-helper-text">We'll never share your email</span>

<!-- Alert with proper role -->
<div role="alert" class="alert alert-error">
    Error message here
</div>
```

---

## JavaScript API

### Toast Notifications

```javascript
// Show success toast
DesignSystem.toast.show({
    type: 'success',
    title: 'Success!',
    message: 'Operation completed successfully',
    duration: 5000  // Auto-dismiss after 5 seconds
});

// Show error toast
DesignSystem.toast.show({
    type: 'error',
    title: 'Error',
    message: 'Something went wrong',
    closeable: true
});

// Show warning
DesignSystem.toast.show({
    type: 'warning',
    title: 'Warning',
    message: 'Please review your changes'
});

// Show info
DesignSystem.toast.show({
    type: 'info',
    message: 'New updates available'
});
```

### Confirmation Dialogs

```javascript
// Basic confirmation
const confirmed = await DesignSystem.confirm({
    title: 'Delete Device',
    message: 'Are you sure you want to delete this device? This action cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'warning'
});

if (confirmed) {
    // User clicked "Delete"
    deleteDevice();
}
```

### Loading Overlays

```javascript
// Show loading overlay on an element
const container = document.getElementById('device-list');
DesignSystem.showLoading(container);

// Perform async operation
await fetchDevices();

// Hide loading overlay
DesignSystem.hideLoading(container);
```

### Modals

```html
<!-- Modal HTML -->
<div id="myModal" data-modal class="modal-dialog" style="display: none;">
    <div class="modal-content">
        <div class="modal-header">
            <h3>Modal Title</h3>
            <button data-modal-close>&times;</button>
        </div>
        <div class="modal-body">
            Modal content
        </div>
        <div class="modal-footer">
            <button class="btn btn-primary" data-modal-close>Close</button>
        </div>
    </div>
</div>

<!-- Trigger button -->
<button data-modal-open="myModal">Open Modal</button>
```

```javascript
// Programmatic control
const modal = new DesignSystem.Modal(document.getElementById('myModal'));
modal.open();
modal.close();

// Listen to events
modal.element.addEventListener('modal:opened', () => {
    console.log('Modal opened');
});
```

### Tabs

```html
<div class="nav-tabs-modern">
    <button class="nav-tab" data-tab-target="tab1">Tab 1</button>
    <button class="nav-tab" data-tab-target="tab2">Tab 2</button>
    <button class="nav-tab" data-tab-target="tab3">Tab 3</button>
</div>

<div id="tab1" class="tab-panel">Content 1</div>
<div id="tab2" class="tab-panel">Content 2</div>
<div id="tab3" class="tab-panel">Content 3</div>
```

---

## Best Practices

### 1. Use Semantic HTML

```html
<!-- Good -->
<button class="btn btn-primary">Submit</button>
<nav class="navbar">...</nav>
<main id="main-content">...</main>

<!-- Avoid -->
<div class="btn" onclick="submit()">Submit</div>
<div class="navigation">...</div>
```

### 2. Consistent Spacing

Use the spacing scale consistently throughout the application:

```html
<!-- Good -->
<div class="card p-6 mb-4">
    <h3 class="mb-2">Title</h3>
    <p class="mb-4">Content</p>
    <button class="btn">Action</button>
</div>

<!-- Avoid inline styles -->
<div style="padding: 23px; margin-bottom: 17px;">...</div>
```

### 3. Responsive Design

Always consider mobile-first approach:

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Auto-responsive grid -->
</div>
```

### 4. Accessibility First

- Always include proper labels
- Use semantic HTML elements
- Provide keyboard navigation
- Include ARIA attributes when needed
- Test with screen readers

### 5. Performance

- Use CSS classes over inline styles
- Minimize JavaScript where CSS can work
- Lazy load images and heavy components
- Use skeleton loaders for async content

---

## Migration Guide

### From Old Styles to Design System

```html
<!-- Old -->
<div class="colorcard" style="padding: 20px;">
    <h3 class="text-title">Title</h3>
    <p class="text-second">Content</p>
</div>

<!-- New -->
<div class="card">
    <div class="card-body">
        <h3 class="card-title">Title</h3>
        <p class="text-base">Content</p>
    </div>
</div>
```

---

## Support

For questions or issues with the design system:

1. Check this documentation first
2. Review component examples in the codebase
3. Test in both Bradken and Jebi themes
4. Ensure accessibility compliance

---

## Changelog

### Version 1.0.0 (Current)

- Initial release of unified design system
- Complete component library
- JavaScript utilities for interactivity
- Full accessibility support
- Responsive grid system
- Support for multiple brand themes
