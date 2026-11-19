document.addEventListener("DOMContentLoaded", () => {
  const boton = document.querySelector(".menu-btn");
  const enlaces = document.querySelector(".nav-links");

  if (boton && enlaces) {
    boton.addEventListener("click", () => {
      const abierto = enlaces.classList.toggle("abierto");
      boton.setAttribute("aria-expanded", String(abierto));
      boton.innerHTML = `<i class="fa-solid fa-${abierto ? "xmark" : "bars"}"></i>`;
    });
    enlaces.querySelectorAll("a").forEach((enlace) => {
      enlace.addEventListener("click", () => {
        enlaces.classList.remove("abierto");
        boton.setAttribute("aria-expanded", "false");
      });
    });
  }

  const elementos = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observador = new IntersectionObserver((entradas, obs) => {
      entradas.forEach((entrada) => {
        if (entrada.isIntersecting) {
          entrada.target.classList.add("visible");
          obs.unobserve(entrada.target);
        }
      });
    }, { threshold: 0.12 });
    elementos.forEach((elemento, indice) => {
      elemento.style.setProperty("--delay", `${(indice % 5) * 0.07}s`);
      observador.observe(elemento);
    });
  } else {
    elementos.forEach((elemento) => elemento.classList.add("visible"));
  }

  const secciones = Array.from(document.querySelectorAll("section[id]"));
  const items = Array.from(document.querySelectorAll('.nav-links a[href^="#"]'));
  window.addEventListener("scroll", () => {
    let actual = "";
    secciones.forEach((seccion) => {
      if (window.scrollY >= seccion.offsetTop - 130) actual = seccion.id;
    });
    items.forEach((item) => {
      item.classList.toggle("activo", item.getAttribute("href") === `#${actual}`);
    });
  });
});
