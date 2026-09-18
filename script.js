/* terrace.zone: shared page behaviour (self-hosted build).
   Screen the backdrop pool by theme (light/dark), then pick at random on
   every (re)load — Comprador's roll, no sessionStorage pinning. Set before
   first paint (no flash). The names are baked in because a static page can't
   list a folder, so regenerate these arrays when files in images/backdrops/
   change. */
(function () {
  var names = {
    light: [
      "backdrop",
      "round-tower",
      "roman-forum",
      "bibliotheque-nationale",
      "cenotaphe-newton"
    ],
    dark: [
      "backdrop",
      "round-tower",
      "roman-forum",
      "bibliotheque-nationale",
      "cenotaphe-newton"
    ]
  };

  var root = document.documentElement;
  var explicit = root.getAttribute("data-theme");
  var isDark = explicit
    ? explicit === "dark"
    : window.matchMedia("(prefers-color-scheme: dark)").matches;
  var variant = isDark ? "dark" : "light";
  var pool = names[variant];

  // Resolve against this script's own URL rather than the site root, so the
  // pages work unchanged whether they're served from / (terrace.zone) or from
  // a subpath (a GitHub Pages project URL). style.css does this for free,
  // since CSS url() is already relative to the stylesheet.
  var base = document.currentScript
    ? document.currentScript.src.replace(/[^/]*$/, "")
    : "/";

  var pick = pool[Math.floor(Math.random() * pool.length)];
  root.style.setProperty("--backdrop", 'url("' + base + "images/backdrops/" + pick + "-" + variant + '.webp")');
})();