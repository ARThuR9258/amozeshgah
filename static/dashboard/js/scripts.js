var body = document.querySelector("body");

var MQL = 100;
if (document.getElementById("menu-category") !== null) {
  if (window.innerWidth > MQL) {
    var headerElement = document.getElementById("menu-category");
    // var loadingEl = document.querySelector(".nav-loading");
    var headerHeight = headerElement.clientHeight;

    var previousTop = 0;
    window.addEventListener("scroll", function () {
      var currentTop = window.scrollY;

      //check if user is scrolling up
      if (currentTop < previousTop) {
        //if scrolling up...
        if (currentTop > -1 && headerElement.classList.contains("is-fixed")) {
          headerElement.classList.add("is-visible");
          // loadingEl.classList.add("is-visile");
        } else {
          headerElement.classList.remove("is-visible", "is-fixed");
          // loadingEl.classList.remove("is-visile");
        }
      } else if (currentTop > previousTop) {
        //if scrolling down...
        headerElement.classList.remove("is-visible");
        // loadingEl.classList.remove("is-visile");
        if (
          currentTop > headerHeight &&
          !headerElement.classList.contains("is-fixed")
        ) {
          headerElement.classList.add("is-fixed");
        }
      }
      previousTop = currentTop;
    });
  }
}

// Header Search
if (document.getElementById("search-navbar") !== null) {
  document.addEventListener("DOMContentLoaded", function () {
    const searchNavbar = document.getElementById("search-navbar");
    const searchInner = searchNavbar.querySelector(".search-inner");
    const searchButton = document.getElementById("btn-search-mobile");

    var searchResults = searchNavbar.querySelector(".search-results");
    var searchInput = searchNavbar.querySelector(".input");
    var searchClear = searchNavbar.querySelector(".btn-search-clear");
    var searchClose = searchNavbar.querySelector(".btn-search-close");

    searchButton.addEventListener("click", function (e) {
      e.stopPropagation();
      searchInner.classList.add("active");
    });
    searchInner.addEventListener("click", function (e) {
      e.stopPropagation();
    });
    document.addEventListener("click", function () {
      searchInner.classList.remove("active");
    });

    searchInput.addEventListener("input", (input) => {
      if (input.target.value.length > 0) {
        searchResults.classList.add("active");
        searchClear.style.display = "block";
      } else {
        searchResults.classList.remove("active");
        searchClear.style.display = "none";
      }
    });
    searchClear.onclick = () => {
      searchInput.value = "";
      searchResults.classList.remove("active");
      searchClear.style.display = "none";
    };
    searchClose.onclick = () => {
      searchInput.value = "";
      searchResults.classList.remove("active");
      searchClear.style.display = "none";
      searchInner.classList.remove("active");
    };
  });
}

// Show Side Basket
if (document.querySelector(".btn-basket") !== null) {
  var btnsSideBasket = document.querySelectorAll(".btn-basket");
  var sideBasket = document.getElementById("side-basket");
  var dismissBasket = document.getElementById("dismiss-basket");
  var basketOverlay = document.querySelector(".basket-overlay");
  var body = document.querySelector("body");

  btnsSideBasket.forEach((btnBasket) => {
    btnBasket.addEventListener("click", function () {
      sideBasket.classList.add("active");
      basketOverlay.classList.add("active");
      body.classList.add("fixedposition");
    });
  });
  basketOverlay.addEventListener("click", function () {
    sideBasket.classList.remove("active");
    basketOverlay.classList.remove("active");
    body.classList.remove("fixedposition");
  });
  dismissBasket.addEventListener("click", function () {
    sideBasket.classList.remove("active");
    basketOverlay.classList.remove("active");
    body.classList.remove("fixedposition");
  });
}

// For Delete Item from side Basket
function deleteBasktet_item(el) {
  el.parentElement.parentElement.parentElement.parentElement.remove();
}

if (document.querySelector("[data-price]")) {
  const allElementPrices = document.querySelectorAll("[data-price]");
  if (allElementPrices.length > 0) {
    allElementPrices.forEach((element) => {
      var price = element.getAttribute("data-price");
      price += "";
      price = price.replace(",", "");
      x = price.split(".");
      y = x[0];
      z = x.length > 1 ? "." + x[1] : "";
      var rgx = /(\d+)(\d{3})/;
      while (rgx.test(y)) y = y.replace(rgx, "$1" + "," + "$2");
      // return y + z;
      // element.innerHTML = `${y + z} <span class="toman">تومان</span>`;
      element.innerHTML = `${y + z}`;
    });
  }
}

