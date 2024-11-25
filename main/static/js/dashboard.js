// JavaScript for Dashboard Functionality

// Dark Mode Toggle
const toggleSwitch = document.getElementById('themeToggle');
const body = document.body;

// Check for saved theme
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-theme');
    toggleSwitch.checked = true;
}

toggleSwitch.addEventListener('change', () => {
    body.classList.toggle('dark-theme');
    if (body.classList.contains('dark-theme')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
});

// Mobile Menu Toggle
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.querySelector('.sidebar');

menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('active');
});

// Close Sidebar on Navigation Link Click (Optional)
const navLinks = document.querySelectorAll('.nav-links a');

navLinks.forEach(link => {
    link.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });
});


// User Profile Dropdown Functionality
const userDropdownButton = document.querySelector('.user-dropdown-button');
const userDropdownMenu = document.querySelector('.user-dropdown-menu');

userDropdownButton.addEventListener('click', function (event) {
    event.stopPropagation(); // Prevent event bubbling
    const expanded = this.getAttribute('aria-expanded') === 'true' || false;
    this.setAttribute('aria-expanded', !expanded);
    this.classList.toggle('open');
    userDropdownMenu.classList.toggle('show');
});

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    if (!userDropdownButton.contains(event.target) && !userDropdownMenu.contains(event.target)) {
        userDropdownButton.setAttribute('aria-expanded', 'false');
        userDropdownButton.classList.remove('open');
        userDropdownMenu.classList.remove('show');
    }
});

// Close dropdown with Escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        userDropdownButton.setAttribute('aria-expanded', 'false');
        userDropdownButton.classList.remove('open');
        userDropdownMenu.classList.remove('show');
        userDropdownButton.focus();
    }
});

// Wishlist Page Functionality

// Event Listeners for Wishlist Buttons
