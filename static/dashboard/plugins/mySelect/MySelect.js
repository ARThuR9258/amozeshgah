document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".select-container").forEach((container) => {
    const input = container.querySelector(".select-input");
    const dropdown = container.querySelector(".dropdown-list");
    const selectedItems = container.querySelector(".selected-items");
    const selectedListItems = container.querySelector(".select-list-of-items");

    const filterDropdown = () => {
      const searchText = input.value.toLowerCase();
      [...dropdown.options].forEach((option) => {
        option.style.display = option.value.toLowerCase().includes(searchText)
          ? ""
          : "none";
      });
    };

    const addSelectedItem = (itemValue, itemText) => {
      const selectedItem = document.createElement("div");
      selectedItem.classList.add("selected-item");
      selectedItem.innerHTML = `
                <span class="text-item">${itemText}</span>
                <span class="remove-item">&times;</span>
            `;
      selectedItem.setAttribute("data-value", itemValue);
      selectedItems.appendChild(selectedItem);
    };

    const removeSelectedItem = (itemElement) => {
      const itemValue = itemElement.getAttribute("data-value");
      itemElement.remove();
      [...dropdown.options].forEach((option) => {
        if (option.value === itemValue) {
          option.disabled = false;
        }
      });
    };

    input.addEventListener("focus", () => {
      selectedListItems.style.display = "block";
      filterDropdown();
    });

    input.addEventListener("input", filterDropdown);

    dropdown.addEventListener("change", () => {
      const selectedOption = dropdown.options[dropdown.selectedIndex];
      if (!selectedOption.disabled) {
        addSelectedItem(selectedOption.value, selectedOption.text);
        selectedOption.disabled = true;
        input.value = "";
        selectedListItems.style.display = "none";
      }
    });

    selectedItems.addEventListener("click", (event) => {
      if (event.target.classList.contains("remove-item")) {
        const itemElement = event.target.parentElement;
        removeSelectedItem(itemElement);
      }
    });

    document.addEventListener("click", (event) => {
      if (!event.target.closest(".select-container")) {
        selectedListItems.style.display = "none";
      }
    });

    selectedItems.addEventListener("click", () => {
      selectedListItems.style.display = "block";
      input.focus();
    });
  });
});
