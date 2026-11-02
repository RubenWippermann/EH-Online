/* Hero-Loop (KI-generiert): nur Desktop (min-width 1024px, hover:hover), erst nach window load,
   nicht bei prefers-reduced-motion, saveData oder 2g. Poster bleibt sonst stehen. Stumm, Pause-Knopf. */
(function () {
  var box = document.querySelector(".hero-media");
  if (!box) return;
  var v = box.querySelector("video"), btn = box.querySelector(".hero-media-pause");
  if (!v || !btn) return;
  var c = navigator.connection || {};
  if (c.saveData || /(^|slow-)2g$/.test(c.effectiveType || "")) return;
  var mq = function (q) { return window.matchMedia && window.matchMedia(q).matches; };
  if (!mq("(min-width:1024px) and (hover:hover)") || mq("(prefers-reduced-motion:reduce)")) return;
  function start() {
    v.muted = true;
    v.src = v.getAttribute("data-src");
    v.addEventListener("playing", function () { v.hidden = false; btn.hidden = false; }, { once: true });
    var p = v.play();
    if (p && p.catch) p.catch(function () { v.removeAttribute("src"); v.load(); });
  }
  btn.addEventListener("click", function () {
    if (v.paused) { v.play(); btn.setAttribute("aria-label", "Video pausieren"); btn.setAttribute("data-state", "play"); }
    else { v.pause(); btn.setAttribute("aria-label", "Video abspielen"); btn.setAttribute("data-state", "pause"); }
  });
  if (document.readyState === "complete") start(); else window.addEventListener("load", start, { once: true });
})();
