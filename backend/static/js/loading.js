/**
 * loading.js - Loading states and transitions
 * Premium SaaS Dashboard
 */

(function() {
    'use strict';

    // ===== Loading Overlay =====
    const createLoadingOverlay = () => {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: rgba(246, 248, 251, 0.8);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        `;
        
        const spinner = overlay.querySelector('.loading-spinner');
        spinner.style.cssText = `
            text-align: center;
        `;
        
        const spinnerBorder = overlay.querySelector('.spinner-border');
        spinnerBorder.style.cssText = `
            width: 3rem;
            height: 3rem;
            border-width: 3px;
        `;
        
        return overlay;
    };

    // ===== Show Loading =====
    window.showLoading = () => {
        let overlay = document.querySelector('.loading-overlay');
        if (!overlay) {
            overlay = createLoadingOverlay();
            document.body.appendChild(overlay);
        }
        
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            overlay.style.visibility = 'visible';
        });
    };

    // ===== Hide Loading =====
    window.hideLoading = () => {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
            
            // Remove after transition
            setTimeout(() => {
                if (overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, 300);
        }
    };

    // ===== Button Loading State =====
    const setButtonLoading = (button, isLoading) => {
        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.classList.add('btn-loading');
            button.disabled = true;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
            }
        }
    };

    // ===== Form Submit Enhancement =====
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        
        form.addEventListener('submit', () => {
            setButtonLoading(submitBtn, true);
        });
    });

    // ===== Page Transition Loading =====
    let isLoading = false;
    
    // Show loading on link clicks
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        
        // Skip for certain links
        const href = link.getAttribute('href');
        if (!href || 
            href.startsWith('#') || 
            href.startsWith('javascript:') ||
            link.target === '_blank' ||
            e.ctrlKey || 
            e.metaKey ||
            e.shiftKey) {
            return;
        }
        
        // Don't show for same-page anchors
        if (href.startsWith('#') || href === window.location.pathname) {
            return;
        }
        
        isLoading = true;
        showLoading();
    });

    // Hide loading when page is fully loaded
    window.addEventListener('pageshow', () => {
        if (isLoading) {
            hideLoading();
            isLoading = false;
        }
    });

    // Hide loading if page is loaded from cache
    window.addEventListener('load', () => {
        setTimeout(() => {
            hideLoading();
            isLoading = false;
        }, 100);
    });

    // ===== Image Loading State =====
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        // Add loading class initially
        img.classList.add('img-loading');
        
        img.addEventListener('load', () => {
            img.classList.remove('img-loading');
            img.classList.add('img-loaded');
        });
        
        img.addEventListener('error', () => {
            img.classList.remove('img-loading');
            img.classList.add('img-error');
        });
    });

    // ===== Table Loading State =====
    window.showTableLoading = (tableContainer) => {
        if (!tableContainer) return;
        
        tableContainer.classList.add('table-loading');
        const loader = document.createElement('div');
        loader.className = 'table-loading-indicator';
        loader.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <small class="text-secondary">Loading data...</small>
        `;
        tableContainer.appendChild(loader);
    };

    window.hideTableLoading = (tableContainer) => {
        if (!tableContainer) return;
        
        tableContainer.classList.remove('table-loading');
        const loader = tableContainer.querySelector('.table-loading-indicator');
        if (loader) {
            loader.remove();
        }
    };

    // ===== Skeleton Loading (for dynamic content) =====
    const showSkeleton = (container, count = 3) => {
        const skeletons = [];
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-wrapper';
            skeleton.innerHTML = `
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text"></div>
            `;
            container.appendChild(skeleton);
            skeletons.push(skeleton);
        }
        return skeletons;
    };

    const hideSkeletons = (container) => {
        const skeletons = container.querySelectorAll('.skeleton-wrapper');
        skeletons.forEach(skeleton => skeleton.remove());
    };

    // ===== Fetch with Loading =====
    window.fetchWithLoading = async (url, options = {}) => {
        showLoading();
        try {
            const response = await fetch(url, options);
            return response;
        } finally {
            hideLoading();
        }
    };

    // ===== Auto-submit Form with Loading =====
    const setupAutoSubmitForms = () => {
        const autoSubmitForms = document.querySelectorAll('[data-auto-submit]');
        autoSubmitForms.forEach(form => {
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    if (form.dataset.autoSubmit !== 'false') {
                        setTimeout(() => {
                            const btn = form.querySelector('button[type="submit"]');
                            if (btn) setButtonLoading(btn, true);
                            form.submit();
                        }, 300);
                    }
                });
            });
        });
    };

    setupAutoSubmitForms();

    // ===== Lazy Loading Images =====
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px'
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // ===== Request Idle Callback for Non-critical Loading =====
    const scheduleIdleTask = (callback) => {
        if ('requestIdleCallback' in window) {
            requestIdleCallback(callback, { timeout: 2000 });
        } else {
            setTimeout(callback, 100);
        }
    };

    // Load non-critical features during idle time
    scheduleIdleTask(() => {
        // Preload next page data or initialize non-critical components
        console.log('[Loading] Idle tasks scheduled');
    });

    // ===== Performance Monitoring =====
    if (window.performance) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                const connectTime = perfData.responseEnd - perfData.requestStart;
                
                console.log(`%c[Performance] Page load: ${pageLoadTime}ms | Connect: ${connectTime}ms`,
                    'color: #64748B; font-size: 10px;'
                );
            }, 0);
        });
    }

    // ===== Service Worker Registration (for PWA capability) =====
    if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
        window.addEventListener('load', () => {
            // Uncomment when service worker is ready
            // navigator.serviceWorker.register('/sw.js')
            //     .then(reg => console.log('SW registered'))
            //     .catch(err => console.log('SW registration failed'));
        });
    }

})();