// MegaMenu
function InitialMegaMenu() {
  const subHeaders = document.querySelectorAll(".sub-header");
  const subCategories = document.querySelectorAll(".sub-category");
  const megaMenu = document.getElementById("megamenu");
  const megaMenu_content = megaMenu.querySelector(".mega-content");
  const megaMenu_overlay = document.querySelector(".megemenu-overlay");

  let activeIndex = 0; // Set initial active index to the first element

  // Function to activate a sub-header and sub-category by index
  function activateSubHeader(index) {
    subCategories.forEach((category) => (category.style.display = "none"));
    subHeaders.forEach((header) => header.classList.remove("active"));
    subCategories[index].style.display = "block";
    subHeaders[index].classList.add("active");
    activeIndex = index;
  }

  megaMenu_overlay.addEventListener("mouseout", () => {
    megaMenu_content.classList.remove("active");
    megaMenu_overlay.classList.remove("active");
    subCategories.forEach((category) => (category.style.display = "none"));
    subHeaders.forEach((header) => header.classList.remove("active"));
    activeIndex = -1;
  });

  subHeaders.forEach((header, index) => {
    header.addEventListener("mouseover", () => {
      activateSubHeader(index);
    });
  });

  megaMenu.addEventListener("mouseover", () => {
    megaMenu_content.classList.add("active");
    megaMenu_overlay.classList.add("active");
    if (activeIndex === -1) {
      activateSubHeader(0); // Activate the first sub-header and sub-category by default
    } else {
      subCategories[activeIndex].style.display = "block";
      subHeaders[activeIndex].classList.add("active");
    }
  });

  megaMenu.addEventListener("mouseout", (event) => {
    if (!megaMenu.contains(event.relatedTarget)) {
      megaMenu_content.classList.remove("active");
      megaMenu_overlay.classList.remove("active");
      subCategories.forEach((category) => (category.style.display = "none"));
      subHeaders.forEach((header) => header.classList.remove("active"));
      activeIndex = -1;
    }
  });
}
//if (document.getElementById("megamenu") !== null) {
//  document.addEventListener("DOMContentLoaded", function () {
//      InitialMegaMenu();
//  });
//}

