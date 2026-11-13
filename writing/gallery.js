/* terrace.zone writing gallery: pack the tiles so the grid is always a clean
   rectangle, flush at the bottom, at any column count.
   Tiles keep their order. A tile asked to be wide or tall keeps that shape;
   square tiles may be promoted to wide (2x1) or tall (1x2), never 2x2. The
   packer tries the fewest promotions first (latest tiles first) until the
   first-fit layout has no holes. Without JS the CSS grid still works, just
   with possible gaps on the last row. */
(function () {
  var grid = document.querySelector(".gallery");
  if (!grid) return;
  var tiles = Array.prototype.slice.call(grid.querySelectorAll(".tile"));
  var SQ = { w: 1, h: 1 }, WIDE = { w: 2, h: 1 }, TALL = { w: 1, h: 2 };

  function asked(t) {
    if (t.classList.contains("tile-wide")) return WIDE;
    if (t.classList.contains("tile-tall")) return TALL;
    return SQ;
  }

  // first-fit (dense) placement; returns boxes, or null if it leaves a hole
  function pack(shapes, cols) {
    var occ = [], box = [];
    function free(r, c) { return !(occ[r] && occ[r][c]); }
    for (var i = 0; i < shapes.length; i++) {
      var w = Math.min(shapes[i].w, cols), h = shapes[i].h, placed = false;
      for (var r = 0; !placed; r++) {
        for (var c = 0; c + w <= cols && !placed; c++) {
          var ok = true;
          for (var rr = r; rr < r + h && ok; rr++)
            for (var cc = c; cc < c + w && ok; cc++) ok = free(rr, cc);
          if (ok) {
            for (rr = r; rr < r + h; rr++) { occ[rr] = occ[rr] || []; for (cc = c; cc < c + w; cc++) occ[rr][cc] = 1; }
            box[i] = { r: r, c: c, w: w, h: h }; placed = true;
          }
        }
      }
    }
    for (var r2 = 0; r2 < occ.length; r2++)
      for (var c2 = 0; c2 < cols; c2++) if (free(r2, c2)) return { box: box, holes: true };
    return { box: box, holes: false };
  }

  function layout() {
    var cols = parseInt(getComputedStyle(grid).getPropertyValue("--cols"), 10) || 4;
    var base = tiles.map(asked);
    var free = [];                              // indices of square tiles, latest first
    base.forEach(function (s, i) { if (s === SQ) free.unshift(i); });

    var best = pack(base, cols);
    // try k promotions, k = 1, 2, ...; each promoted tile goes wide or tall
    for (var k = 1; best.holes && k <= free.length && k <= 6; k++) {
      var found = null;
      (function choose(start, picked) {
        if (found) return;
        if (picked.length === k) {
          var n = 1 << k;
          for (var m = 0; m < n && !found; m++) {
            var shapes = base.slice();
            picked.forEach(function (idx, j) { shapes[idx] = (m >> j) & 1 ? TALL : WIDE; });
            var p = pack(shapes, cols);
            if (!p.holes) found = p;
          }
          return;
        }
        for (var s = start; s < free.length && !found; s++) choose(s + 1, picked.concat(free[s]));
      })(0, []);
      if (found) best = found;
    }

    tiles.forEach(function (t, i) {
      var b = best.box[i];
      t.style.gridColumn = (b.c + 1) + " / span " + b.w;
      t.style.gridRow = (b.r + 1) + " / span " + b.h;
      t.style.setProperty("--rows", b.h);
    });
  }

  layout();
  var last = getComputedStyle(grid).getPropertyValue("--cols");
  window.addEventListener("resize", function () {
    var cols = getComputedStyle(grid).getPropertyValue("--cols");
    if (cols !== last) { last = cols; layout(); }
  });
})();
