/* Explicit public-site analytics. No form values, DOM text, full URLs or clinical data. */
(function () {
  "use strict";
  var endpoint = "https://app.riskcontinuum.health/api/analytics/landing";
  var paths = { "/": "landing", "/landing.html": "landing", "/privacy.html": "privacy", "/terms.html": "terms" };
  var page = paths[location.pathname];
  if (!page || !crypto.randomUUID) return;
  var enabled = false, queue = [], timer, source = {}, internal = false;
  var started = performance.now(), visible = 0, active = !document.hidden, depth = 0, reported = false;
  var sourceNames = ["linkedin","email","qr","google","bing","facebook","instagram","x","twitter","aha","acc","usc","bonsecours","direct","other"];
  var mediumNames = ["social","organic","email","referral","qr","cpc","paid_social","direct","other"];
  var query = new URLSearchParams(location.search);
  ["utm_source", "utm_medium"].forEach(function (key) {
    var value = query.get(key); if (value) { value = value.toLowerCase(); source[key] = (key === "utm_source" ? sourceNames : mediumNames).indexOf(value) >= 0 ? value : "other"; }
  });
  try { var ref = new URL(document.referrer); if (/^https?:$/.test(ref.protocol) && /^(?:[a-z0-9-]+\.)+[a-z]{2,63}$/i.test(ref.hostname)) source.referrer_domain = ref.hostname.toLowerCase(); } catch (_) {}
  try { internal = localStorage.getItem("rcckm:analytics-internal-test") === "true"; } catch (_) {}
  function track(name, properties) {
    if (queue.length >= 40) return;
    queue.push({ event: "nextjs_" + name, properties: properties || {}, uuid: crypto.randomUUID() });
    if (enabled && !timer) timer = setTimeout(function () { timer = undefined; flush(); }, 500);
  }
  function flush() {
    if (!enabled || !queue.length) return;
    var events = queue.splice(0, 20);
    var body = JSON.stringify({ events: events, internal_test: internal, device_category: innerWidth < 600 ? "mobile" : innerWidth < 1024 ? "tablet" : "desktop", acquisition: source });
    // text/plain avoids preflight on unload; the collector validates JSON and the exact site origin.
    fetch(endpoint, { method: "POST", credentials: "include", headers: { "Content-Type": "text/plain" }, body: body, keepalive: true }).catch(function () {});
    if (queue.length) timer = setTimeout(function () { timer = undefined; flush(); }, 500);
  }
  function reportEngagement() {
    if (active) { visible += performance.now() - started; started = performance.now(); }
    if (visible >= 1000) track("page_engaged", { page: page, duration_ms: Math.min(3600000, Math.round(visible / 10) * 10), scroll_percent: depth });
    visible = 0; flush();
  }
  track("page_viewed", { page: page });
  fetch(endpoint, { credentials: "include", cache: "no-store" }).then(function (r) { return r.json(); }).then(function (c) { enabled = c.enabled === true; if (enabled) flush(); else queue = []; }).catch(function () { queue = []; });
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) { reportEngagement(); active = false; }
    else { active = true; started = performance.now(); }
  });
  addEventListener("pagehide", function () { if (!reported) { reported = true; reportEngagement(); } });
  addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - innerHeight;
    depth = Math.max(depth, h <= 0 ? 100 : Math.floor(Math.min(100, Math.max(0, scrollY / h * 100)) / 25) * 25);
  }, { passive: true });
  var sections = ["hero","stats","trajectory","plan","decide","report","demo","how","who","founder","cta","footer"];
  if (typeof IntersectionObserver !== "undefined") {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { if (!entry.isIntersecting) return; var section = entry.target.getAttribute("data-analytics-section"); if (sections.indexOf(section) >= 0) { track("landing_section_viewed", { section: section }); observer.unobserve(entry.target); } });
    }, { threshold: 0.15 });
    document.querySelectorAll("[data-analytics-section]").forEach(function (node) { observer.observe(node); });
  }
  document.addEventListener("click", function (e) {
    var node = e.target instanceof Element ? e.target.closest("a,button,[role=tab],input[type=range]") : null;
    if (!node) return;
    var action = node.tagName === "A" ? "link" : "button";
    if (node instanceof HTMLAnchorElement) {
      try {
        var url = new URL(node.getAttribute("href") || "", location.origin);
        if (url.protocol === "mailto:") action = "contact";
        else if (url.hostname === "app.riskcontinuum.health") action = url.pathname === "/sign-up" ? "sign_up" : url.pathname === "/sign-in" ? "sign_in" : "open_app";
        else if (url.pathname === "/privacy.html") action = "privacy";
        else if (url.pathname === "/terms.html") action = "terms";
        else if (url.origin === location.origin && url.hash) action = "navigate";
      } catch (_) {}
    } else if (node.closest(".plan,.demo")) action = "demo";
    track("ui_action", { page: page, action: action });
    flush();
  }, true);
  var errors = 0;
  function reportError(value, kind) {
    if (++errors > 20) return;
    var type = value instanceof Error && ["Error","TypeError","RangeError","ReferenceError","SyntaxError","URIError","EvalError","AggregateError"].indexOf(value.name) >= 0 ? value.name : "Other";
    track("runtime_error", { page: page, kind: kind, error_type: type }); flush();
  }
  addEventListener("error", function (e) { reportError(e.error, e instanceof ErrorEvent ? "error" : "resource"); }, true);
  addEventListener("unhandledrejection", function (e) { reportError(e.reason, "unhandled_rejection"); });
}());
