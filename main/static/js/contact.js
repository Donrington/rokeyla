


    function initMap() {
        // Map options
        var options = {
            zoom: 14,
            center: { lat: 40.7128, lng: -74.0060 }, // Rokeyla's location (Example: New York City)
            styles: [ /* Custom map styles for a modern look */ ]
        };

        // New map
        var map = new google.maps.Map(document.getElementById('map'), options);

        // Custom marker icon
        var icon = {
            url: '../images/map-marker.png', // Path to your custom marker image
            scaledSize: new google.maps.Size(50, 50), // Scaled size
            origin: new google.maps.Point(0, 0), // Origin
            anchor: new google.maps.Point(25, 50) // Anchor
        };

        // Add marker
        var marker = new google.maps.Marker({
            position: options.center,
            map: map,
            icon: icon,
            animation: google.maps.Animation.DROP
        });

        // Info window
        var infoWindow = new google.maps.InfoWindow({
            content: '<h3>Rokeyla Headquarters</h3><p>123 Fashion Avenue, Suite 100<br>New York, NY 10018</p>'
        });

        // Marker click event
        marker.addListener('click', function () {
            infoWindow.open(map, marker);
        });
    }



    document.addEventListener('DOMContentLoaded', function () {
        const contactForm = document.getElementById('contactForm');

        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Form validation
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const subject = document.getElementById('subject').value.trim();
            const message = document.getElementById('message').value.trim();

            if (name && email && subject && message) {
                // Simulate form submission
                alert('Thank you for your message! We will get back to you shortly.');
                contactForm.reset();
            } else {
                alert('Please fill in all fields.');
            }
        });
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
