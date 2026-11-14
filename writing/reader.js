/* terrace.zone reader: chapters, progress, place memory and text settings
   for writing/*.html. Progressive enhancement: without JS the post is one
   plain page, as before. No dependencies.

   - Chapters = the post's <h2>s. With 2+ chapters you get a chapter menu,
     "chapter by chapter" or "entire work" (AO3-style), prev/next links,
     ←/→ keys, and #hash links that the back button understands.
   - Every post: progress bar, time left, "Aa" settings (size, spacing,
     width, font), and it remembers where you stopped (localStorage only;
     nothing leaves the browser). */
(function () {
  "use strict";
  var body = document.querySelector(".post-body");
  var header = document.querySelector(".post-header");
  if (!body || !header) return;

  var WPM = 238;
  var slug = (location.pathname.split("/").pop() || "post").replace(/\.html$/, "");
  var store = {
    get: function (k, d) {
      try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); }
      catch (e) { return d; }
    },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };
  function words(el) { var t = el.textContent.trim(); return t ? t.split(/\s+/).length : 0; }
  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    for (var k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }
  function fmtMin(m) {
    m = Math.max(1, Math.round(m));
    return m < 60 ? m + " min" : Math.floor(m / 60) + " h " + (m % 60 ? (m % 60) + " min" : "");
  }

  /* ---- group the flat pandoc output into <section>s, one per <h2> ---- */
  var chapters = [];
  var preface = null, cur = null;
  Array.prototype.slice.call(body.childNodes).forEach(function (node) {
    if (node.nodeType === 1 && node.tagName === "H2") {
      if (!node.id) node.id = "ch-" + (chapters.length + 1);
      cur = el("section", { "class": "chapter", "aria-labelledby": node.id });
      chapters.push({ sec: cur, h: node, id: node.id, title: node.textContent.trim() });
      body.insertBefore(cur, node);
    } else if (!cur) {
      if (node.nodeType === 1 || (node.nodeType === 3 && node.textContent.trim())) {
        if (!preface) { preface = el("div", { "class": "chapter-preface" }); body.insertBefore(preface, node); }
        preface.appendChild(node);
        return;
      }
    }
    if (cur) cur.appendChild(node);
  });
  var multi = chapters.length >= 2;
  if (!multi) {
    // a single "chapter" spanning the whole body keeps the maths uniform
    chapters = [{ sec: body, h: null, id: "", title: "" }];
    preface = null;
  }
  chapters.forEach(function (c, i) { c.i = i; c.words = words(c.sec); });
  var total = chapters.reduce(function (a, c) { return a + c.words; }, 0) || 1;
  var before = 0;
  chapters.forEach(function (c) { c.before = before; before += c.words; });

  /* ---- settings ---- */
  var SIZES = [0.92, 1, 1.05, 1.15, 1.27, 1.4];
  var LEADS = { tight: 1.55, normal: 1.78, loose: 2 };
  var WIDTHS = { narrow: "34em", normal: "none", wide: "none" };
  var prefs = store.get("tz-reader-prefs", { size: 2, lead: "normal", width: "normal", font: "serif", mode: "chapter" });
  var article = body.closest("article") || body.parentNode;
  function applyPrefs() {
    body.style.setProperty("--rd-size", SIZES[prefs.size] + "rem");
    body.style.setProperty("--rd-lead", LEADS[prefs.lead]);
    body.style.setProperty("--rd-measure", WIDTHS[prefs.width]);
    body.classList.toggle("rd-sans", prefs.font === "sans");
    document.documentElement.classList.toggle("rd-wide", prefs.width === "wide");
    store.set("tz-reader-prefs", prefs);
  }

  /* ---- the reader bar ---- */
  var bar = el("div", { "class": "reader-bar", role: "region", "aria-label": "Reader" });
  var tocBtn = el("button", { type: "button", "class": "rd-btn", "aria-expanded": "false", "aria-controls": "rd-toc" }, "☰ Chapters");
  var where = el("span", { "class": "rd-where", "aria-live": "polite" });
  var left = el("span", { "class": "rd-left" });
  var aaBtn = el("button", { type: "button", "class": "rd-btn", "aria-expanded": "false", "aria-controls": "rd-aa", title: "Text settings" }, "Aa");
  var prog = el("div", { "class": "rd-progress", role: "progressbar", "aria-label": "Progress in this work", "aria-valuemin": "0", "aria-valuemax": "100" });
  var progFill = el("span");
  prog.appendChild(progFill);
  if (multi) bar.appendChild(tocBtn);
  else bar.classList.add("rd-solo");
  bar.appendChild(el("span", { "class": "rd-break", "aria-hidden": "true" }));
  bar.appendChild(where);
  bar.appendChild(left);
  bar.appendChild(aaBtn);
  bar.appendChild(prog);

  /* chapter menu */
  var toc = el("div", { "class": "rd-panel rd-toc", id: "rd-toc", hidden: "" });
  if (multi) {
    var modes = el("div", { "class": "rd-seg", role: "group", "aria-label": "View" });
    var mChap = el("button", { type: "button", "data-mode": "chapter" }, "Chapter by chapter");
    var mAll = el("button", { type: "button", "data-mode": "entire" }, "Entire work");
    modes.appendChild(mChap); modes.appendChild(mAll);
    toc.appendChild(modes);
    var ol = el("ol");
    chapters.forEach(function (c) {
      var li = el("li");
      var a = el("a", { href: "#" + c.id });
      a.textContent = c.title;
      var m = el("span", { "class": "rd-min" }, fmtMin(c.words / WPM));
      li.appendChild(a); li.appendChild(m);
      ol.appendChild(li);
      c.link = a;
    });
    toc.appendChild(ol);
    [mChap, mAll].forEach(function (b) {
      b.addEventListener("click", function () {
        var c = currentChapter();
        prefs.mode = b.getAttribute("data-mode");
        applyPrefs(); render(c, false);
        closePanels();
      });
    });
  }
  /* download menu: EPUB and PDF as two pills, built from the end-of-story
     links (which work without JS) */
  var dls = Array.prototype.slice.call(document.querySelectorAll(".post-links a[download]"));
  var dlBtn = el("button", { type: "button", "class": "rd-btn", "aria-expanded": "false", "aria-controls": "rd-dl" }, "↓ Download");
  var dlMenu = el("div", { "class": "rd-panel rd-dlmenu", id: "rd-dl", hidden: "" });
  dls.forEach(function (d) {
    dlMenu.appendChild(el("a", { href: d.getAttribute("href"), download: "", "class": "rd-pill" }, d.textContent));
  });
  if (dls.length) bar.insertBefore(dlBtn, aaBtn);

  /* Aa panel */
  var aa = el("div", { "class": "rd-panel rd-aa", id: "rd-aa", hidden: "" });
  function row(label, opts, key) {
    var r = el("div", { "class": "rd-row" });
    r.appendChild(el("span", { "class": "rd-label" }, label));
    var g = el("div", { "class": "rd-seg", role: "group", "aria-label": label });
    opts.forEach(function (o) {
      var b = el("button", { type: "button" }, o[1]);
      b.addEventListener("click", function () {
        if (key === "size") prefs.size = Math.max(0, Math.min(SIZES.length - 1, prefs.size + o[0]));
        else prefs[key] = o[0];
        keepPlace(applyPrefs); sync();
      });
      b._val = o[0]; b._key = key;
      g.appendChild(b);
    });
    r.appendChild(g);
    aa.appendChild(r);
  }
  row("Size", [[-1, "A−"], [1, "A+"]], "size");
  row("Spacing", [["tight", "Tight"], ["normal", "Normal"], ["loose", "Loose"]], "lead");
  row("Width", [["narrow", "Narrow"], ["normal", "Normal"], ["wide", "Wide"]], "width");
  row("Font", [["serif", "Serif"], ["sans", "Sans"]], "font");

  bar.appendChild(toc);
  bar.appendChild(aa);
  bar.appendChild(dlMenu);
  // after the title block: the hero (painting + title) and its credit, if any
  var anchor = document.querySelector(".post-epigraph") || header.closest(".post-hero") || header;
  anchor.parentNode.insertBefore(bar, anchor.nextSibling);

  /* end-of-chapter navigation */
  var foot = el("nav", { "class": "rd-foot", "aria-label": "Chapters" });
  var prevA = el("a", { "class": "rd-prev", rel: "prev" });
  var idxA = el("button", { type: "button", "class": "rd-idx" }, "Chapter index");
  var nextA = el("a", { "class": "rd-next", rel: "next" });
  foot.appendChild(prevA); foot.appendChild(idxA); foot.appendChild(nextA);
  if (multi) body.parentNode.insertBefore(foot, body.nextSibling);
  idxA.addEventListener("click", function () {
    bar.scrollIntoView({ block: "start" });
    openPanel(toc, tocBtn);
  });

  /* ---- panels ---- */
  function closePanels() {
    [[toc, tocBtn], [aa, aaBtn], [dlMenu, dlBtn]].forEach(function (p) { p[0].hidden = true; p[1].setAttribute("aria-expanded", "false"); });
  }
  function openPanel(p, b) {
    var was = !p.hidden;
    closePanels();
    if (!was) { p.hidden = false; b.setAttribute("aria-expanded", "true"); sync(); }
  }
  tocBtn.addEventListener("click", function (e) { e.stopPropagation(); openPanel(toc, tocBtn); });
  aaBtn.addEventListener("click", function (e) { e.stopPropagation(); openPanel(aa, aaBtn); });
  dlBtn.addEventListener("click", function (e) { e.stopPropagation(); openPanel(dlMenu, dlBtn); });
  document.addEventListener("click", function (e) { if (!bar.contains(e.target)) closePanels(); });
  toc.addEventListener("click", function (e) { if (e.target.tagName === "A" && e.target.hash) closePanels(); });

  /* ---- chapter view ---- */
  var shown = chapters[0];
  function chapterFor(id) {
    if (!id) return null;
    var t = document.getElementById(id);
    if (!t) return null;
    for (var i = 0; i < chapters.length; i++) if (chapters[i].sec.contains(t)) return chapters[i];
    return null;
  }
  function currentChapter() {
    if (!multi) return chapters[0];
    if (prefs.mode === "chapter") return shown;
    var c = chapters[0];
    for (var i = 0; i < chapters.length; i++) {
      if (chapters[i].sec.getBoundingClientRect().top < innerHeight * 0.35) c = chapters[i]; else break;
    }
    return c;
  }
  function render(c, scrollTop) {
    c = c || chapters[0];
    shown = c;
    var single = multi && prefs.mode === "chapter";
    chapters.forEach(function (x) { x.sec.hidden = single && x !== c; });
    if (preface) preface.hidden = single && c.i !== 0;
    foot.hidden = !single;
    document.documentElement.classList.toggle("rd-single", single);
    if (single) {
      var p = chapters[c.i - 1], n = chapters[c.i + 1];
      prevA.hidden = !p; nextA.hidden = !n;
      if (p) { prevA.href = "#" + p.id; prevA.textContent = "← " + p.title; }
      if (n) { nextA.href = "#" + n.id; nextA.textContent = n.title + " →"; }
    }
    if (scrollTop) {
      var y = (single ? c.h : c.h || body).getBoundingClientRect().top + scrollY - bar.offsetHeight - 12;
      scrollTo(0, Math.max(0, y));
    }
    sync();
  }

  /* ---- progress, time left, place memory ---- */
  function fractionIn(c) {
    var r = c.sec.getBoundingClientRect();
    var span = r.height - innerHeight * 0.6;
    if (span <= 0) return r.top < innerHeight ? 1 : 0;
    return Math.max(0, Math.min(1, (-r.top + innerHeight * 0.2) / span));
  }
  function sync() {
    var c = currentChapter();
    var f = fractionIn(c);
    var done = (c.before + f * c.words) / total;
    var pct = Math.round(done * 100);
    progFill.style.width = (done * 100).toFixed(2) + "%";
    prog.setAttribute("aria-valuenow", String(pct));
    if (multi) {
      where.textContent = c.title + " · " + (c.i + 1) + "/" + chapters.length;
      left.textContent = fmtMin((1 - f) * c.words / WPM) + " left in chapter · " + pct + "%";
      chapters.forEach(function (x) {
        if (!x.link) return;
        if (x === c) x.link.setAttribute("aria-current", "location");
        else x.link.removeAttribute("aria-current");
      });
      if (mChap) {
        mChap.setAttribute("aria-pressed", String(prefs.mode === "chapter"));
        mAll.setAttribute("aria-pressed", String(prefs.mode === "entire"));
      }
    } else {
      where.textContent = "";
      left.textContent = fmtMin((1 - done) * total / WPM) + " left · " + pct + "%";
    }
    Array.prototype.forEach.call(aa.querySelectorAll("button"), function (b) {
      if (b._key === "size") b.disabled = (b._val < 0 ? prefs.size <= 0 : prefs.size >= SIZES.length - 1);
      else b.setAttribute("aria-pressed", String(prefs[b._key] === b._val));
    });
    return { c: c, f: f, done: done };
  }
  var saveT = 0;
  function save() {
    var s = sync();
    store.set("tz-read:" + slug, { id: s.c.id, f: +s.f.toFixed(4), done: +s.done.toFixed(4), t: Date.now() });
  }
  function goTo(c, f) {
    render(c, false);
    var r = c.sec.getBoundingClientRect();
    var span = r.height - innerHeight * 0.6;
    scrollTo(0, Math.max(0, r.top + scrollY + f * Math.max(0, span) - innerHeight * 0.2));
    sync();
  }
  function keepPlace(fn) {
    var c = currentChapter(), f = fractionIn(c);
    fn();
    goTo(c, f);
  }
  var ticking = false;
  addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      sync();
      clearTimeout(saveT);
      saveT = setTimeout(save, 400);
    });
  }, { passive: true });
  addEventListener("resize", function () { sync(); });

  addEventListener("hashchange", function () {
    var c = chapterFor(location.hash.slice(1));
    if (c) render(c, true);
  });

  addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closePanels(); return; }
    if (!multi || prefs.mode !== "chapter" || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    var t = e.target.tagName;
    if (t === "INPUT" || t === "TEXTAREA" || e.target.isContentEditable) return;
    var n = e.key === "ArrowRight" ? chapters[shown.i + 1] : e.key === "ArrowLeft" ? chapters[shown.i - 1] : null;
    if (n) { e.preventDefault(); location.hash = n.id; }
  });

  /* ---- start ---- */
  document.documentElement.classList.add("rd-on");
  applyPrefs();
  var hashC = chapterFor(location.hash.slice(1));
  var saved = store.get("tz-read:" + slug, null);
  if (hashC) {
    render(hashC, false);
    var t = document.getElementById(location.hash.slice(1));
    if (t) t.scrollIntoView();
  } else if (saved && saved.done > 0.01 && saved.done < 0.995) {
    var sc = chapterFor(saved.id) || chapters[0];
    goTo(sc, saved.f || 0);
    var toast = el("div", { "class": "rd-toast", role: "status" });
    toast.appendChild(document.createTextNode("Picked up where you left off" + (multi ? " in " + sc.title : "") + ". "));
    var restart = el("button", { type: "button" }, "Start from the beginning");
    restart.addEventListener("click", function () {
      toast.remove();
      render(chapters[0], false);
      scrollTo(0, 0);
      save();
    });
    toast.appendChild(restart);
    document.body.appendChild(toast);
    setTimeout(function () { toast.classList.add("is-gone"); }, 7000);
  } else {
    render(chapters[0], false);
  }
})();
