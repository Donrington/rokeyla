


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
