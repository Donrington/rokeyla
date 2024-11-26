// // Cart JavaScript functionalities

// document.addEventListener("DOMContentLoaded", function () {
//     // Handle remove item from cart
//     document.querySelectorAll(".remove-btn").forEach(button => {
//         button.addEventListener("click", function () {
//             const cartItem = this.closest(".cart-item");
//             cartItem.remove();
//             updateTotals();
//         });
//     });

//     // Handle quantity change
//     document.querySelectorAll(".quantity-input").forEach(input => {
//         input.addEventListener("change", function () {
//             const quantity = parseInt(this.value);
//             const priceElement = this.closest(".cart-item").querySelector(".price");
//             const subtotalElement = this.closest(".cart-item").querySelector(".subtotal");
//             const price = parseFloat(priceElement.textContent.replace("$", ""));
//             const newSubtotal = (price * quantity).toFixed(2);
//             subtotalElement.textContent = `$${newSubtotal}`;
//             updateTotals();
//         });
//     });

//     function updateTotals() {
//         let subtotal = 0;
//         document.querySelectorAll(".subtotal").forEach(subtotalElement => {
//             subtotal += parseFloat(subtotalElement.textContent.replace("$", ""));
//         });
//         document.querySelector(".subtotal-amount").textContent = `$${subtotal.toFixed(2)}`;
//         document.querySelector(".total-amount").textContent = `$${subtotal.toFixed(2)}`;
//     }
// });



// document.addEventListener('DOMContentLoaded', function () {
//     const addToCartBtn = document.querySelector('.add-to-cart .button');
//     const cartIcon = document.getElementById('cartIcon');
//     const cartCount = document.getElementById('cartCount');
//     const cartSidebar = document.getElementById('cartSidebar');
//     const cartOverlay = document.getElementById('cartOverlay');
//     const closeCartBtn = document.getElementById('closeCart');
//     const cartItemsContainer = document.getElementById('cartItems');
//     const cartTotal = document.getElementById('cartTotal');
//     let cart = [];

//     addToCartBtn.addEventListener('click', addToCart);

//     cartIcon.addEventListener('click', toggleCart);
//     closeCartBtn.addEventListener('click', toggleCart);
//     cartOverlay.addEventListener('click', toggleCart);

//     function addToCart() {
//         const quantity = document.querySelector('.quantity-input').value;
//         const productTitle = document.querySelector('.product-title').textContent;
//         const productImage = document.getElementById('mainProductImage').src;
//         const productPrice = parseFloat(document.getElementById('dynamicPrice').textContent.replace('$', ''));

//         const existingProduct = cart.find(item => item.title === productTitle);

//         if (existingProduct) {
//             existingProduct.quantity += parseInt(quantity);
//         } else {
//             cart.push({
//                 title: productTitle,
//                 image: productImage,
//                 price: productPrice,
//                 quantity: parseInt(quantity)
//             });
//         }

//         updateCart();
//         showCartSidebar();
//     }

//     function updateCart() {
//         cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);

//         cartItemsContainer.innerHTML = '';
//         let total = 0;

//         cart.forEach(item => {
//             total += item.price * item.quantity;
//             const cartItem = document.createElement('div');
//             cartItem.className = 'cart-item';
//             cartItem.innerHTML = `
//                 <img src="${item.image}" alt="${item.title}">
//                 <span class="cart-item-title">${item.title}</span>
//                 <input type="number" class="cart-item-quantity" value="${item.quantity}" min="1">
//                 <span class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</span>
//                 <button class="remove-item">&times;</button>
//             `;
//             cartItemsContainer.appendChild(cartItem);

//             cartItem.querySelector('.cart-item-quantity').addEventListener('change', (e) => {
//                 item.quantity = parseInt(e.target.value);
//                 updateCart();
//             });

//             cartItem.querySelector('.remove-item').addEventListener('click', () => {
//                 cart = cart.filter(cartItem => cartItem !== item);
//                 updateCart();
//             });
//         });

