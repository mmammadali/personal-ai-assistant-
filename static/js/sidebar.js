/**
 * Sidebar functionality for agent switching
 */

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    // Mobile menu toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !event.target.closest('.mobile-menu-toggle')) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    // Add mobile menu toggle button if not exists
    if (window.innerWidth <= 768 && !document.querySelector('.mobile-menu-toggle')) {
        const mobileToggle = document.createElement('button');
        mobileToggle.className = 'mobile-menu-toggle';
        mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
        document.body.appendChild(mobileToggle);
    }
    
    // Highlight active page
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath || (href === '/' && currentPath === '/')) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
});

