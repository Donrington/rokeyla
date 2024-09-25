// JavaScript functionalities for the checkout page

// Example: Handling form validations, dynamic price updates, etc.

// Place Order Button Click
document.querySelector('.custom-btn-type2').addEventListener('click', function() {
    alert('Your order has been placed!');
});

// Additional JavaScript as required
// Change Navbar Style on Scroll
window.addEventListener('scroll', function () {
    const navbar = document.getElementById('mainNavbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});



document.addEventListener('DOMContentLoaded', function () {
    const addToCartBtn = document.querySelector('.add-to-cart .button');
    const cartIcon = document.getElementById('cartIcon');
    const cartCount = document.getElementById('cartCount');
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    const closeCartBtn = document.getElementById('closeCart');
    const cartItemsContainer = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');
    let cart = [];

    // Add to cart button may not exist on all pages, so check before adding the event listener
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', addToCart);
    }

    cartIcon.addEventListener('click', toggleCart);
    closeCartBtn.addEventListener('click', closeCart);
    cartOverlay.addEventListener('click', closeCart);

    function addToCart() {
        const quantity = document.querySelector('.quantity-input').value;
        const productTitle = document.querySelector('.product-title').textContent;
        const productImage = document.getElementById('mainProductImage').src;
        const productPrice = parseFloat(document.getElementById('dynamicPrice').textContent.replace('$', ''));

        const existingProduct = cart.find(item => item.title === productTitle);

        if (existingProduct) {
            existingProduct.quantity += parseInt(quantity);
        } else {
            cart.push({
                title: productTitle,
                image: productImage,
                price: productPrice,
                quantity: parseInt(quantity)
            });
        }

        updateCart();
        showCartSidebar();
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
        const cartSidebarRight = cartSidebar.style.right === '0px' ? '-100%' : '0px';
        cartSidebar.style.right = cartSidebarRight;
        cartOverlay.style.display = cartSidebarRight === '0px' ? 'block' : 'none';
    }

    function closeCart() {
        cartSidebar.style.right = '-100%';
        cartOverlay.style.display = 'none';
    }

    function showCartSidebar() {
        cartSidebar.style.right = '0px';
        cartOverlay.style.display = 'block';
    }
});
