/**
 * sidebar.js - Sidebar functionality
 * Premium SaaS Dashboard
 * 
 * Handles mobile sidebar toggle, active state management,
 * and smooth transitions.
 */

(function() {
    'use strict';

    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggleBtn = document.getElementById('mobileToggle');

    if (!sidebar || !overlay || !toggleBtn) return;

    /**
     * Open the sidebar (mobile)
     */
    function openSidebar() {
        sidebar.classList.add('show');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
        toggleBtn.setAttribute('aria-expanded', 'true');
        toggleBtn.innerHTML = '<i class="bi bi-x-lg"></i>';
    }

    /**
     * Close the sidebar (mobile)
     */
    function closeSidebar() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.style.overflow = '';
        toggleBtn.setAttribute('aria-expanded', 'false');
        toggleBtn.innerHTML = '<i class="bi bi-list"></i>';
    }

    /**
     * Toggle sidebar open/close
     */
    function toggleSidebar() {
        if (sidebar.classList.contains('show')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }

    // Toggle button click
    toggleBtn.addEventListener('click', toggleSidebar);

    // Overlay click to close
    overlay.addEventListener('click', closeSidebar);

    // Close sidebar on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });

    // Close sidebar on window resize (if going to desktop)
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 992 && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });

    // Set initial aria-expanded
    toggleBtn.setAttribute('aria-expanded', 'false');

    // Highlight active nav link on page load with animation
    const activeLink = sidebar.querySelector('.sidebar-nav-link.active');
    if (activeLink) {
        // Ensure the active indicator is visible
        activeLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    console.log('[Sidebar] Initialized successfully');
})();