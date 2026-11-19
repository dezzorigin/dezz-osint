// dezz-osint landing — tab terminal + tombol salin. Tanpa dependensi.
(function () {
  "use strict";

  // ── Tab terminal ──────────────────────────────────────────────────────
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".term-tabs [role='tab']"));
  var panels = {};
  tabs.forEach(function (tab) {
    panels[tab.dataset.tab] = document.getElementById("term-" + tab.dataset.tab);
  });
  var commands = {
    ip: 'dezz ip 8.8.8.8',
    github: 'dezz github torvalds',
    resources: 'dezz resources "sherlock" --limit 5',
    sf: 'dezz sf --search dns'
  };
  var active = "ip";

  function select(name) {
    active = name;
    tabs.forEach(function (tab) {
      var on = tab.dataset.tab === name;
      tab.setAttribute("aria-selected", on ? "true" : "false");
      panels[tab.dataset.tab].hidden = !on;
    });
  }
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () { select(tab.dataset.tab); });
  });

  // ── Salin ke clipboard (dengan fallback) ──────────────────────────────
  function copyText(text, noteEl) {
    function done() {
      if (noteEl) noteEl.textContent = "Disalin ke clipboard.";
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    } else {
      fallback();
    }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) { /* diam */ }
      document.body.removeChild(ta);
    }
  }

  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var note = btn.parentElement.querySelector(".copy-note");
      copyText(btn.getAttribute("data-copy"), note);
    });
  });

  var copyCmd = document.getElementById("copy-cmd");
  if (copyCmd) {
    copyCmd.addEventListener("click", function () {
      copyText(commands[active], null);
      copyCmd.textContent = "Disalin.";
      setTimeout(function () { copyCmd.textContent = "Salin perintah aktif"; }, 2000);
    });
  }
})();
