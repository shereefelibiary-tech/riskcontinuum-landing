// Contact and feedback forms for the public site. Messages go to the RCCKM app
// (app.riskcontinuum.health/api/messages), which stores them for the team to read.
// No cookies are sent. If sending fails, the visitor is pointed to the email address.
(function () {
  var ENDPOINT = "https://app.riskcontinuum.health/api/messages";
  var EMAIL = "shereef@riskcontinuum.health";
  var FALLBACK = "Your message could not be sent. Please email " + EMAIL + ".";

  var css = [
    ".msg-form{display:grid;gap:12px;margin-top:14px;text-align:left}",
    ".msg-form label{display:grid;gap:5px;font-size:14px;font-weight:600;color:var(--ink,#1D1416)}",
    ".msg-form label em{font-style:normal;font-weight:400;color:var(--muted,#6F6064)}",
    ".msg-form input:not(.hp),.msg-form textarea{font:inherit;font-size:16px;font-weight:400;color:var(--ink,#1D1416);background:var(--surface,#fff);border:1px solid var(--line-2,#DDD0CF);border-radius:12px;padding:10px 12px;width:100%}",
    ".msg-form textarea{resize:vertical;min-height:96px}",
    ".msg-form input:focus-visible,.msg-form textarea:focus-visible{outline:2px solid var(--accent,#861327);outline-offset:1px;border-color:transparent}",
    ".msg-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}",
    "@media (max-width:640px){.msg-row{grid-template-columns:1fr}}",
    ".msg-note{font-size:13.5px;color:var(--muted,#6F6064);margin:0}",
    ".msg-foot{display:flex;align-items:center;justify-content:flex-end;gap:12px;flex-wrap:wrap}",
    ".msg-status{font-size:14px;color:var(--accent,#861327);margin:0 auto 0 0}",
    ".msg-form button[type=submit]{display:inline-flex;align-items:center;font:inherit;font-weight:600;font-size:15px;border:0;border-radius:999px;padding:11px 22px;background:var(--accent,#861327);color:#fff;cursor:pointer}",
    ".msg-form button[type=submit]:disabled{opacity:.6;cursor:default}",
    ".msg-done{margin-top:14px;font-size:16px;color:var(--ink,#1D1416)}",
    ".hp{position:absolute;left:-10000px;width:1px;height:1px;opacity:0}",
    ".msg-rating{border:0;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:6px}",
    ".msg-rating legend{font-size:14px;font-weight:600;margin-bottom:6px;width:100%;color:var(--ink,#1D1416)}",
    ".msg-rating legend em{font-style:normal;font-weight:400;color:var(--muted,#6F6064)}",
    ".msg-rating button{width:40px;height:40px;border-radius:999px;border:1px solid var(--line-2,#DDD0CF);background:#fff;font:inherit;font-weight:600;cursor:pointer;color:var(--ink,#1D1416)}",
    ".msg-rating button[aria-pressed=true]{background:var(--accent,#861327);border-color:var(--accent,#861327);color:#fff}",
    "dialog.msg-dialog{margin:auto;max-height:calc(100vh - 32px);overflow:auto;width:min(520px,calc(100vw - 32px));border:1px solid var(--line,#ECE4E3);border-radius:20px;padding:24px;background:#fff;color:var(--ink,#1D1416);box-shadow:0 30px 80px -30px rgba(45,12,20,.4)}",
    "dialog.msg-dialog::backdrop{background:rgba(29,20,22,.45)}",
    "dialog.msg-dialog h2{font-family:var(--display,'Jost',sans-serif);font-weight:500;font-size:24px;margin:0 0 4px}",
    ".msg-close{position:absolute;top:12px;right:14px;border:0;background:none;font-size:22px;line-height:1;cursor:pointer;color:var(--muted,#6F6064)}"
  ].join("");
  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  function send(form, payload, done) {
    var status = form.querySelector(".msg-status");
    var button = form.querySelector("button[type=submit]");
    status.textContent = "";
    button.disabled = true;
    button.textContent = "Sending…";
    fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), credentials: "omit", cache: "no-store" })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { return { ok: r.ok, status: r.status, body: b }; }); })
      .then(function (res) {
        if (res.ok) { done(); return; }
        status.textContent = res.status === 400 && res.body.detail ? res.body.detail : (res.body.detail || FALLBACK);
        button.disabled = false; button.textContent = "Send";
      })
      .catch(function () { status.textContent = FALLBACK; button.disabled = false; button.textContent = "Send"; });
  }

  function value(form, name) { var el = form.elements[name]; return el ? String(el.value || "").trim() : ""; }

  function bind(form, extra) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".msg-status");
      var message = value(form, "message");
      var email = value(form, "email");
      if (!message) { status.textContent = "Please write a message."; form.elements.message.focus(); return; }
      if (form.dataset.kind === "contact" && !email) { status.textContent = "Please enter your email address so we can reply."; form.elements.email.focus(); return; }
      if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { status.textContent = "Please enter a valid email address."; form.elements.email.focus(); return; }
      var payload = { kind: form.dataset.kind, message: message, email: email, name: value(form, "name"), organization: value(form, "organization"),
        page: (document.body.dataset.page || location.pathname).slice(0, 120), website: value(form, "website") };
      if (extra) extra(payload);
      send(form, payload, function () {
        var done = document.createElement("p");
        done.className = "msg-done";
        done.setAttribute("role", "status");
        done.textContent = form.dataset.kind === "contact" ? "Thank you. Your message is on its way, and we'll reply by email." : "Thank you for the feedback.";
        form.replaceWith(done);
      });
    });
  }

  document.querySelectorAll("form.msg-form[data-kind]").forEach(function (f) { bind(f); });

  // Feedback dialog, built on first use and opened from any [data-feedback] link.
  var dialog = null;
  function feedbackDialog() {
    if (dialog) return dialog;
    dialog = document.createElement("dialog");
    dialog.className = "msg-dialog";
    dialog.setAttribute("aria-labelledby", "msg-dialog-title");
    dialog.innerHTML =
      '<button type="button" class="msg-close" aria-label="Close">&times;</button>' +
      '<h2 id="msg-dialog-title">Send feedback</h2>' +
      '<p class="msg-note">What works, what doesn’t, or what you’d like to see. <b>Please don’t include patient information.</b></p>' +
      '<form class="msg-form" data-kind="feedback" novalidate>' +
      '<fieldset class="msg-rating"><legend>How useful does RCCKM look? <em>(optional)</em></legend>' +
      [1, 2, 3, 4, 5].map(function (n) { return '<button type="button" data-rating="' + n + '" aria-pressed="false" aria-label="' + n + ' of 5">' + n + "</button>"; }).join("") +
      "</fieldset>" +
      '<label><span>Your feedback</span><textarea name="message" rows="5" maxlength="4000" required></textarea></label>' +
      '<label><span>Email <em>(optional, if you’d like a reply)</em></span><input name="email" type="email" autocomplete="email" maxlength="254"></label>' +
      '<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">' +
      '<div class="msg-foot"><p class="msg-status" role="status" aria-live="polite"></p><button type="submit">Send</button></div>' +
      "</form>";
    document.body.appendChild(dialog);
    var rating = null;
    dialog.querySelectorAll("[data-rating]").forEach(function (b) {
      b.addEventListener("click", function () {
        var n = Number(b.dataset.rating);
        rating = rating === n ? null : n;
        dialog.querySelectorAll("[data-rating]").forEach(function (x) { x.setAttribute("aria-pressed", String(Number(x.dataset.rating) === rating)); });
      });
    });
    dialog.querySelector(".msg-close").addEventListener("click", function () { dialog.close(); });
    bind(dialog.querySelector("form"), function (p) { if (rating) p.rating = rating; });
    return dialog;
  }
  document.addEventListener("click", function (e) {
    var link = e.target instanceof Element ? e.target.closest("[data-feedback]") : null;
    if (!link) return;
    e.preventDefault();
    var d = feedbackDialog();
    if (typeof d.showModal === "function") d.showModal(); else d.setAttribute("open", "");
  });
}());
