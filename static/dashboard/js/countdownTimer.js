document.addEventListener("DOMContentLoaded", () => {
  const countdownTimers = document.querySelectorAll(".countdown-timer");

  countdownTimers.forEach((counter) => initializeCountdown(counter));
});

function initializeCountdown(counter) {
  // ایجاد ساختار تایمر
  const timerInner = counter.querySelector(".timer-inner");
  timerInner.innerHTML = createTimerStructure();

  // دریافت تاریخ هدف و عناصر تایمر
  const targetTime = new Date(counter.getAttribute("data-countdown")).getTime();
  const [daysElem, hoursElem, minutesElem, secondsElem] =
    getTimerElements(timerInner);

  // راه‌اندازی تایمر
  const timer = setInterval(
    () =>
      updateCountdown(
        targetTime,
        { daysElem, hoursElem, minutesElem, secondsElem },
        timer
      ),
    1000
  );
}

function createTimerStructure() {
  return `
        <div class="box-time">
            <h6 class="timer-secound">00</h6>
            <span>ثانیه</span>
        </div>
        <div class="box-time">
            <h6 class="timer-minutes">00</h6>
            <span>دقیقه</span>
        </div>
        <div class="box-time">
            <h6 class="timer-hours">00</h6>
            <span>ساعت</span>
        </div>
        <div class="box-time">
            <h6 class="timer-days">00</h6>
            <span>روز</span>
        </div>
    `;
}

function getTimerElements(timerInner) {
  const daysElem = timerInner.querySelector(".timer-days");
  const hoursElem = timerInner.querySelector(".timer-hours");
  const minutesElem = timerInner.querySelector(".timer-minutes");
  const secondsElem = timerInner.querySelector(".timer-secound");

  return [daysElem, hoursElem, minutesElem, secondsElem];
}

function updateCountdown(targetTime, elements, timer) {
  const currentTime = new Date().getTime();
  const remainingTime = targetTime - currentTime;

  if (remainingTime <= 0) {
    clearInterval(timer);
    setTimerElements(elements, 0, 0, 0, 0);
    // console.log("زمان به پایان رسید.");
    return;
  }

  const days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));
  const hours = Math.floor(
    (remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
  );
  const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

  setTimerElements(elements, days, hours, minutes, seconds);
}

function setTimerElements(
  { daysElem, hoursElem, minutesElem, secondsElem },
  days,
  hours,
  minutes,
  seconds
) {
  daysElem.textContent = formatTimeUnit(days);
  hoursElem.textContent = formatTimeUnit(hours);
  minutesElem.textContent = formatTimeUnit(minutes);
  secondsElem.textContent = formatTimeUnit(seconds);
}

function formatTimeUnit(unit) {
  return unit < 10 ? `0${unit}` : unit;
}
