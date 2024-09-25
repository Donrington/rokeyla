$(document).ready(function () {
    // Category Filter Click
    $('#categoryFilter .list-group-item').click(function () {
        const category = $(this).data('category');
        $('#categoryFilter .list-group-item').removeClass('active');
        $(this).addClass('active');
        filterProducts(category);
    });

    // Price Range Slider
    $('#priceRange').on('input', function () {
        $('#priceValue').text($(this).val());
        filterProductsByPrice($(this).val());
    });

    // Search Bar
    $('#searchBar').on('input', function () {
        const searchTerm = $(this).val().toLowerCase();
        filterProductsBySearch(searchTerm);
    });

    // Function to filter products by category
    function filterProducts(category) {
        $('.product-item').each(function () {
            const itemCategory = $(this).data('category');
            if (category === 'all' || itemCategory === category) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    }

    // Function to filter products by price
    function filterProductsByPrice(price) {
        $('.product-item').each(function () {
            const itemPrice = $(this).data('price');
            if (itemPrice <= price) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    }

    // Function to filter products by search term
    function filterProductsBySearch(searchTerm) {
        $('.product-item').each(function () {
            const itemTitle = $(this).find('.card-title').text().toLowerCase();
            if (itemTitle.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    }

    // Initial load of all products
    filterProducts('all');
});


// Change Navbar Style on Scroll
window.addEventListener('scroll', function () {
    const navbar = document.getElementById('mainNavbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});
