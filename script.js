/* terrace.zone: shared page behaviour.
   Picks a random backdrop from the theme-appropriate pool and sets it as
   --backdrop before first paint (no flash). Included synchronously in <head>.
   The names are baked in because a static page can't list a folder, so
   regenerate these arrays when files in images/backdrops/ change. */
(function () {
  var names = [
    "backdrop",
    "round-tower",
    "roman-forum",
    "bibliotheque-nationale",
    "cenotaphe-newton"
  ];

  var root = document.documentElement;
  var explicit = root.getAttribute("data-theme");
  var isDark = explicit
    ? explicit === "dark"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;
  var variant = isDark ? "dark" : "light";

  // Resolve against this script's own URL rather than the site root, so the
  // pages work unchanged whether they're served from / (terrace.zone) or from
  // a subpath (a GitHub Pages project URL). style.css does this for free,
  // since CSS url() is already relative to the stylesheet.
  var base = document.currentScript
    ? document.currentScript.src.replace(/[^/]*$/, "")
    : "/";

  function urlFor(name) {
    return base + "images/backdrops/" + name + "-" + variant + ".webp";
  }

  // Keep the pick stable for the tab, so clicking through pages doesn't reshuffle
  // the backdrop (and re-download it) on every navigation. The indexOf guard also
  // discards a stored pick whose file has since been renamed or removed.
  var key = "backdrop:" + variant;
  var pick;
  try { pick = sessionStorage.getItem(key); } catch (e) {}
  if (names.indexOf(pick) === -1) {
    pick = names[Math.floor(Math.random() * names.length)];
    try { sessionStorage.setItem(key, pick); } catch (e) {}
  }
  root.style.setProperty("--backdrop", 'url("' + urlFor(pick) + '")');
})();
