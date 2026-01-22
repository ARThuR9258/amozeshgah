// var rangeFeedback = document.querySelectorAll('.rate-range');
// var bigValueSpan = document.querySelectorAll('.value-range');
// var pipFormats = {
//     "1": "خیلی بد",
//     "2": "بد",
//     "3": "معمولی",
//     "4": "خوب",
//     "5": "عالی",
// }
// rangeFeedback.forEach(itemRange => {
//     noUiSlider.create(itemRange, {
//         start: 3,
//         step: 1,
//         snap: true,
//         connect: 'lower',
//         behaviour: 'tap',
//         direction: 'rtl',
//         range: {
//             "min": 1,
//             "25%": 2,
//             "50%": 3,
//             "75%": 4,
//             "max": 5,
//         },
//         format: {
//             to: function (value) {
//                 // Math.round and -1, so 1.00 => 0, 2.00 => 2, etc.
//                 return ["خیلی بد", "بد", "معمولی", "خوب", "عالی"][Math.round(value) - 1];
//             },
//             from: Number
//         },
//         pips: {
//             mode: 'range',
//             density: 24,
//             format: {
//                 to: function (a) {
//                     return pipFormats[a];
//                 }
//             }
//         }
//     });
// });

// bigValueSpan.forEach((itemValue, i) => {
//     rangeFeedback[i].noUiSlider.on('update', function (values, handle) {
//         itemValue.innerHTML = values[handle];
//     });
// });

// برای میانگین قیمت
var rangePriceFilter = document.querySelectorAll(".range-price-filter");
var priceRange = [];
var sliderValueMax = [],
  sliderValueMin = [];
var maxValue = [],
  minValue = [];

rangePriceFilter.forEach((item, i) => {
  priceRange[i] = item.querySelector(".price-range");
  sliderValueMax[i] = item.querySelectorAll(".slider-value-max")[0];
  sliderValueMin[i] = item.querySelectorAll(".slider-value-min")[0];
  maxValue[i] = parseInt(sliderValueMax[i].dataset.value);
  minValue[i] = parseInt(sliderValueMin[i].dataset.value);
});
priceRange.forEach((priceItem, i) => {
  noUiSlider.create(priceItem, {
    start: [minValue[i], maxValue[i]],
    margin: 30,
    connect: true,
    direction: "rtl",
    range: {
      min: minValue[i],
      max: maxValue[i],
    },
  });
  priceItem.noUiSlider.on("update", function (values, handle) {
    if (handle) {
      sliderValueMax[i].innerHTML = separate(Math.round(values[handle]));
    } else {
      sliderValueMin[i].innerHTML = separate(Math.round(values[handle]));
    }
  });
});

function separate(Number) {
  Number += "";
  Number = Number.replace(",", "");
  x = Number.split(".");
  y = x[0];
  z = x.length > 1 ? "." + x[1] : "";
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(y)) y = y.replace(rgx, "$1" + "," + "$2");
  return y + z;
}
