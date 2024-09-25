document.addEventListener('DOMContentLoaded', () => {
    const testimonials = document.querySelectorAll('.testimonial-item');
    let currentTestimonial = 0;

    function showTestimonial(index) {
        testimonials.forEach((testimonial, i) => {
            testimonial.classList.remove('active');
            if (i === index) {
                testimonial.classList.add('active');
            }
        });
    }

    // Initial display
    showTestimonial(currentTestimonial);

    // Auto-slide testimonials every 5 seconds
    setInterval(() => {
        currentTestimonial = (currentTestimonial + 1) % testimonials.length;
        showTestimonial(currentTestimonial);
    }, 5000);
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
