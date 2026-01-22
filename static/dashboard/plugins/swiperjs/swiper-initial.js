function swiperHome() {
  const swiper_home = new Swiper(".swiper-home", {
    slidesPerView: 1,
    spaceBetween: 5,
    effect: "fade",
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  });
}

function swiperSpecialOffers() {
  const swiper_specialOffers = new Swiper(".swiper-special-offers", {
    slidesPerView: 2,
    spaceBetween: 5,
    loop: false,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      0: {
        slidesPerView: 2,
      },
      768: {
        slidesPerView: 3,
      },
      992: {
        slidesPerView: 4,
      },
      1200: {
        slidesPerView: 5,
      },
      1400: {
        slidesPerView: 6,
      },
    },
  });
}

if (document.querySelector(".swiper-buttons-control") !== null) {
  document
    .querySelector(".swiper-btn-prev")
    .addEventListener("click", () => swiper_specialOffers.slidePrev());
  document
    .querySelector(".swiper-btn-next")
    .addEventListener("click", () => swiper_specialOffers.slideNext());
}

function swiperProducts() {
  const swiper_products = new Swiper(".swiper-products", {
    slidesPerView: 2,
    spaceBetween: 5,
    loop: false,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      300: {
        slidesPerView: 2,
        spaceBetween: 5,
      },
      480: {
        slidesPerView: 2,
        spaceBetween: 8,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 10,
      },
      992: {
        slidesPerView: 4,
        spaceBetween: 12,
      },
      1200: {
        slidesPerView: 5,
        spaceBetween: 10,
      },
    },
  });
}

function swiperProductsType2() {
  const swiper_products_type2 = new Swiper(".swiper-products-type-2", {
    slidesPerView: 2,
    spaceBetween: 5,
    loop: false,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      300: {
        slidesPerView: 2,
        spaceBetween: 5,
      },
      480: {
        slidesPerView: 2,
        spaceBetween: 8,
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 10,
      },
      992: {
        slidesPerView: 3,
        spaceBetween: 12,
      },
      1200: {
        slidesPerView: 4,
        spaceBetween: 10,
      },
    },
  });
}

function swiperimageUser() {
  const swiper_imagesUser = new Swiper(".swiper-images-user", {
    slidesPerView: 1,
    spaceBetween: 10,
    loop: false,
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
      // dynamicBullets: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    on: {
      slideChange: function () {
        // تمام ویدیوهای داخل اسلایدها را پیدا کرده و آنها را متوقف کنید
        const videos = document.querySelectorAll(".swiper-slide video");
        videos.forEach((video) => {
          if (!video.paused) {
            video.pause();
          }
        });
      },
    },
  });
}

function swiperSingleProducts() {
  const swiper_singleProducts = new Swiper(".swiper-single-product", {
    slidesPerView: 1,
    spaceBetween: 10,
    loop: false,
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
  });
}

function swiperimageOfficial() {
  const swiper_imagesOfficial_thumbs = new Swiper(
    ".swiper-images-official-thumbs",
    {
      spaceBetween: 5,
      loop: false,
      freeMode: true,
      slidesPerView: "auto",
      breakpoints: {
        0: {
          spaceBetween: 5,
        },
        768: {
          spaceBetween: 10,
        },
      },
    }
  );
  const swiper_imagesOfficial = new Swiper(".swiper-images-official", {
    slidesPerView: 1,
    spaceBetween: 0,
    loop: false,
    centeredSlides: true,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    thumbs: {
      swiper: swiper_imagesOfficial_thumbs,
    },
    on: {
      slideChange: function () {
        // تمام ویدیوهای داخل اسلایدها را پیدا کرده و آنها را متوقف کنید
        const videos = document.querySelectorAll(".swiper-slide video");
        videos.forEach((video) => {
          if (!video.paused) {
            video.pause();
          }
        });
      },
    },
  });
}

function swiperBlogsHero() {
  const swiper_blogsHero = new Swiper(".swiper-blogs-hero", {
    spaceBetween: 15,
    slidesPerView: "auto",
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    autoplay: {
      delay: 4000,
      disableOnInteraction: false,
    },
    breakpoints: {
      0: {
        spaceBetween: 5,
        slidesPerView: 1,
      },
      768: {
        spaceBetween: 10,
        slidesPerView: "auto",
      },
      1800: {
        spaceBetween: 10,
        slidesPerView: "auto",
      },
    },
  });
}
