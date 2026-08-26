(function() {
    "use strict";
    var KEY = "ehk-consent";
    var MAXAGE = 60 * 60 * 24 * 365;
    function get() {
        try {
            return localStorage.getItem(KEY);
        } catch (e) {}
        var m = /(?:^|;\s*)ehk_consent=([^;]+)/.exec(document.cookie);
        return m ? decodeURIComponent(m[1]) : null;
    }
    function set(v) {
        try {
            localStorage.setItem(KEY, v);
        } catch (e) {}
        document.cookie = "ehk_consent=" + encodeURIComponent(v) + ";max-age=" + MAXAGE + ";path=/;samesite=lax";
    }
    var banner = document.querySelector("[data-cc-banner]");
    function openBanner() {
        if (banner) {
            banner.hidden = false;
            document.body.classList.add("cc-open");
        }
    }
    function closeBanner() {
        if (banner) {
            banner.hidden = true;
            document.body.classList.remove("cc-open");
        }
    }
    function enableMarketing() {
        document.documentElement.setAttribute("data-consent", "marketing");
        Array.prototype.forEach.call(document.querySelectorAll("[data-ad-consent]"), function(el) {
            el.classList.add("consented");
        });
    }
    function apply(v) {
        if (v === "accept") enableMarketing(); else document.documentElement.setAttribute("data-consent", "essential");
    }
    function choose(v) {
        set(v);
        apply(v);
        closeBanner();
    }
    function boot() {
        if (banner) {
            var a = banner.querySelector('[data-cc="accept"]');
            var r = banner.querySelector('[data-cc="reject"]');
            if (a) a.addEventListener("click", function() {
                choose("accept");
            });
            if (r) r.addEventListener("click", function() {
                choose("reject");
            });
        }
        Array.prototype.forEach.call(document.querySelectorAll("[data-cookie-settings]"), function(b) {
            b.addEventListener("click", function(e) {
                e.preventDefault();
                openBanner();
            });
        });
        var cur = get();
        if (cur === "accept" || cur === "reject") {
            apply(cur);
        } else {
            openBanner();
        }
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
