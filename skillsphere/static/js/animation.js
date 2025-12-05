// ✅ Animate On Scroll Initialization
document.addEventListener('DOMContentLoaded', () => {
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 1000,
      once: true,
      easing: 'ease-in-out',
    });
  }
});

// ✅ Smooth Scroll for Anchor Links
document.addEventListener('DOMContentLoaded', () => {
  const smoothLinks = document.querySelectorAll('a[href^="#"]');
  smoothLinks.forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId.length > 1) {
        e.preventDefault();
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          window.scrollTo({
            top: targetElement.offsetTop - 70, // offset for sticky navbar
            behavior: 'smooth',
          });
        }
      }
    });
  });
});

// ✅ Scrollspy Active Section Highlight
document.addEventListener('DOMContentLoaded', () => {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link[href^="#"]');

  function activateNavLink() {
    let scrollY = window.scrollY + 120; // offset for navbar height
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');
      const link = document.querySelector(`.nav-link[href="#${sectionId}"]`);

      if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
        link?.classList.add('active');
      } else {
        link?.classList.remove('active');
      }
    });
  }

  window.addEventListener('scroll', activateNavLink);
  activateNavLink(); // Run once on load
});

// ✅ Navbar Blur Transition (on scroll)
document.addEventListener('scroll', () => {
  const header = document.querySelector('header');
  if (window.scrollY > 10) {
    header?.classList.add('nav-scrolled');
  } else {
    header?.classList.remove('nav-scrolled');
  }
});
// 🔝 Back to Top Button Logic
document.addEventListener('DOMContentLoaded', () => {
  const backToTop = document.getElementById('backToTop');
  const scrollThreshold = 400;

  window.addEventListener('scroll', () => {
    if (window.scrollY > scrollThreshold) {
      backToTop?.classList.remove('hidden');
      backToTop?.classList.add('fade-in');
    } else {
      backToTop?.classList.add('hidden');
      backToTop?.classList.remove('fade-in');
    }
  });

  backToTop?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth'});
  });
});
