document.addEventListener("DOMContentLoaded", () => {
  const player = new Plyr("#player_top_video", {
    controls: [
      "play",
      "progress",
      "current-time",
      "mute",
      "volume",
      "settings",
      "fullscreen",
    ],
    // دیگر تنظیمات:
    // autoplay: true,
    // clickToPlay: false,
    // keyboard: { focused: true, global: true },
  });
});
