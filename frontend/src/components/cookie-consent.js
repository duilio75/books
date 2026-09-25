// Cookie banner and preferences (GDPR + ePrivacy Directive).
//
// Optional scripts must be written as inert blocks, tagged with the category
// that has to be granted before they run:
//   <script type="text/plain" data-cookie-category="analytics" src="..."></script>
// They are activated on load when already granted, or as soon as the visitor
// grants the category. Server-side, templates can check
// {% if cookie_consent.granted.analytics %} instead.
class CookieConsent {
  static selector() {
    return "[data-cookie-banner]";
  }

  constructor(banner) {
    this.banner = banner;
    const state = document.getElementById("cookie-consent-granted");
    this.granted = state ? JSON.parse(state.textContent) : [];

    for (const form of document.querySelectorAll("[data-cookie-consent-form]")) {
      form.addEventListener("submit", (event) => this.submit(event, form));
    }
    for (const link of document.querySelectorAll("[data-cookie-settings]")) {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        this.openSettings();
      });
    }

    this.activateScripts();
  }

  openSettings() {
    this.banner.hidden = false;
    const details = this.banner.querySelector("[data-cookie-details]");
    details.open = true;
    (details.querySelector("input[name=categories]") || details.querySelector("summary")).focus();
  }

  async submit(event, form) {
    event.preventDefault();
    const data = new FormData(form);
    if (event.submitter) data.set(event.submitter.name, event.submitter.value);

    let response;
    try {
      response = await fetch(form.action, {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
    } catch {
      form.submit();
      return;
    }
    if (!response.ok) {
      form.submit();
      return;
    }

    const { granted } = await response.json();
    const revoked = this.granted.some((key) => !granted.includes(key));
    this.granted = granted;

    // Scripts that already ran cannot be unloaded: start from a clean page.
    if (revoked) {
      window.location.reload();
      return;
    }

    this.syncCheckboxes();
    this.banner.hidden = true;
    this.activateScripts();
    document.dispatchEvent(new CustomEvent("cookieconsent:change", { detail: { granted } }));
  }

  syncCheckboxes() {
    for (const box of document.querySelectorAll("[data-cookie-consent-form] input[name=categories]")) {
      box.checked = this.granted.includes(box.value);
    }
  }

  activateScripts() {
    const blocked = document.querySelectorAll('script[type="text/plain"][data-cookie-category]');
    for (const inert of blocked) {
      if (!this.granted.includes(inert.dataset.cookieCategory)) continue;

      const script = document.createElement("script");
      for (const { name, value } of inert.attributes) {
        if (name !== "type" && name !== "data-cookie-category") script.setAttribute(name, value);
      }
      script.textContent = inert.textContent;
      inert.replaceWith(script);
    }
  }
}

export default CookieConsent;
