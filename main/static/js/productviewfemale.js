document.addEventListener("DOMContentLoaded", function() {
    const colorRadios = document.querySelectorAll('input[name="color"]');
    const productImage = document.getElementById("mainProductImage");
    const dynamicPrice = document.getElementById("dynamicPrice");

    const images = {
        black: "static/images/gala.jpg",
        green: "static/images/",
        red: "static/images/",
        white: "static/images/"
    };

    const prices = {
        black: "$134.90",
        green: "$144.90",
        red: "$154.90",
        white: "$124.90"
    };

    colorRadios.forEach(function(radio) {
        radio.addEventListener("change", function() {
            const selectedColor = this.value;
            productImage.src = images[selectedColor];
            dynamicPrice.textContent = prices[selectedColor];
        });
    });

    // Zoom effect
    const zoomIcon = document.querySelector(".zoom-icon");
    productImage.addEventListener("mouseover", function() {
        zoomIcon.style.display = "block";
    });

    productImage.addEventListener("mouseout", function() {
        zoomIcon.style.display = "none";
    });

    productImage.addEventListener("click", function() {
        // Implement a modal or a lightbox to show the image in full size.
    });
});


// JavaScript to handle image modal popup
const modal = document.getElementById('imageModal');
const img = document.getElementById('mainProductImage');
const modalImg = document.getElementById('fullImage');
const captionText = document.getElementById('caption');
const zoomIcon = document.querySelector('.zoom-icon');

img.onclick = function() {
    modal.style.display = "block";
    modalImg.src = this.src;
    captionText.innerHTML = this.alt;
}

zoomIcon.onclick = function() {
    modal.style.display = "block";
    modalImg.src = img.src;
    captionText.innerHTML = img.alt;
}

const closeModal = document.getElementsByClassName('close')[0];

closeModal.onclick = function() {
    modal.style.display = "none";
}


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

    addToCartBtn.addEventListener('click', addToCart);

    cartIcon.addEventListener('click', toggleCart);
    closeCartBtn.addEventListener('click', toggleCart);
    cartOverlay.addEventListener('click', toggleCart);

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
    

    function showCartSidebar() {
        cartSidebar.style.right = '0px';
        cartOverlay.style.display = 'block';
    }
});