// For Card Colors
if (document.querySelector(".card-colors") !== null) {
  document.querySelectorAll(".card-colors").forEach((ul) => {
    ul.querySelectorAll("li").forEach((li) => {
      const color = li.getAttribute("data-color");
      li.style.backgroundColor = color;
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const tooltipElements = document.querySelectorAll("[data-tooltip]");

  tooltipElements.forEach((element) => {
    element.addEventListener("mouseenter", function () {
      const tooltipText = this.getAttribute("data-tooltip");
      const tooltip = document.createElement("div");
      tooltip.className = "tooltip";
      tooltip.innerText = tooltipText;
      this.appendChild(tooltip);

      const elementRect = this.getBoundingClientRect();
      tooltip.style.left = `${
        elementRect.width / 2 - tooltip.offsetWidth / 2
      }px`;
      tooltip.style.top = `${-tooltip.offsetHeight - 10}px`;

      requestAnimationFrame(() => {
        tooltip.classList.add("show");
      });

      this._tooltip = tooltip;
    });

    element.addEventListener("mouseleave", function () {
      if (this._tooltip) {
        this._tooltip.remove();
        this._tooltip = null;
      }
    });
  });
});

// Change Bookmark Color Active
function changeBookmark(el) {
  el.classList.toggle("active");
}

// برای لاگین
if (document.querySelector(".login-section") != null) {
  var modalSignContent = document.querySelectorAll(".login-section");
  var currentTab = 0;
  showModalSignContent(currentTab);
}

function showModalSignContent(num) {
  for (i = 0; i < modalSignContent.length; i++) {
    modalSignContent[i].classList.remove("active");
  }
  modalSignContent[num].classList.add("active");
}

function toggleText() {
  const footer_text = document.getElementById("footer-text");
  const btn_seeMore = document.getElementById("btn-seeMore");

  if (footer_text.classList.contains("expanded")) {
    footer_text.classList.remove("expanded");
    btn_seeMore.innerHTML = `مشاهده بیشتر<i class='fi fi-rs-plus-small'></i>`;
  } else {
    footer_text.classList.add("expanded");
    btn_seeMore.innerHTML = `بستن<i class='fi fi-rs-minus-small'></i>`;
  }
}
function toggleComment(button) {
  const comment = button.previousElementSibling;
  comment.classList.toggle("expanded");
  button.style.display = "none";
}

// Collapse
if (document.querySelector(".btn-collapse") != null) {
  var collapseButtons = document.querySelectorAll(".btn-collapse");
  collapseButtons.forEach(function (button) {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      var target = document.querySelector(
        button.getAttribute("data-collapse-target")
      );
      if (target.classList.contains("show")) {
        target.classList.remove("show");
        button.classList.remove("collapsed");
      } else {
        target.classList.add("show");
        button.classList.add("collapsed");
      }
    });
  });
}

// Side Filter
if (document.querySelector(".products-side") != null) {
  var productsSide = document.querySelector(".products-side");
  var btnAdvancedSearch = document.querySelector(".btn-advanced-search");
  var closeSidebar = document.querySelector(".close-sidebar");

  btnAdvancedSearch.onclick = () => {
    productsSide.classList.add("active");
    body.classList.add("fixed-position");
  };
  closeSidebar.onclick = () => {
    productsSide.classList.remove("active");
    body.classList.remove("fixed-position");
  };
}

// Tabs
if (document.querySelectorAll(".nav-link") != null) {
  const tabsButtons = document.querySelectorAll(".nav-link");
  const tabPans = document.querySelectorAll(".tab-pane");
  tabsButtons.forEach((tabBtn, i) => {
    tabBtn.onclick = () => {
      tabPans.forEach((tabpane) => {
        tabpane.classList.add("hidden");
      });
      tabsButtons.forEach((btn) => {
        btn.classList.remove("active");
      });
      tabBtn.classList.add("active");
      tabPans[i].classList.remove("hidden");
    };
  });
}

// Change Sort
function changeSort(el) {
  let btnsGroup = document.querySelectorAll(".btn-li");
  let i;
  for (i = 0; i < btnsGroup.length; i++) {
    btnsGroup[i].classList.remove("active");
  }
  el.classList.add("active");
}

// Add Positive To Review Product
if (document.getElementById("btn-add-positive") != null) {
  document
    .getElementById("btn-add-positive")
    .addEventListener("click", function () {
      const input = document.getElementById("input-add-positive");
      const inputValue = input.value.trim();
      if (inputValue !== "") {
        const newLi = document.createElement("li");
        newLi.innerHTML = `
            <span class="name"><span class="fi fi-ss-check-circle"></span> ${inputValue}</span>
            <button class="delete"><i class="fi fi-rs-trash"></i></button>
        `;
        newLi.querySelector(".delete").addEventListener("click", function () {
          newLi.remove();
        });
        document.querySelector(".positive-list").appendChild(newLi);
        input.value = "";
      }
    });
}
// Add Negative To Revuew Product
if (document.getElementById("btn-add-negative") != null) {
  document
    .getElementById("btn-add-negative")
    .addEventListener("click", function () {
      const input = document.getElementById("input-add-negative");
      const inputValue = input.value.trim();
      if (inputValue !== "") {
        const newLi = document.createElement("li");
        newLi.innerHTML = `
            <span class="name"><span class="fi fi-ss-cross-circle"></span> ${inputValue}</span>
            <button class="delete"><i class="fi fi-rs-trash"></i></button>
        `;
        newLi.querySelector(".delete").addEventListener("click", function () {
          newLi.remove();
        });
        document.querySelector(".negative-list").appendChild(newLi);
        input.value = "";
      }
    });
}

// Copy Fuction
function copyClipboard(el) {
  var selectParentElement = el.previousElementSibling.value;
  navigator.clipboard.writeText(selectParentElement);

  el.classList.add("copied");
  el.textContent = "کپی شد‌!";

  setTimeout(() => {
    el.classList.remove("copied");
    el.textContent = "کپی کن";
  }, 2000);
}

// Change Cart Value
function changeValue(inputId, increment) {
  var input = document.getElementById(inputId);
  var value = parseInt(input.value);

  if (increment && value < 10) {
    value++;
  } else if (!increment && value > 0) {
    value--;
  }

  input.value = value;

  if (value === 0) {
    var cartItem =
      input.parentElement.parentElement.parentElement.parentElement
        .parentElement;
    cartItem.parentElement.removeChild(cartItem);
  }
}

// Choose Address
if (document.getElementById("choose-address") != null) {
  var address_content = document.getElementById("choose-address");
  var alladdress = address_content.querySelectorAll(".address-info");
  alladdress.forEach((address, i) => {
    address.addEventListener("click", () => {
      alladdress.forEach((address) => address.classList.remove("active"));
      address.classList.add("active");
    });
  });
}
function chooseAddress(el) {
  let cards_of_address = document.querySelectorAll(".card-address");
  let i;
  for (i = 0; i < cards_of_address.length; i++) {
    cards_of_address[i].classList.remove("active");
  }
  el.classList.add("active");
}

function changeGalleryImages(type) {
  const userImagesGrid = document.querySelector(".user-images-grid");
  const userImagesPreview = document.querySelector(".user-images-preview");
  if (type == "show-images-preview") {
    userImagesPreview.classList.add("active");
    userImagesGrid.classList.remove("active");
  } else if (type == "show-images-grid") {
    userImagesGrid.classList.add("active");
    userImagesPreview.classList.remove("active");
  }
}

function openReviewTab() {
  const reviewTab = document.getElementById("tab-reviews");
  const tabsButtons = document.querySelectorAll(".nav-link");
  const tabPans = document.querySelectorAll(".tab-pane");

  // پیدا کردن ایندکس تب "دیدگاه‌ها"
  const index = Array.from(tabsButtons).indexOf(reviewTab);

  if (index !== -1) {
    // غیر فعال کردن تمام تب‌ها و محتوای آنها
    tabsButtons.forEach((btn) => btn.classList.remove("active"));
    tabPans.forEach((pane) => pane.classList.add("hidden"));

    // فعال کردن تب "دیدگاه‌ها" و محتوای مربوط به آن
    reviewTab.classList.add("active");
    tabPans[index].classList.remove("hidden");

    // اسکرول به تب
    reviewTab.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}
if (document.querySelector(".btn-review") != null) {
  document.querySelector(".btn-review").addEventListener("click", function (e) {
    e.preventDefault();
    openReviewTab(); // باز کردن تب "دیدگاه‌ها"
  });
}

// User Dashboard
if (document.querySelector(".user-dashboard-section") != null) {
  var userMenu = document.querySelector(".grid-user-menu .user-menu");
  var overlayUserMenu = document.querySelector(".overlay-userMenu");
  var btnUserMenu = document.querySelector(".btn-user-menu");
  var btnCloseprofileMenu = document.querySelector(".btn-close-menu");
  btnUserMenu.onclick = () => {
    userMenu.classList.add("active");
    overlayUserMenu.classList.add("active");
  };
  overlayUserMenu.onclick = () => {
    userMenu.classList.remove("active");
    overlayUserMenu.classList.remove("active");
  };
  btnCloseprofileMenu.onclick = () => {
    userMenu.classList.remove("active");
    overlayUserMenu.classList.remove("active");
  };
}

// Dropdowns
function initialDropdown() {
  document.addEventListener("DOMContentLoaded", function () {
    const dropdownToggles = document.querySelectorAll(".dropdown-toggle");

    dropdownToggles.forEach((toggle) => {
      toggle.addEventListener("click", function () {
        const dropdownMenu = toggle.nextElementSibling;
        if (dropdownMenu.classList.contains("open")) {
          dropdownMenu.classList.remove("open");
        } else {
          closeAllDropdowns();
          dropdownMenu.classList.add("open");
        }
      });
    });
    window.addEventListener("click", function (event) {
      if (
        !event.target.matches(".dropdown-toggle") &&
        !event.target.closest(".dropdown-menu") &&
        !event.target.matches(".fi")
      ) {
        closeAllDropdowns();
      }
    });

    function closeAllDropdowns() {
      dropdownToggles.forEach((toggle) => {
        const dropdownMenu = toggle.nextElementSibling;
        if (dropdownMenu.classList.contains("open")) {
          dropdownMenu.classList.remove("open");
        }
      });
    }
  });
}

function openNotificationPanel(type) {
  // const sideNotification = document.querySelector(".side-notification");
  const tabsButtons = document.querySelectorAll(".nav-link");
  const tabPans = document.querySelectorAll(".tab-pane");

  const index = Array.from(tabsButtons).indexOf(document.getElementById(type));
  if (index !== -1) {
    tabsButtons.forEach((btn) => btn.classList.remove("active"));
    tabPans.forEach((pane) => pane.classList.add("hidden"));
    // add active class to current tab
    document.getElementById(type).classList.add("active");
    tabPans[index].classList.remove("hidden");
  }
}

function deleteAlert(el) {
  el.parentElement.remove();
}
