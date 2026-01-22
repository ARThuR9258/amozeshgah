var body = document.querySelector("body");

if (document.querySelector("[data-sheet-name]") != null) {
  const modalButtons = document.querySelectorAll("[data-sheet-name]");
  const totalSheet = document.querySelectorAll(".sheet");
  var sheetBackDrop = document.querySelector(".sheet-backdrop");
  modalButtons.forEach((sheetBtn) => {
    const sheetName = sheetBtn.getAttribute("data-sheet-name");
    sheetBtn.addEventListener("click", function (e) {
      sheetBackDrop.classList.add("active");
      e.preventDefault();
      showSheetDialog(sheetName);
    });
  });
}

function showSheetDialog(sheetName) {
  let sheet = document.getElementById(sheetName);
  let sheet_inner = sheet.querySelector(".inner");
  body.classList.add("fixed-position");
  sheet.classList.add("active");
  setTimeout(() => {
    sheet_inner.classList.add("show");
  }, 200);
}

function hideSheetDialog(sheetId) {
  let sheet = document.getElementById(sheetId);
  let sheet_inner = sheet.querySelector(".inner");
  body.classList.remove("fixed-position");
  sheet.classList.remove("active");
  sheetBackDrop.classList.remove("active");
  sheet_inner.classList.remove("show");
  setTimeout(() => {
    sheet_inner.classList.remove("show");
  }, 200);
}
