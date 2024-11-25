;

// Scroll reveal animation
const scrollElements = document.querySelectorAll(".featured-section, .introduction-section, .testimonials-section, .luxury-style-section");

const elementInView = (el, offset = 0) => {
    const elementTop = el.getBoundingClientRect().top;
    return (
        elementTop <= 
        ((window.innerHeight || document.documentElement.clientHeight) - offset)
    );
};

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



// Ensure GSAP is loaded by adding this script tag in your HTML before running this script
// Select elements for animation
document.addEventListener("DOMContentLoaded", function () {
    const cursor = document.getElementById("customCursor");

    // Track cursor movement
    document.addEventListener("mousemove", (e) => {
        cursor.style.left = `${e.pageX}px`;
        cursor.style.top = `${e.pageY}px`;
        cursor.style.opacity = 1; // Make the cursor visible on movement
    });

    // Hide cursor when mouse leaves window
    document.addEventListener("mouseleave", () => {
        cursor.style.opacity = 0;
    });

    // Hover effect on interactive elements
    const interactiveElements = document.querySelectorAll("a, button, .hoverable");
    interactiveElements.forEach((element) => {
        element.addEventListener("mouseenter", () => {
            cursor.classList.add("mycircleicon-hover");
        });
        element.addEventListener("mouseleave", () => {
            cursor.classList.remove("mycircleicon-hover");
        });
    });
});


// Add hover effects to product cards
items.forEach((item) => {
    item.addEventListener("mouseenter", () => {
        gsap.to(cursor, {scale: 1, duration: 0.2, overwrite: "auto", delay: 0.2});
    });
    item.addEventListener("mouseleave", () => {
        gsap.to(cursor, {scale: 0, duration: 0.2, overwrite: "auto"});
    });
});





document.addEventListener('DOMContentLoaded', function() {
    let slides = document.querySelectorAll('.testimonial-slide');
    let dots = document.querySelectorAll('.carousel-dots .dot');
    let currentIndex = 0;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
            dots[i].classList.remove('active');
            if (i === index) {
                slide.classList.add('active');
                dots[i].classList.add('active');
            }
        });
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    dots.forEach((dot, i) => {
        dot.addEventListener('click', () => {
            currentIndex = i;
            showSlide(i);
        });
    });

    showSlide(currentIndex);

    setInterval(nextSlide, 5000); // Change slide every 5 seconds
});

document.addEventListener('DOMContentLoaded', function() {
    // For each product card
    document.querySelectorAll('.product-card').forEach(function(card) {
        const productId = card.querySelector('input[name^="size_"]')?.name.split('_')[1];
        const sizeInputs = card.querySelectorAll(`input[name="size_${productId}"]`);
        const colorInputs = card.querySelectorAll(`input[name="color_${productId}"]`);
        const sizeHiddenInput = card.querySelector('input[name="selected_size"]');
        const colorHiddenInput = card.querySelector('input[name="selected_color"]');
        
        // Update size hidden input
        sizeInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                sizeHiddenInput.value = input.value;
            });
        });
        
        // Update color hidden input
        colorInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                colorHiddenInput.value = input.value;
            });
        });
    });
});



