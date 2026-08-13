/* Longevity Marathon — shared front-end behavior.
   Minimal vanilla JS: mobile nav toggle, newsletter form (simulated —
   no backend exists yet), and journal filters reflected in the URL
   query string. No framework, no build step. */

(function () {
  "use strict";

  /* ---------- Mobile nav toggle ---------- */
  function initNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.getElementById("site-nav");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    // Close menu when a nav link is activated (mobile)
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- Newsletter form (simulated) ----------
     There is no real subscription backend in this prototype. The form
     validates client-side and shows success/error/already-subscribed
     states so the pattern can be reviewed and later wired to a real
     double opt-in provider (see /privacy and website spec §13.4). */
  function initNewsletterForms() {
    var forms = document.querySelectorAll("[data-newsletter-form]");
    forms.forEach(function (form) {
      var email = form.querySelector('input[type="email"]');
      var status = form.querySelector("[data-form-status]");
      var emailError = form.querySelector("[data-email-error]");

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var value = (email.value || "").trim();
        var valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);

        if (!valid) {
          if (emailError) {
            emailError.textContent = value
              ? "That doesn't look like a complete email address."
              : "Enter an email address to subscribe.";
            emailError.classList.add("is-visible");
          }
          email.setAttribute("aria-invalid", "true");
          if (status) {
            status.className = "form-status";
            status.textContent = "";
          }
          email.focus();
          return;
        }

        if (emailError) emailError.classList.remove("is-visible");
        email.removeAttribute("aria-invalid");

        // Simulate a network round trip and a known "already subscribed" demo address.
        if (status) {
          status.className = "form-status is-visible";
          status.textContent = "Sending…";
        }
        window.setTimeout(function () {
          if (!status) return;
          if (value.toLowerCase() === "already@subscribed.demo") {
            status.className = "form-status is-visible form-status--error";
            status.textContent =
              "That address is already subscribed. Check your inbox for the most recent entry, or look for a confirmation email from your first signup.";
          } else {
            status.className = "form-status is-visible form-status--success";
            status.textContent =
              "Almost there — check " + value + " for a confirmation email. Nothing gets sent to the list until you confirm.";
            form.reset();
          }
        }, 500);
      });
    });
  }

  /* ---------- Journal filters, reflected in the URL query string ---------- */
  function initJournalFilters() {
    var root = document.querySelector("[data-journal-filters]");
    if (!root) return;
    var cards = Array.prototype.slice.call(document.querySelectorAll("[data-entry-card]"));
    var chips = Array.prototype.slice.call(root.querySelectorAll(".chip"));
    var resetBtn = root.querySelector("[data-filters-reset]");
    var emptyState = document.querySelector("[data-journal-empty]");
    var countEl = document.querySelector("[data-journal-count]");

    function currentParams() {
      return new URLSearchParams(window.location.search);
    }

    function activeFilters() {
      var params = currentParams();
      return {
        type: params.get("type") || "all",
        topic: params.get("topic") || "all",
        phase: params.get("phase") || "all"
      };
    }

    function applyChipsFromURL() {
      var active = activeFilters();
      chips.forEach(function (chip) {
        var group = chip.getAttribute("data-filter-group");
        var val = chip.getAttribute("data-filter-value");
        var isActive = active[group] === val;
        chip.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }

    function render() {
      var active = activeFilters();
      var visibleCount = 0;
      cards.forEach(function (card) {
        var type = card.getAttribute("data-type");
        var topics = (card.getAttribute("data-topics") || "").split(",");
        var phase = card.getAttribute("data-phase");
        var matches =
          (active.type === "all" || active.type === type) &&
          (active.topic === "all" || topics.indexOf(active.topic) !== -1) &&
          (active.phase === "all" || active.phase === phase);
        card.style.display = matches ? "" : "none";
        if (matches) visibleCount++;
      });
      if (emptyState) emptyState.style.display = visibleCount === 0 ? "" : "none";
      if (countEl) {
        countEl.textContent =
          visibleCount === cards.length
            ? "Showing all " + cards.length + " entries."
            : "Showing " + visibleCount + " of " + cards.length + " entries.";
      }
      applyChipsFromURL();
    }

    function setParam(group, value) {
      var params = currentParams();
      if (value === "all") {
        params.delete(group);
      } else {
        params.set(group, value);
      }
      var qs = params.toString();
      var newUrl = window.location.pathname + (qs ? "?" + qs : "");
      window.history.replaceState(null, "", newUrl);
      render();
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        var group = chip.getAttribute("data-filter-group");
        var val = chip.getAttribute("data-filter-value");
        var alreadyActive = chip.getAttribute("aria-pressed") === "true";
        setParam(group, alreadyActive ? "all" : val);
      });
    });

    if (resetBtn) {
      resetBtn.addEventListener("click", function () {
        window.history.replaceState(null, "", window.location.pathname);
        render();
      });
    }

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initNav();
    initNewsletterForms();
    initJournalFilters();
  });
})();
