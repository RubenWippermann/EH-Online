(function() {
    "use strict";
    try {
        var saved = localStorage.getItem("ehd-theme");
        if (saved === "dark" || saved === "light") document.documentElement.setAttribute("data-theme", saved);
    } catch (e) {}
    function toggleTheme() {
        var cur = document.documentElement.getAttribute("data-theme") || "light";
        var next = cur === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        try {
            localStorage.setItem("ehd-theme", next);
        } catch (e) {}
    }
    function initNav() {
        var btn = document.querySelector(".menu-toggle");
        if (btn) {
            btn.addEventListener("click", function() {
                var open = document.body.classList.toggle("menu-open");
                btn.setAttribute("aria-expanded", open ? "true" : "false");
                btn.setAttribute("aria-label", open ? "Menü schließen" : "Menü öffnen");
            });
            Array.prototype.forEach.call(document.querySelectorAll(".nav-links a"), function(a) {
                a.addEventListener("click", function() {
                    document.body.classList.remove("menu-open");
                    btn.setAttribute("aria-expanded", "false");
                });
            });
            document.addEventListener("keydown", function(e) {
                if (e.key === "Escape") {
                    document.body.classList.remove("menu-open");
                    btn.setAttribute("aria-expanded", "false");
                }
            });
        }
        var hdr = document.querySelector(".site-header");
        if (hdr) {
            var onScroll = function() {
                hdr.classList.toggle("is-stuck", window.scrollY > 6);
            };
            onScroll();
            window.addEventListener("scroll", onScroll, {
                passive: true
            });
        }
        Array.prototype.forEach.call(document.querySelectorAll("[data-theme-toggle]"), function(b) {
            b.addEventListener("click", toggleTheme);
        });
    }
    function initReveal() {
        var els = document.querySelectorAll(".rv");
        if (!els.length) return;
        if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            Array.prototype.forEach.call(els, function(el) {
                el.classList.add("in");
            });
            return;
        }
        var io = new IntersectionObserver(function(entries) {
            entries.forEach(function(en) {
                if (!en.isIntersecting) return;
                en.target.classList.add("in");
                io.unobserve(en.target);
            });
        }, {
            rootMargin: "0px 0px -8% 0px",
            threshold: .06
        });
        Array.prototype.forEach.call(els, function(el, i) {
            el.style.transitionDelay = Math.min(i % 4, 3) * 70 + "ms";
            io.observe(el);
        });
        setTimeout(function() {
            Array.prototype.forEach.call(els, function(el) {
                if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add("in");
            });
        }, 2500);
    }
    function initKoop() {
        var box = document.getElementById("koopHinweis");
        if (!box) return;
        var boxes = document.querySelectorAll('input[name="kurse"][data-traeger]');
        if (!boxes.length) return;
        function sync() {
            var bww = false;
            Array.prototype.forEach.call(boxes, function(b) {
                if (b.checked && b.getAttribute("data-traeger") === "bww") bww = true;
            });
            box.hidden = !bww;
        }
        Array.prototype.forEach.call(boxes, function(b) {
            b.addEventListener("change", sync);
        });
        sync();
    }
    function initYear() {
        var y = String((new Date).getFullYear());
        Array.prototype.forEach.call(document.querySelectorAll("[data-year]"), function(el) {
            el.textContent = y;
        });
    }
    function initAnchorFocus() {
        if (!location.hash) return;
        var t = document.getElementById(location.hash.slice(1));
        if (t) setTimeout(function() {
            t.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }, 120);
    }
    function boot() {
        initNav();
        initReveal();
        initKoop();
        initYear();
        initAnchorFocus();
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
