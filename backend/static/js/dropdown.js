/**
 * dropdown.js - Dropdown and UI interaction enhancements
 * Premium SaaS Dashboard
 * 
 * Handles dropdown animations, notification panel,
 * search functionality, and keyboard shortcuts.
 */

(function() {
    'use strict';

    // ===== Dropdown Enhancements =====
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        // Add show class with animation
        toggle.addEventListener('show.bs.dropdown', () => {
            menu.style.animation = 'fadeInUp 0.2s ease-out';
            toggle.setAttribute('aria-expanded', 'true');
        });
        
        toggle.addEventListener('hide.bs.dropdown', () => {
            toggle.setAttribute('aria-expanded', 'false');
        });
    });

    // ===== Close dropdowns when clicking outside (single delegated listener) =====
    document.addEventListener('click', (e) => {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            const dropdown = menu.closest('.dropdown');
            if (dropdown && !dropdown.contains(e.target)) {
                const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
                if (toggle) {
                    const instance = bootstrap.Dropdown.getInstance(toggle);
                    if (instance) {
                        instance.hide();
                    } else {
                        // Fallback: remove class manually
                        menu.classList.remove('show');
                        toggle.classList.remove('show');
                        toggle.setAttribute('aria-expanded', 'false');
                    }
                }
            }
        });
    });

    // ===== Profile Dropdown Chevron Rotation =====
    const profileToggle = document.querySelector('.header-profile');
    if (profileToggle) {
        profileToggle.addEventListener('show.bs.dropdown', () => {
            profileToggle.setAttribute('aria-expanded', 'true');
        });
        
        profileToggle.addEventListener('hide.bs.dropdown', () => {
            profileToggle.setAttribute('aria-expanded', 'false');
        });
    }

    // ===== Notification Panel (placeholder for future enhancement) =====
    const notificationBtn = document.querySelector('.header-btn[title="Notifications"]');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            // Add notification count animation
            const badge = notificationBtn.querySelector('.badge-dot');
            if (badge) {
                badge.style.animation = 'none';
                badge.offsetHeight; // Trigger reflow
                badge.style.animation = 'pulse 2s ease-in-out';
            }
            
            // Here you could open a notifications dropdown/modal
            console.log('Notifications clicked - Feature ready for implementation');
        });
    }

    // ===== Search Functionality (⌘K / Ctrl+K) =====
    const searchInput = document.querySelector('.header-search input');
    const searchContainer = document.querySelector('.header-search');
    
    // Keyboard shortcut for search
    document.addEventListener('keydown', (e) => {
        // ⌘K or Ctrl+K
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                // Add visual feedback
                searchContainer.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    searchContainer.style.transform = 'scale(1)';
                }, 200);
            }
        }
        
        // Escape to blur search
        if (e.key === 'Escape' && searchInput && document.activeElement === searchInput) {
            searchInput.blur();
        }
    });

    // Search input enhancements
    if (searchInput) {
        // Clear button on input
        searchInput.addEventListener('input', (e) => {
            const value = e.target.value;
            if (value.length > 0) {
                searchInput.classList.add('has-value');
            } else {
                searchInput.classList.remove('has-value');
            }
        });
        
        // Search on Enter key
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    console.log('Search query:', query);
                    // Here you could implement global search
                    // For now, redirect to a search results page
                    // window.location.href = `/search?q=${encodeURIComponent(query)}`;
                }
            }
        });
    }

    // ===== Smooth Button Ripple Effect =====
    const buttons = document.querySelectorAll('.btn, .quick-action-item, .stats-card');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Don't add ripple to buttons with disabled state
            if (this.disabled || this.classList.contains('disabled')) return;
            
            const ripple = document.createElement('span');
            ripple.classList.add('btn-ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // ===== Active Navigation Link Smooth Scroll =====
    const activeNavLinks = document.querySelectorAll('.sidebar-nav-link.active');
    activeNavLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add click feedback
            this.style.transform = 'scale(0.97)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // ===== Table Row Hover Enhancement =====
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.2s ease';
        });
    });

    // ===== Form Input Focus Enhancement =====
    const formInputs = document.querySelectorAll('.form-control, .form-select');
    formInputs.forEach(input => {
        // Add focus animation
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateY(-1px)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = '';
        });
    });

    // ===== Card Hover Enhancement =====
    const cards = document.querySelectorAll('.card, .stats-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });

    // ===== Announcement Card Interactions =====
    const announcementCards = document.querySelectorAll('.announcement-card');
    announcementCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // If the card is wrapped in a link, let it handle navigation
            const link = this.querySelector('a');
            if (link && !e.target.closest('a')) {
                window.location.href = link.href;
            }
        });
        
        // Add cursor pointer
        const link = card.querySelector('a');
        if (link) {
            card.style.cursor = 'pointer';
        }
    });

    // ===== Quick Action Items =====
    const quickActions = document.querySelectorAll('.quick-action-item');
    quickActions.forEach(action => {
        action.addEventListener('click', function(e) {
            // Prevent default to show animation before navigation
            const href = this.getAttribute('href');
            if (href && !e.ctrlKey && !e.metaKey) {
                // Add loading state
                this.style.pointerEvents = 'none';
                this.style.opacity = '0.7';
                
                // Allow navigation after short delay
                setTimeout(() => {
                    if (href && !href.startsWith('#')) {
                        window.location.href = href;
                    }
                }, 200);
            }
        });
    });

    // ===== Empty State Button Enhancement =====
    const emptyStateBtns = document.querySelectorAll('.empty-state .btn');
    emptyStateBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // ===== Tooltip Initialization (for custom tooltips) =====
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggers.forEach(trigger => {
            new bootstrap.Tooltip(trigger, {
                animation: true,
                delay: { show: 200, hide: 100 }
            });
        });
    }

    // ===== Loading State Management =====
    // Add loading class to body during page transitions
    window.addEventListener('beforeunload', () => {
        document.body.classList.add('page-loading');
    });

    // Remove loading class after page load
    window.addEventListener('load', () => {
        document.body.classList.remove('page-loading');
    });

    // Theme.js already handles card entry animations.
    // This IntersectionObserver was duplicated and its inline opacity: 0 
    // overrode animations, causing all forms inside .card elements to be invisible.
    // Removed to fix the disappearing form bug.

    // ===== Sidebar Active Link Smooth Scroll (Mobile) =====
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        const activeLink = sidebar.querySelector('.sidebar-nav-link.active');
        if (activeLink && window.innerWidth < 992) {
            // On mobile, ensure active link is visible when sidebar opens
            const mobileToggle = document.getElementById('mobileToggle');
            if (mobileToggle) {
                mobileToggle.addEventListener('click', () => {
                    setTimeout(() => {
                        activeLink.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                });
            }
        }
    }

    // ===== Console Branding =====
    console.log('%c EduCore SMS %c Premium Edition ',
        'background: linear-gradient(135deg, #315EFB 0%, #6D7CFB 100%); color: white; padding: 8px 12px; border-radius: 6px 0 0 6px; font-weight: bold; font-size: 14px;',
        'background: #111827; color: #fff; padding: 8px 12px; border-radius: 0 6px 6px 0; font-size: 14px;'
    );
    console.log('%c✨ Professional School Management System',
        'color: #64748B; font-size: 11px; margin-top: 4px;'
    );

})();