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



// Orders Page Functionality

(function () {
    const ordersSearchInput = document.getElementById('ordersSearch');
    const ordersTableBody = document.getElementById('ordersTableBody');

    ordersSearchInput.addEventListener('keyup', function () {
        const searchTerm = this.value.toLowerCase();
        const orders = ordersTableBody.getElementsByTagName('tr');

        Array.from(orders).forEach(function (order) {
            const orderId = order.getElementsByTagName('td')[0].textContent.toLowerCase();
            const date = order.getElementsByTagName('td')[1].textContent.toLowerCase();
            const status = order.getElementsByTagName('td')[2].textContent.toLowerCase();
            const total = order.getElementsByTagName('td')[3].textContent.toLowerCase();

            if (
                orderId.includes(searchTerm) ||
                date.includes(searchTerm) ||
                status.includes(searchTerm) ||
                total.includes(searchTerm)
            ) {
                order.style.display = '';
            } else {
                order.style.display = 'none';
            }
        });
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

    // Filter Orders
    // Custom Dropdown Functionality
    const ordersFilterButton = document.getElementById('ordersFilterButton');
    const ordersDropdownMenu = document.getElementById('ordersDropdownMenu');
    const ordersFilterText = document.getElementById('ordersFilterText');
    const ordersDropdownItems = ordersDropdownMenu.getElementsByClassName('orders-dropdown-item');

    ordersFilterButton.addEventListener('click', function (e) {
        e.stopPropagation();
        ordersDropdownMenu.classList.toggle('show');
        this.classList.toggle('open');
    });

    // Close the dropdown when clicking outside
    document.addEventListener('click', function () {
        ordersDropdownMenu.classList.remove('show');
        ordersFilterButton.classList.remove('open');
    });

    // Handle selection
    Array.from(ordersDropdownItems).forEach(function (item) {
        item.addEventListener('click', function () {
            // Remove 'selected' class from all items
            Array.from(ordersDropdownItems).forEach(function (el) {
                el.classList.remove('selected');
            });
            // Add 'selected' class to the clicked item
            this.classList.add('selected');
            // Update the button text
            ordersFilterText.textContent = this.textContent;
            // Close the dropdown
            ordersDropdownMenu.classList.remove('show');
            ordersFilterButton.classList.remove('open');
            // Filter orders
            filterOrders(this.getAttribute('data-value'));
        });
    });

    // Filter Orders Function
    function filterOrders(filterValue) {
        const orders = ordersTableBody.getElementsByTagName('tr');

        Array.from(orders).forEach(function (order) {
            const status = order.getElementsByTagName('td')[2].textContent.toLowerCase();

            if (filterValue === 'all' || status.includes(filterValue)) {
                order.style.display = '';
            } else {
                order.style.display = 'none';
            }
        });
    }
})();

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

