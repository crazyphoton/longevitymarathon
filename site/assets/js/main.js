/* Longevity Marathon — shared front-end behavior.
   Minimal vanilla JS: mobile nav toggle, newsletter form (double opt-in
   via a Supabase Edge Function + Resend, see spec §13.4), and journal
   filters reflected in the URL query string. No framework, no build step. */

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

  /* ---------- Newsletter form (double opt-in) ----------
     Posts to a Supabase Edge Function which stores the pending subscriber
     and sends a confirmation email via Resend. Nothing is sent to the list
     until the reader confirms (see /privacy and website spec §13.4). */
  var SUBSCRIBE_URL =
    "https://hwquutezbptpuppilvgq.supabase.co/functions/v1/newsletter/subscribe";

  function initNewsletterForms() {
    var forms = document.querySelectorAll("[data-newsletter-form]");
    forms.forEach(function (form) {
      var email = form.querySelector('input[type="email"]');
      var status = form.querySelector("[data-form-status]");
      var emailError = form.querySelector("[data-email-error]");
      var submitBtn = form.querySelector('button[type="submit"], button:not([type])');

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

        if (status) {
          status.className = "form-status is-visible";
          status.textContent = "Sending…";
        }
        if (submitBtn) submitBtn.disabled = true;

        var firstNameInput = form.querySelector('input[name="first_name"]');
        var sourceInput = form.querySelector('input[name="source"]');
        var honeypot = form.querySelector('input[name="website"]');

        fetch(SUBSCRIBE_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: value,
            first_name: firstNameInput ? firstNameInput.value : "",
            source: sourceInput ? sourceInput.value : "",
            website: honeypot ? honeypot.value : ""
          })
        })
          .then(function (resp) {
            return resp.json().then(function (body) {
              return { ok: resp.ok, body: body };
            });
          })
          .then(function (result) {
            if (!status) return;
            if (result.ok) {
              status.className = "form-status is-visible form-status--success";
              status.textContent =
                "Almost there — check " + value + " for a confirmation email. Nothing gets sent to the list until you confirm.";
              form.reset();
            } else {
              status.className = "form-status is-visible form-status--error";
              status.textContent =
                (result.body && result.body.error) ||
                "Something went wrong on our side. Please try again.";
            }
          })
          .catch(function () {
            if (!status) return;
            status.className = "form-status is-visible form-status--error";
            status.textContent =
              "Couldn't reach the subscription service. Check your connection and try again — your place on this page is safe.";
          })
          .then(function () {
            if (submitBtn) submitBtn.disabled = false;
          });
      });
    });
  }

  /* ---------- Confirm/unsubscribe landing states ----------
     The Edge Function redirects back to /newsletter/?state=… after a
     reader clicks a confirmation or unsubscribe link. */
  function initNewsletterState() {
    var state = new URLSearchParams(window.location.search).get("state");
    if (!state) return;
    var status = document.querySelector("[data-form-status]");
    if (!status) return;
    var messages = {
      confirmed:
        "Subscription confirmed — you're on the list. New entries and meaningful data updates will land in your inbox.",
      unsubscribed:
        "You've been unsubscribed. No further emails will be sent to your address.",
      invalid:
        "That link is invalid or was already used. If you were trying to subscribe, submit the form again for a fresh confirmation email."
    };
    if (!messages[state]) return;
    status.className =
      "form-status is-visible " +
      (state === "invalid" ? "form-status--error" : "form-status--success");
    status.textContent = messages[state];
    status.scrollIntoView({ block: "center" });
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
    initNewsletterState();
    initJournalFilters();
  });
})();
