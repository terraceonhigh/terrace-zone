/* terrace.zone: shared page behaviour.
   Picks a random backdrop from the theme-appropriate pool and sets it as
   --backdrop before first paint (no flash). Included synchronously in <head>.
   The pools are baked here because a static page can't list a folder, so
   regenerate these arrays when files in images/backdrops/ change. */
(function () {
  var lightBackdrops = [
    "/images/backdrops/backdrop-light.webp",
    "/images/backdrops/round-tower-light.webp",
    "/images/backdrops/roman-forum-light.webp",
    "/images/backdrops/bibliotheque-nationale-light.webp",
    "/images/backdrops/cenotaphe-newton-light.webp"
  ];
  var darkBackdrops = [
    "/images/backdrops/backdrop-dark.webp",
    "/images/backdrops/round-tower-dark.webp",
    "/images/backdrops/roman-forum-dark.webp",
    "/images/backdrops/bibliotheque-nationale-dark.webp",
    "/images/backdrops/cenotaphe-newton-dark.webp"
  ];

  var root = document.documentElement;
  var explicit = root.getAttribute("data-theme");
  var isDark = explicit
    ? explicit === "dark"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;

  // Keep the pick stable for the tab, so clicking through pages doesn't reshuffle
  // the backdrop (and re-download it) on every navigation. The indexOf guard also
  // discards a stored pick whose file has since been renamed or removed.
  var pool = isDark ? darkBackdrops : lightBackdrops;
  var key = "backdrop:" + (isDark ? "dark" : "light");
  var pick;
  try { pick = sessionStorage.getItem(key); } catch (e) {}
  if (pool.indexOf(pick) === -1) {
    pick = pool[Math.floor(Math.random() * pool.length)];
    try { sessionStorage.setItem(key, pick); } catch (e) {}
  }
  root.style.setProperty("--backdrop", 'url("' + pick + '")');
})();
