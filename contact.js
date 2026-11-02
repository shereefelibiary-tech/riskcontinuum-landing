// Email links: still open the visitor's mail app, and also copy the address with a short notice,
// because a mailto: link does nothing on computers without a default mail app (common with webmail).
(function () {
  var toast, timer;
  function notify(text) {
    if (!toast) {
      toast = document.createElement("div");
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      toast.style.cssText = "position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:1000;" +
        "width:max-content;max-width:calc(100% - 32px);background:#1D1416;color:#fff;" +
        "font:500 15px/1.45 'Instrument Sans',system-ui,-apple-system,'Segoe UI',sans-serif;" +
        "padding:12px 18px;border-radius:12px;box-shadow:0 14px 34px -12px rgba(0,0,0,.45);" +
        "text-align:center;opacity:0;transition:opacity .25s";
      document.body.appendChild(toast);
    }
    toast.textContent = text;
    toast.style.opacity = "1";
    clearTimeout(timer);
    timer = setTimeout(function () { toast.style.opacity = "0"; }, 6000);
  }
  document.addEventListener("click", function (e) {
    var link = e.target instanceof Element ? e.target.closest('a[href^="mailto:"]') : null;
    if (!link) return;
    var address = decodeURIComponent(link.getAttribute("href").slice(7).split("?")[0]);
    var copied = "Email address copied: " + address + ". If your mail app didn’t open, paste it into a new email.";
    var shown = "Email: " + address;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(address).then(function () { notify(copied); }, function () { notify(shown); });
      } else {
        notify(shown);
      }
    } catch (_) {
      notify(shown);
    }
  });
}());
