/* terrace.zone: shared page behaviour.
   Picks a random backdrop from the theme-appropriate pool and sets it as
   --backdrop before first paint (no flash). Included synchronously in <head>.
   The pools are baked here because a static page can't list a folder, so
   regenerate these arrays when files in images/backdrops/ change. */
(function () {
  var lightBackdrops = [
    "/images/backdrops/backdrop-light.png",
    "/images/backdrops/round-tower-light.png",
    "/images/backdrops/roman-forum-light.png",
    "/images/backdrops/bibliotheque-nationale-light.png",
    "/images/backdrops/cenotaphe-newton-light.png"
  ];
  var darkBackdrops = [
    "/images/backdrops/backdrop-dark.png",
    "/images/backdrops/round-tower-dark.png",
    "/images/backdrops/roman-forum-dark.png",
    "/images/backdrops/bibliotheque-nationale-dark.png",
    "/images/backdrops/cenotaphe-newton-dark.png"
  ];

  var root = document.documentElement;
  var explicit = root.getAttribute("data-theme");
  var isDark = explicit
    ? explicit === "dark"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;

  var pool = isDark ? darkBackdrops : lightBackdrops;
  var pick = pool[Math.floor(Math.random() * pool.length)];
  root.style.setProperty("--backdrop", 'url("' + pick + '")');
})();
