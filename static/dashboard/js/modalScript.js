var body = document.querySelector("body");

if (document.querySelector("[data-modal-name]") != null) {
  const modalButtons = document.querySelectorAll("[data-modal-name]");
  modalButtons.forEach((modalBtn) => {
    const modalName = modalBtn.getAttribute("data-modal-name");
    modalBtn.addEventListener("click", function (e) {
      e.preventDefault();
      showModalDialog(modalName);
    });
  });
}

function showModalDialog(modalName) {
  let modal = document.getElementById(modalName);
  let modal_dialog = modal.querySelector(".modal-dialog");
  body.classList.add("fixed-position");
  modal.classList.add("show");
  modal_dialog.classList.add("show");
}

function hideModalDialog(modalid) {
  let modal = document.getElementById(modalid);
  let modal_dialog = modal.querySelector(".modal-dialog");
  body.classList.remove("fixed-position");
  modal.classList.remove("show");
  modal_dialog.classList.remove("show");
  // setTimeout(() => {
  // }, 400);
}
