const sections = document.querySelectorAll("section");
const boxes = document.querySelectorAll(".box");
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("show");
    } else {
      entry.target.classList.remove("show");
    }
  });
});

boxes.forEach((box) => {
  observer.observe(box);
});