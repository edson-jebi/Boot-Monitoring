/**
 * Security utilities for JEBI Web Application
 * Prevents unauthorized access via browser back button after logout
 */

// Secure logout function
function secureLogout() {
    // Clear any local storage or session storage
    if (typeof(Storage) !== "undefined") {
        localStorage.clear();
        sessionStorage.clear();
    }
    
    // Use POST method for logout for better security
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/logout';
    
    // Add CSRF token if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = csrfToken.getAttribute('content');
        form.appendChild(csrfInput);
    }
    
    document.body.appendChild(form);
    form.submit();
}

// Prevent back button access after logout
function preventBackButtonAfterLogout() {
    // Check if we're on the login page and there's a logout message
    if (window.location.pathname.includes('/login')) {
        // Replace current history entry to prevent back navigation
        if (window.history.replaceState) {
            window.history.replaceState(null, null, window.location.href);
        }
        
        // Listen for browser back/forward navigation
        window.addEventListener('popstate', function(event) {
            // Force redirect to login if trying to navigate back
            window.location.replace('/login');
        });
        
        // Prevent page caching
        window.addEventListener('beforeunload', function() {
            // Clear any cached data
            if (typeof(Storage) !== "undefined") {
                sessionStorage.clear();
            }
        });
        
        // Add additional history entries to make back button ineffective
        window.history.pushState(null, null, window.location.href);
        window.addEventListener('popstate', function() {
            window.history.pushState(null, null, window.location.href);
        });
    }
}

// Session validation for authenticated pages
function validateSession() {
    // Only run on authenticated pages (not login page)
    if (!window.location.pathname.includes('/login')) {
        // Check session validity every 30 seconds
        setInterval(function() {
            fetch('/api/session-check', {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => {
                if (response.status === 401) {
                    // Session invalid, redirect to login
                    alert('Your session has expired. You will be redirected to the login page.');
                    window.location.replace('/login');
                }
            })
            .catch(error => {
                console.log('Session check failed:', error);
            });
        }, 30000); // Check every 30 seconds
    }
}

// Page visibility change handler to check session when page becomes visible
function handleVisibilityChange() {
    if (!document.hidden && !window.location.pathname.includes('/login')) {
        // Page became visible, check session immediately
        fetch('/api/session-check', {
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.status === 401) {
                alert('Your session has expired. You will be redirected to the login page.');
                window.location.replace('/login');
            }
        })
        .catch(error => {
            console.log('Session check failed:', error);
        });
    }
}

// Initialize security measures when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    preventBackButtonAfterLogout();
    validateSession();
    
    // Add visibility change listener
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Override logout links to use secure logout
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            secureLogout();
        });
    });
    
    // Additional security: Clear page on focus if logged out
    window.addEventListener('focus', function() {
        if (window.location.pathname.includes('/login')) {
            // Clear any form data that might be cached
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                if (form.method !== 'post' || !form.querySelector('input[name="username"]')) {
                    form.reset();
                }
            });
        }
    });
    
    // Disable right-click context menu on login page for additional security
    if (window.location.pathname.includes('/login')) {
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
        });
    }
});

// Export for use in other scripts
window.SecurityUtils = {
    secureLogout: secureLogout,
    preventBackButtonAfterLogout: preventBackButtonAfterLogout,
    validateSession: validateSession
};
