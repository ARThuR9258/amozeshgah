var initialTimes = {}; // ذخیره زمان اولیه هر تایمر
var timerIntervals = {}; // ذخیره شناسه تایمر هر تایمر

// startTimer('1', 3);

function startTimer(timerId, countdownNumber) {
  var spanElement = document.getElementById(`timer${timerId}`);
  var btnActions = document.querySelector(`.btn-resend_${timerId}`);

  var timerElementString = `timer${timerId}`;
  var timeLeft = countdownNumber;

  btnActions.style.display = "none";
  spanElement.style.display = "block";

  if (initialTimes[timerElementString] === undefined) {
    initialTimes[timerElementString] = timeLeft; // ذخیره زمان اولیه
  }

  if (timerIntervals[timerId] !== undefined) {
    clearInterval(timerIntervals[timerId]); // از بین بردن تایمر قبلی
  }

  timerIntervals[timerId] = setInterval(function () {
    if (timeLeft <= 0) {
      clearInterval(timerIntervals[timerId]);
      btnActions.style.display = "block";
      spanElement.innerHTML = "00:00";
      spanElement.style.display = "none";
    } else {
      spanElement.textContent = formatTime(timeLeft);
      timeLeft--;
      spanElement.style.display = "block";
    }
  }, 1000);
}

function formatTime(time) {
  var minutes = Math.floor(time / 60);
  var seconds = time % 60;
  return (
    minutes.toString().padStart(2, "0") +
    ":" +
    seconds.toString().padStart(2, "0")
  );
}
