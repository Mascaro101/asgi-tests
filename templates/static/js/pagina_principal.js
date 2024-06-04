// Iniciar el primer swiper
var swiper1 = new Swiper(".mySwiper-1", {
  slidesPerView: 1,
  spaceBetween: 30,
  loop: true,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
});

// Iniciar el segundo swiper
var swiper2 = new Swiper(".mySwiper-2", {
  slidesPerView: 3,
  spaceBetween: 20,
  loop: true,
  loopFillGroupWithBlank: true,
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
  breakpoints: {
    0: {
      slidesPerView: 1,
    },
    520: {
      slidesPerView: 2,
    },
    950: {
      slidesPerView: 3,
    },
  },
});

// Función para avanzar automáticamente cada swiper
function autoSlideNext(swiper) {
  setInterval(function() {
    swiper.slideNext();
  }, 3000); // Cambiar cada 3 segundos
}

// Llamar a la función para avanzar automáticamente para cada swiper
autoSlideNext(swiper1);
autoSlideNext(swiper2);

  
  let tabInputs = document.querySelectorAll(".tabInput");

tabInputs.forEach(function(input) {
    input.addEventListener('change', function() {
      let id = input.getAttribute('aria-controls');
      let thisSwiper = document.getElementById('swiper' + id);
      thisSwiper.swiper.update();
    });
  });
  
  