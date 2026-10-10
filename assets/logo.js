/* hice logo: the dot bounces across the word, each letter grows out of the floor where it lands,
   then the dot jumps onto the dotless i and floats. Adapted from logo.html.
   Markup: <span class="mark"><span class="word"><span class="l">h</span><span class="l" data-dotless>ı</span>…</span>
           <i class="mark-dot"><span class="dot-float"><span class="dot-core"></span></span></i></span>
   A mark with [data-intro] plays the intro; every other mark just places the dot on the i. */
(function () {
  "use strict";
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ctx = document.createElement("canvas").getContext("2d");
  function easeInOutCubic(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

  function metrics(mark) {
    var wr = mark.getBoundingClientRect();
    var cs = getComputedStyle(mark);
    var fs = parseFloat(cs.fontSize), lh = parseFloat(cs.lineHeight);
    if (!(wr.width > 0) || isNaN(lh)) return null;
    ctx.font = cs.fontWeight + " " + fs + "px " + cs.fontFamily;
    var A = ctx.measureText("Ï").actualBoundingBoxAscent;
    var D = ctx.measureText("y").actualBoundingBoxDescent;
    var baselineY = wr.top + (lh - (A + D)) / 2 + A;
    var iEl = $(".l[data-dotless]", mark), ir = iEl.getBoundingClientRect();
    var tittleTop = baselineY - ctx.measureText("i").actualBoundingBoxAscent;
    var tittleBottom = baselineY - ctx.measureText("ı").actualBoundingBoxAscent;
    var tittleH = tittleBottom - tittleTop;
    var word = $(".word", mark), wordR = word.getBoundingClientRect();
    return {
      fs: fs, baselineY: baselineY - wr.top, wordTop: wordR.top - wr.top, wordH: wordR.height,
      tittleX: ir.left + ir.width / 2 - wr.left,
      tittleY: (tittleTop + tittleBottom) / 2 - wr.top - 0.14 * fs,
      tittleH: tittleH,
      letters: $$(".l", mark).map(function (el) {
        var r = el.getBoundingClientRect();
        return { el: el, left: r.left - wr.left, right: r.right - wr.left, cx: r.left + r.width / 2 - wr.left, baseInEl: baselineY - r.top };
      })
    };
  }

  function sizeDot(mark, m) {
    var dot = $(".mark-dot", mark), s = m.tittleH * 0.367;
    dot.style.width = dot.style.height = s + "px";
    return { dot: dot, size: s };
  }

  /* static state: letters visible, dot resting (and floating) on the i */
  function place(mark) {
    var m = metrics(mark); if (!m) return;
    var d = sizeDot(mark, m);
    d.dot.style.transform = "translate(" + (m.tittleX - d.size / 2) + "px," + (m.tittleY - d.size / 2) + "px)";
    d.dot.style.opacity = 1;
    $(".dot-core", mark).style.transform = "scale(1.5)";
    mark.classList.add("is-idle");
  }

  function popLetter(L) {
    L.el.style.transformOrigin = "50% " + L.baseInEl + "px";
    L.el.animate([
      { opacity: 0, transform: "translateY(.8em) scale(.55, .9)", offset: 0 },
      { opacity: 1, transform: "translateY(.55em) scale(.7, 1)", offset: .12 },
      { transform: "translateY(-.07em) scale(.94, 1.08)", offset: .58 },
      { transform: "translateY(.015em) scale(1.04, .96)", offset: .8 },
      { opacity: 1, transform: "translateY(0) scale(1, 1)", offset: 1 }
    ], { duration: 760, easing: "cubic-bezier(.25,.8,.3,1)", fill: "forwards" });
  }

  function splashAt(mark, x, y, fs) {
    var s = document.createElement("span");
    s.className = "splash"; s.style.left = x + "px"; s.style.top = y + "px";
    mark.appendChild(s);
    s.animate([{ transform: "scale(.3, .5)", opacity: .85 }, { transform: "scale(2.2, 1.4)", opacity: 0 }],
      { duration: 650, easing: "cubic-bezier(.2,.8,.2,1)" }).onfinish = function () { s.remove(); };
    for (var i = 0; i < 5; i++) {
      var p = document.createElement("span");
      p.className = "spark"; p.style.left = x + "px"; p.style.top = y + "px";
      mark.appendChild(p);
      var ang = Math.PI * (0.12 + 0.76 * (i / 4)) + (Math.random() - .5) * 0.25;
      var dist = fs * (0.16 + Math.random() * 0.12), dx = -Math.cos(ang) * dist, dy = -Math.sin(ang) * dist;
      p.animate([
        { transform: "translate(0,0) scale(1)", opacity: 1 },
        { transform: "translate(" + dx + "px," + dy + "px) scale(.8)", opacity: .9, offset: .55 },
        { transform: "translate(" + dx * 1.3 + "px," + (dy * 0.6 + fs * .06) + "px) scale(.3)", opacity: 0 }
      ], { duration: 520 + Math.random() * 160, easing: "cubic-bezier(.2,.7,.4,1)" }).onfinish = (function (el) { return function () { el.remove(); }; })(p);
    }
  }

  function intro(mark, done) {
    var m = metrics(mark); if (!m) { done(); return; }
    var word = $(".word", mark), d = sizeDot(mark, m), dot = d.dot, dotR = d.size / 2, core = $(".dot-core", mark);
    mark.removeAttribute("data-intro");
    mark.classList.remove("is-idle");
    $$(".l", mark).forEach(function (el) { el.style.opacity = 0; });
    var floor = (m.wordTop + m.wordH) - m.baselineY - 0.025 * m.fs;
    word.style.clipPath = "inset(-50% -50% " + Math.max(0, floor) + "px -50%)";
    core.style.transform = "scale(1)";
    dot.style.opacity = 1;

    var L = m.letters, k = L.length;
    var startX = L[0].left - 0.18 * m.fs, groundY = m.baselineY - dotR;
    var bounceH = 0.96 * m.fs, arcH = 0.585 * m.fs;
    var endX = L[k - 1].right + 0.06 * m.fs + dotR;
    var xs = [startX].concat(L.map(function (l) { return l.cx; }), [endX]);
    var hops = xs.length - 1, hopT = 2250 / k;
    var T = { bounce: hopT * hops, pause: 900, arc: 975, settle: 500 };
    var total = T.bounce + T.pause + T.arc, lastX = endX, triggered = 0;

    function triggerUpTo(n) { while (triggered < n) { popLetter(L[triggered]); splashAt(mark, L[triggered].cx, m.baselineY, m.fs); triggered++; } }
    function put(cx, cy, sx, sy) { dot.style.transform = "translate(" + (cx - dotR) + "px," + (cy - dotR) + "px) scale(" + sx + "," + sy + ")"; }
    put(startX, groundY, 1, 1);

    var t0 = null;
    function tick(now) {
      if (t0 === null) t0 = now;
      var t = now - t0;
      if (t <= T.bounce) {
        var i = Math.min(hops - 1, Math.floor(t / hopT)), u = Math.min(1, (t - i * hopT) / hopT);
        var s = Math.sin(Math.PI * u), h = i === hops - 1 ? bounceH * 0.45 : bounceH * (1 - 0.1 * i);
        put(xs[i] + (xs[i + 1] - xs[i]) * u, groundY - h * s, 1.30 - 0.40 * s, 0.70 + 0.40 * s);
        triggerUpTo(Math.min(k, Math.floor(t / hopT + 1e-6)));
      } else if (t <= T.bounce + T.pause) {
        triggerUpTo(k);
        var settle = Math.min(1, (t - T.bounce) / T.pause / 0.4);
        put(lastX, groundY, 1.30 - 0.30 * settle, 0.70 + 0.30 * settle);
      } else if (t <= total) {
        var eu = easeInOutCubic((t - T.bounce - T.pause) / T.arc);
        put(lastX + (m.tittleX - lastX) * eu, groundY + (m.tittleY - groundY) * eu - arcH * 4 * eu * (1 - eu), 1, 1);
      } else if (t <= total + T.settle) {
        var sq = Math.sin(Math.PI * (t - total) / T.settle);
        put(m.tittleX, m.tittleY, 1 + 0.25 * sq, 1 - 0.25 * sq);
      } else {
        put(m.tittleX, m.tittleY, 1, 1);
        mark.classList.add("is-idle");
        core.animate([{ transform: "scale(1)" }, { transform: "scale(1.5)" }], { duration: 1200, easing: "cubic-bezier(.33,1,.68,1)", fill: "forwards" });
        word.style.clipPath = "none";
        done();
        return;
      }
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    setTimeout(function () { word.style.clipPath = "none"; }, hopT * k + 900);
  }

  function seenIntro() { try { return sessionStorage.getItem("hice-logo-intro") === "1"; } catch (e) { return false; } }
  function markSeen() { try { sessionStorage.setItem("hice-logo-intro", "1"); } catch (e) {} }

  function start() {
    var marks = $$(".logo .mark");
    var home = !!$("#top.hero");
    var playing = new Set();
    marks.forEach(function (mark) {
      var animate = mark.hasAttribute("data-intro") && !reduced && (home || !seenIntro());
      if (!animate) mark.removeAttribute("data-intro");
      if (typeof ResizeObserver === "function") {
        new ResizeObserver(function () { if (!playing.has(mark)) place(mark); }).observe(mark);
      }
      if (animate) {
        playing.add(mark); markSeen();
        intro(mark, function () { playing.delete(mark); });
      } else place(mark);
    });
  }

  var fontsReady = document.fonts && document.fonts.load
    ? document.fonts.load('400 24px "Momo Trust Display"').then(function () { return document.fonts.ready; })
    : Promise.resolve();
  fontsReady.catch(function () {}).then(start);
})();
