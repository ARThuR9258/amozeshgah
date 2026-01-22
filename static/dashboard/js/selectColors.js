// For Desktop Preview Products Images
var swiper_ProductImagesPreview;
var swiper_ProductImagesThumbs;
function SwiperProductImagesThumbs() {
    swiper_ProductImagesThumbs = new Swiper(".swiper-product-images-thumbs", {
        slidesPerView: 3,
        spaceBetween: 10,
        loop: false,
        breakpoints: {
            450: {
                slidesPerView: 4,
            },
            575: {
                slidesPerView: 4,
            },
            768: {
                slidesPerView: 4,
            },
            992: {
                slidesPerView: 4,
            },
            1200: {
                slidesPerView: 5,
            },
        },
    });
    return swiper_ProductImagesThumbs;
}
function SwiperProductImagesPreview() {
    var thumbs = SwiperProductImagesThumbs();
    swiper_ProductImagesPreview = new Swiper(
        ".swiper-product-images-preview",
        {
            slidesPerView: 1,
            spaceBetween: 0,
            loop: false,
            thumbs: {
                swiper: thumbs,
            },
            pagination: {
                el: ".swiper-pagination",
                clickable: true,
                dynamicBullets: true,
            },
        }
    );
}

function SlideToAttributeValue(attributeid, valueid) {
    if (!swiper_ProductImagesPreview) {
        SwiperProductImagesPreview();
    }
    let swiperSlides = document.querySelectorAll(
        ".swiper-product-images-preview .swiper-slide"
    );

    for (let index = 0; index < swiperSlides.length; index++) {
        let slide = swiperSlides[index];
        let img = slide.querySelector("img");
        let imgAttributeId = parseInt(img.getAttribute("data-attributeid"), 10); // تبدیل به عدد
        let imgValueId = parseInt(img.getAttribute("data-valueid"), 10); // تبدیل به عدد

        if (imgAttributeId === attributeid && imgValueId === valueid) {
            swiper_ProductImagesPreview.slideTo(index); // انتقال به اسلاید مشخص
            break; // خروج از حلقه
        }
    }
}
