const navbar = document.getElementById("navbar");
const menuToggle = document.getElementById("menuToggle");
const mobileMenu = document.getElementById("mobileMenu");
const closeMenu = document.getElementById("closeMenu");
let lastScrollTop = 0;

function toggleMenu() {
  mobileMenu.classList.toggle("translate-x-full");
  document.body.classList.toggle("overflow-hidden");
}

menuToggle.addEventListener("click", toggleMenu);
closeMenu.addEventListener("click", toggleMenu);

window.addEventListener("scroll", function () {
  let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  if (scrollTop > lastScrollTop && scrollTop > 100) {
    navbar.style.transform = "translateY(-100%)";
  } else {
    navbar.style.transform = "translateY(0)";
  }
  lastScrollTop = scrollTop;

  // Add background to navbar when scrolling
  if (scrollTop > 50) {
    navbar.classList.add("bg-white/95", "dark:bg-gray-900/95", "shadow-lg");
  } else {
    navbar.classList.remove("bg-white/95", "dark:bg-gray-900/95", "shadow-lg");
  }
});

window.addEventListener("resize", function () {
  if (window.innerWidth >= 1024) {
    mobileMenu.classList.add("translate-x-full");
    document.body.classList.remove("overflow-hidden");
  }
});
