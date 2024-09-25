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
        logo.src = 'rokeylafiles/RokeylaFiles/Logos/Rokeyla Logo Icon Black.png';
    } else {
        navbar.classList.remove('scrolled');
        logo.src = 'rokeylafiles/RokeylaFiles/Logos/Rokeyla Logo Icon White.png';
    }
});


// Ensure GSAP is loaded by adding this script tag in your HTML before running this script
// Select elements for animation
let items = document.querySelectorAll(".hero-section"),
    cursor = document.querySelector(".mycircleicon");

// Set initial state for the cursor
gsap.set(cursor, {autoAlpha: 1, scale: 0});

// Move cursor with mouse movement
window.addEventListener("mousemove", (e) => {
    gsap.to(cursor, {duration: 0.3, x: e.pageX, y: e.pageY, ease: "power3"});
});

// Add hover effects to images
items.forEach((item) => {
    item.addEventListener("mouseenter", () => {
        gsap.to(cursor, {scale: 1, duration: 0.2, overwrite: "auto", delay: 0.2});
    });
    item.addEventListener("mouseleave", () => {
        gsap.to(cursor, {scale: 0, duration: 0.2, overwrite: "auto"});
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
