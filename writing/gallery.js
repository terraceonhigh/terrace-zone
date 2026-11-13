/* terrace.zone writing gallery: pack the tiles so the grid is always a clean
   rectangle, flush at the bottom, at any column count.
   Tiles keep their order and their asked-for shape (square, wide, tall);
   then every hole left at the bottom is filled by growing a neighbour into it
   (down first, then sideways). Without JS the CSS grid still works, just
   with possible gaps on the last row. */
(function () {
  var grid = document.querySelector(".gallery");
  if (!grid) return;
  var tiles = Array.prototype.slice.call(grid.querySelectorAll(".tile"));

  function want(t) {
    if (t.classList.contains("tile-wide")) return { w: 2, h: 1 };
    if (t.classList.contains("tile-tall")) return { w: 1, h: 2 };
    return { w: 1, h: 1 };
  }

  function layout() {
    var cols = parseInt(getComputedStyle(grid).getPropertyValue("--cols"), 10) || 4;
    var occ = [];              // occ[r][c] = index of tile, or undefined
    var box = [];              // {r, c, w, h}
    function free(r, c) { return !(occ[r] && occ[r][c] !== undefined); }
    function mark(i) {
      var b = box[i];
      for (var r = b.r; r < b.r + b.h; r++) {
        occ[r] = occ[r] || [];
        for (var c = b.c; c < b.c + b.w; c++) occ[r][c] = i;
      }
    }

    // 1. first-fit placement, in order (like grid-auto-flow: dense)
    tiles.forEach(function (t, i) {
      var s = want(t), w = Math.min(s.w, cols), h = s.h;
      for (var r = 0; ; r++) {
        for (var c = 0; c + w <= cols; c++) {
          var ok = true;
          for (var rr = r; rr < r + h && ok; rr++)
            for (var cc = c; cc < c + w && ok; cc++) ok = free(rr, cc);
          if (ok) { box[i] = { r: r, c: c, w: w, h: h }; mark(i); return; }
        }
      }
    });

    // 2. fill holes so the bottom is flush. For each hole, try in order:
    //    grow the left neighbour right, grow the tile above down, grow the
    //    right neighbour left; first with tiles kept at most 2x2, then without.
    var rows = occ.length;
    function growRight(r, c, cap) {
      if (c === 0 || free(r, c - 1)) return false;
      var i = occ[r][c - 1], b = box[i];
      if (b.c + b.w !== c || b.w >= cap) return false;
      for (var k = b.r; k < b.r + b.h; k++) if (!free(k, c)) return false;
      b.w++; mark(i); return true;
    }
    function growDown(r, c, cap) {
      if (r === 0 || free(r - 1, c)) return false;
      var i = occ[r - 1][c], b = box[i];
      if (b.r + b.h !== r || b.h >= cap) return false;
      for (var k = b.c; k < b.c + b.w; k++) if (!free(r, k)) return false;
      b.h++; mark(i); return true;
    }
    function growLeft(r, c, cap) {
      if (c + 1 >= cols || free(r, c + 1)) return false;
      var i = occ[r][c + 1], b = box[i];
      if (b.c !== c + 1 || b.w >= cap) return false;
      for (var k = b.r; k < b.r + b.h; k++) if (!free(k, c)) return false;
      b.c--; b.w++; mark(i); return true;
    }
    [2, 99].forEach(function (cap) {
      for (var r = 0; r < rows; r++)
        for (var c = 0; c < cols; c++)
          if (free(r, c)) growRight(r, c, cap) || growDown(r, c, cap) || growLeft(r, c, cap);
    });

    // 3. apply
    tiles.forEach(function (t, i) {
      var b = box[i];
      t.style.gridColumn = (b.c + 1) + " / span " + b.w;
      t.style.gridRow = (b.r + 1) + " / span " + b.h;
      t.style.setProperty("--rows", b.h);
    });
  }

  layout();
  var last = null;
  window.addEventListener("resize", function () {
    var cols = getComputedStyle(grid).getPropertyValue("--cols");
    if (cols !== last) { last = cols; layout(); }
  });
})();
