var sidebarCollapse = document.getElementById("sidebarCollapse");
var Sidebar = document.getElementById("sidebar");
var Content = document.getElementById("content");
var adminMenuDrop = document.getElementById("admin-drop-list");
var siderbarOverlay = document.querySelector(".siderbar-overlay");
var btn_closeSiderbar = document.querySelector(".btn-close-sidebar");

sidebarCollapse.addEventListener("click", function () {
  Sidebar.classList.toggle("active");
  Content.classList.toggle("active");
  this.classList.toggle("active");
  siderbarOverlay.classList.add("active");
});
siderbarOverlay.addEventListener("click", function () {
  Sidebar.classList.remove("active");
  Content.classList.remove("active");
  this.classList.remove("active");
  siderbarOverlay.classList.remove("active");
});
btn_closeSiderbar.addEventListener("click", function () {
  Sidebar.classList.remove("active");
  Content.classList.remove("active");
  this.classList.remove("active");
  siderbarOverlay.classList.remove("active");
});

// Dropdowns
if (document.querySelector(".dropdown") != null) {
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

// Collapse
if (document.querySelector(".btn-collapse") != null) {
  var collapseButtons = document.querySelectorAll(".btn-collapse");
  collapseButtons.forEach(function (button) {
    button.addEventListener("click", function () {
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
      element.innerHTML = `${y + z}`;
    });
  }
}

if (document.querySelector(".side-notification")) {
  var sideNotification = document.querySelector(".side-notification");
  var notifOverlay = document.querySelector(".notification-overlay");
  var btn_sideNotification = document.querySelectorAll(".btn-sideNotification");
  notifOverlay.onclick = () => {
    notifOverlay.classList.remove("active");
    sideNotification.classList.remove("active");
  };
  btn_sideNotification.forEach((btnNoti) => {
    btnNoti.addEventListener("click", () => {
      sideNotification.classList.add("active");
      notifOverlay.classList.add("active");
    });
  });
}

function openNotificationPanel(type) {
  const sideNotification = document.querySelector(".side-notification");
  const tabsButtons = sideNotification.querySelectorAll(".nav-link");
  const tabPans = sideNotification.querySelectorAll(".tab-pane");

  const index = Array.from(tabsButtons).indexOf(document.getElementById(type));
  if (index !== -1) {
    tabsButtons.forEach((btn) => btn.classList.remove("active"));
    tabPans.forEach((pane) => pane.classList.add("hidden"));
    // add active class to current tab
    document.getElementById(type).classList.add("active");
    tabPans[index].classList.remove("hidden");
  }
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

function deleteAlert(el) {
  el.parentElement.remove();
}

// برای اضافه کردن ویژگی محصول
if (document.getElementById("submitBtnFeature") !== null) {
  document
    .getElementById("submitBtnFeature")
    .addEventListener("click", addFeatureItemToTable);
}
function addFeatureItemToTable() {
  const formFeatures = document.querySelector(".product-features-add");
  // const form = event.target;
  var title = formFeatures.querySelector(".title").value;
  var feature = formFeatures.querySelector(".feature").value;
  var priority = formFeatures.querySelector(".priority").value;

  // ایجاد ردیف جدید
  const table = document
    .getElementById("featureTable")
    .getElementsByTagName("tbody")[0];

  const newRow = table.insertRow();

  // ایجاد سلول‌ها و پر کردن آن‌ها
  addCell(newRow, 0, title);
  addCell(newRow, 1, feature);
  addCell(newRow, 2, priority);
  const actionsCell = addCell(newRow, 3);

  // ایجاد دکمه‌های ویرایش و حذف
  const btnsAction = createActionButtons(newRow);
  actionsCell.appendChild(btnsAction);

  // پاک کردن فرم
  formFeatures.querySelector(".title").value = "";
  formFeatures.querySelector(".feature").value = "";
  formFeatures.querySelector(".priority").value = "";
}

function addCell(row, index, text) {
  const cell = row.insertCell(index);
  cell.innerText = text !== undefined && text !== null ? text : "";
  return cell;
}

function createActionButtons(row) {
  const btnsAction = document.createElement("div");
  btnsAction.classList.add("btns-action");

  const editButton = createButton(
    "fi fi-rs-pencil",
    "btn-circle edit-btn",
    function () {
      editRow(row);
    }
  );
  const deleteButton = createButton(
    "fi fi-rs-trash",
    "btn-circle delete-btn color-red",
    function () {
      deleteRow(row);
    }
  );

  btnsAction.appendChild(editButton);
  btnsAction.appendChild(deleteButton);

  return btnsAction;
}

function createButton(iconClass, btnClass, onClick) {
  const button = document.createElement("button");
  button.innerHTML = `<i class="${iconClass}"></i>`;
  button.classList.add(...btnClass.split(" "));
  button.addEventListener("click", onClick);
  return button;
}

function editRow(row) {
  const titleCell = row.cells[0];
  const featureCell = row.cells[1];
  const priorityCell = row.cells[2];

  const newTitle = prompt("عنوان جدید را وارد کنید:", titleCell.innerText);
  const newFeature = prompt("ویژگی جدید را وارد کنید:", featureCell.innerText);
  const newPriority = prompt(
    "اولویت جدید را وارد کنید:",
    priorityCell.innerText
  );

  if (newTitle) titleCell.innerText = newTitle;
  if (newFeature) featureCell.innerText = newFeature;
  if (newPriority) priorityCell.innerText = newPriority;
}

function deleteRow(row) {
  row.parentNode.removeChild(row);
}

// برای انتخاب رنگ
function addColorItemToTable() {
  const title = document.getElementById("color-title").value;
  const color = document.getElementById("color-select").value;
  const priority = document.getElementById("color-priority").value;

  if (title && color && priority) {
    const tableBody = document
      .getElementById("table-colors")
      .querySelector("tbody");

    const newRow = document.createElement("tr");
    newRow.innerHTML = `
      <td>${title}</td>
      <td><span style="background-color: ${color}; padding: 5px 10px; color: white; border-radius: 5px;">${color}</span></td>
      <td>${priority}</td>
      <td>
        <div class="btns-action">
          <button class="btn-circle edit-btn"><i class="fi fi-rs-pencil"></i></button>
          <button class="btn-circle color-red delete-btn"><i class="fi fi-rs-trash"></i></button>
        </div>
      </td>
    `;

    tableBody.appendChild(newRow);

    // پاک کردن فیلدهای ورودی
    document.getElementById("color-title").value = "";
    document.getElementById("color-select").value = "#000000";
    document.getElementById("color-priority").value = "";

    // افزودن رویداد به دکمه حذف
    newRow.querySelector(".delete-btn").addEventListener("click", function () {
      tableBody.removeChild(newRow);
    });
    // افزودن رویداد به دکمه ویرایش
    newRow.querySelector(".edit-btn").addEventListener("click", function () {
      editRowColors(newRow);
    });
  } else {
    alert("لطفا همه فیلدها را پر کنید.");
  }
}
function editRowColors(row) {
  const titleCell = row.cells[0];
  const colorCell = row.cells[1];
  const priorityCell = row.cells[2];

  // انتقال داده‌ها به فرم برای ویرایش
  document.getElementById("color-title").value = titleCell.innerText;
  document.getElementById("color-select").value =
    colorCell.children[0].style.backgroundColor;
  document.getElementById("color-priority").value = priorityCell.innerText;

  // حذف ردیف از جدول
  row.remove();
}
if (document.getElementById("submitBtnColor") !== null) {
  document
    .getElementById("submitBtnColor")
    .addEventListener("click", addColorItemToTable);
}
