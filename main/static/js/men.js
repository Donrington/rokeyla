
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


// Change Navbar Style on Scroll
window.addEventListener('scroll', function () {
    const navbar = document.getElementById('mainNavbar');
    const logo = document.getElementById('navbar-logo');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
        logo.src = '/static/RokeylaFiles/Logos/RokeylaLogoIconBlack.png';
    } else {
        navbar.classList.remove('scrolled');
        logo.src = '/static/RokeylaFiles/Logos/RokeylaLogoIconWhite.png';
    }
});



document.addEventListener('DOMContentLoaded', function () {
    // Cart Icon and Sidebar Elements
    const cartIcon = document.getElementById('cartIcon');
    const cartCount = document.getElementById('cartCount');
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    const closeCartBtn = document.getElementById('closeCart');
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    let cart = [];

    // Check if Add to Cart Button Exists
    const addToCartBtn = document.querySelector('.add-to-cart .button');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', addToCart);
    }

    // Event Listeners for Cart Sidebar
    if (cartIcon) {
        cartIcon.addEventListener('click', toggleCart);
    }
    if (closeCartBtn) {
        closeCartBtn.addEventListener('click', toggleCart);
    }
    if (cartOverlay) {
        cartOverlay.addEventListener('click', toggleCart);
    }

    function addToCart() {
        const quantityInput = document.querySelector('.quantity-input');
        const productTitleElement = document.querySelector('.product-title');
        const productImageElement = document.getElementById('mainProductImage');
        const productPriceElement = document.getElementById('dynamicPrice');

        if (quantityInput && productTitleElement && productImageElement && productPriceElement) {
            const quantity = parseInt(quantityInput.value);
            const productTitle = productTitleElement.textContent;
            const productImage = productImageElement.src;
            const productPrice = parseFloat(productPriceElement.textContent.replace('$', ''));

            const existingProduct = cart.find(item => item.title === productTitle);

            if (existingProduct) {
                existingProduct.quantity += quantity;
            } else {
                cart.push({
                    title: productTitle,
                    image: productImage,
                    price: productPrice,
                    quantity: quantity
                });
            }

            updateCart();
            showCartSidebar();
        } else {
            console.error('Product elements not found.');
        }
    }

    function updateCart() {
        cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);

        cartItemsContainer.innerHTML = '';
        let total = 0;

        cart.forEach(item => {
            total += item.price * item.quantity;
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <img src="${item.image}" alt="${item.title}">
                <span class="cart-item-title">${item.title}</span>
                <input type="number" class="cart-item-quantity" value="${item.quantity}" min="1">
                <span class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</span>
                <button class="remove-item">&times;</button>
            `;
            cartItemsContainer.appendChild(cartItem);

            cartItem.querySelector('.cart-item-quantity').addEventListener('change', (e) => {
                item.quantity = parseInt(e.target.value);
                updateCart();
            });

            cartItem.querySelector('.remove-item').addEventListener('click', () => {
                cart = cart.filter(cartItem => cartItem !== item);
                updateCart();
            });
        });

        cartTotal.textContent = `$${total.toFixed(2)}`;
    }

    function toggleCart() {
        const isOpen = cartSidebar.style.right === '0px';
        cartSidebar.style.right = isOpen ? '-100%' : '0px';
        cartOverlay.style.display = isOpen ? 'none' : 'block';
    }

    function showCartSidebar() {
        cartSidebar.style.right = '0px';
        cartOverlay.style.display = 'block';
    }
});


// Animate sections on scroll
const sections = document.querySelectorAll('section');
const options = {
    threshold: 0.2
};

const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
            observer.unobserve(entry.target);
        }
    });
}, options);

sections.forEach(section => {
    observer.observe(section);
});


