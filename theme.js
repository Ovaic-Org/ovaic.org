/* OVAIC light / dark switch. Follows the device until the visitor chooses; the choice is remembered on this device. */
(function () {
  var KEY = "ovaic-theme", root = document.documentElement;
  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  var t = saved(); if (t) root.setAttribute("data-theme", t);
  function dark() { var a = root.getAttribute("data-theme"); return a ? a === "dark" : matchMedia("(prefers-color-scheme: dark)").matches; }
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>';
  function label(b) { var d = dark(); b.innerHTML = d ? SUN : MOON; b.setAttribute("aria-label", d ? "Light mode" : "Dark mode"); b.title = b.getAttribute("aria-label"); }
  document.addEventListener("DOMContentLoaded", function () {
    var b = document.createElement("button"); b.type = "button"; b.className = "theme-toggle"; label(b);
    b.addEventListener("click", function () { var n = dark() ? "light" : "dark"; root.setAttribute("data-theme", n);
      try { localStorage.setItem(KEY, n); } catch (e) {} label(b); });
    document.body.appendChild(b);
  });
})();