//         cartTotal.textContent = `$${total.toFixed(2)}`;
//     }

//     function toggleCart() {
//         const cartSidebarRight = cartSidebar.style.right === '0px' ? '-100%' : '0px';
//         cartSidebar.style.right = cartSidebarRight;
//         cartOverlay.style.display = cartSidebarRight === '0px' ? 'block' : 'none';
//     }
    

//     function showCartSidebar() {
//         cartSidebar.style.right = '0px';
//         cartOverlay.style.display = 'block';
//     }
// });


// // Change Navbar Style on Scroll
// window.addEventListener('scroll', function () {
//     const navbar = document.getElementById('mainNavbar');
//     if (window.scrollY > 50) {
//         navbar.classList.add('scrolled');
//     } else {
//         navbar.classList.remove('scrolled');
//     }
// });




// document.addEventListener('DOMContentLoaded', function () {
//     const addToCartBtn = document.querySelector('.add-to-cart .button');
//     const cartIcon = document.getElementById('cartIcon');
//     const cartCount = document.getElementById('cartCount');
//     const cartSidebar = document.getElementById('cartSidebar');
//     const cartOverlay = document.getElementById('cartOverlay');
//     const closeCartBtn = document.getElementById('closeCart');
//     const cartItemsContainer = document.getElementById('cartItems');
//     const cartTotal = document.getElementById('cartTotal');
//     let cart = [];

//     addToCartBtn.addEventListener('click', addToCart);

//     cartIcon.addEventListener('click', toggleCart);
//     closeCartBtn.addEventListener('click', toggleCart);
//     cartOverlay.addEventListener('click', toggleCart);

//     function addToCart() {
//         const quantity = document.querySelector('.quantity-input').value;
//         const productTitle = document.querySelector('.product-title').textContent;
//         const productImage = document.getElementById('mainProductImage').src;
//         const productPrice = parseFloat(document.getElementById('dynamicPrice').textContent.replace('$', ''));

//         const existingProduct = cart.find(item => item.title === productTitle);

//         if (existingProduct) {
//             existingProduct.quantity += parseInt(quantity);
//         } else {
//             cart.push({
//                 title: productTitle,
//                 image: productImage,
//                 price: productPrice,
//                 quantity: parseInt(quantity)
//             });
//         }

//         updateCart();
//         showCartSidebar();
//     }

//     function updateCart() {
//         cartCount.textContent = cart.reduce((sum, item) => sum + item.quantity, 0);

//         cartItemsContainer.innerHTML = '';
//         let total = 0;

//         cart.forEach(item => {
//             total += item.price * item.quantity;
//             const cartItem = document.createElement('div');
//             cartItem.className = 'cart-item';
//             cartItem.innerHTML = `
//                 <img src="${item.image}" alt="${item.title}">
//                 <span class="cart-item-title">${item.title}</span>
//                 <input type="number" class="cart-item-quantity" value="${item.quantity}" min="1">
//                 <span class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</span>
//                 <button class="remove-item">&times;</button>
//             `;
//             cartItemsContainer.appendChild(cartItem);

//             cartItem.querySelector('.cart-item-quantity').addEventListener('change', (e) => {
//                 item.quantity = parseInt(e.target.value);
//                 updateCart();
//             });

//             cartItem.querySelector('.remove-item').addEventListener('click', () => {
//                 cart = cart.filter(cartItem => cartItem !== item);
//                 updateCart();
//             });
//         });

//         cartTotal.textContent = `$${total.toFixed(2)}`;
//     }

//     function toggleCart() {
//         const cartSidebarRight = cartSidebar.style.right === '0px' ? '-100%' : '0px';
//         cartSidebar.style.right = cartSidebarRight;
//         cartOverlay.style.display = cartSidebarRight === '0px' ? 'block' : 'none';
//     }
    

//     function showCartSidebar() {
//         cartSidebar.style.right = '0px';
//         cartOverlay.style.display = 'block';
//     }
// });
