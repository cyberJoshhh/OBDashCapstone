// Sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log("Sidebar.js loaded");
    
    // Mobile menu toggle functionality
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (mobileMenuToggle && sidebar) {
        console.log("Found mobile toggle and sidebar elements");
        
        mobileMenuToggle.addEventListener('click', function(e) {
            console.log("Mobile toggle clicked");
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle sidebar visibility
            sidebar.classList.toggle('active');
            
            // Create or remove overlay
            if (sidebar.classList.contains('active')) {
                createSidebarOverlay();
            } else {
                removeSidebarOverlay();
            }
        });
    } else {
        console.error("Mobile toggle or sidebar not found");
        if (!mobileMenuToggle) console.error("Mobile toggle not found");
        if (!sidebar) console.error("Sidebar not found");
    }
    
    // Close sidebar when window is resized to larger than mobile breakpoint
    window.addEventListener('resize', function() {
        if (window.innerWidth > 576) {
            if (sidebar && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                removeSidebarOverlay();
            }
        }
    });
    
    // Function to create sidebar overlay
    function createSidebarOverlay() {
        // Remove any existing overlay first
        removeSidebarOverlay();
        
        // Create new overlay
        const overlay = document.createElement('div');
        overlay.id = 'sidebarOverlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
        overlay.style.zIndex = '99';
        
        // Close sidebar when overlay is clicked
        overlay.addEventListener('click', function() {
            if (sidebar) {
                sidebar.classList.remove('active');
                removeSidebarOverlay();
            }
        });
        
        document.body.appendChild(overlay);
    }
    
    // Function to remove sidebar overlay
    function removeSidebarOverlay() {
        const existingOverlay = document.getElementById('sidebarOverlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
    }
    
    // Filter students functionality
    window.filterStudents = function() {
        const searchValue = document.getElementById('searchInput').value.toLowerCase();
        
        // Check if we're on the performance page
        const performanceCards = document.querySelectorAll('.performance-card');
        if (performanceCards.length > 0) {
            performanceCards.forEach(card => {
                const studentName = card.querySelector('.card-header h3').textContent.toLowerCase();
                
                if (studentName.includes(searchValue)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
        
        // Check if we're on the dashboard page
        const studentCards = document.querySelectorAll('.student-card');
        if (studentCards.length > 0) {
            studentCards.forEach(card => {
                const studentName = card.querySelector('.student-name').textContent.toLowerCase();
                const fatherName = card.querySelector('[data-parent="father"]')?.textContent.toLowerCase() || '';
                const motherName = card.querySelector('[data-parent="mother"]')?.textContent.toLowerCase() || '';
                
                if (studentName.includes(searchValue) || 
                    fatherName.includes(searchValue) || 
                    motherName.includes(searchValue)) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        }
    };
});

// Add Student Modal functionality
const addStudentBtn = document.querySelector('.btn-add');
const addStudentModal = document.getElementById('addStudentModal');

if (addStudentBtn && addStudentModal) {
    addStudentBtn.addEventListener('click', function() {
        addStudentModal.style.display = 'block';
    });
    
    // Close modal when clicking on X
    const closeBtn = addStudentModal.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            addStudentModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === addStudentModal) {
            addStudentModal.style.display = 'none';
        }
    });
} 