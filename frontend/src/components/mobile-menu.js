class MobileMenu {
  static selector() {
    return "#menu-toggle";
  }

  constructor(btn) {
    this.btn = btn;
    this.panel = document.getElementById(btn.getAttribute("aria-controls"));
    if (!this.panel) return;

    btn.addEventListener("click", () => this.toggle());

    // Close on Escape, on a click outside the header, and after following a
    // link, so the panel never stays open over the page underneath.
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.close();
    });

    document.addEventListener("click", (e) => {
      if (!this.isOpen()) return;
      if (this.btn.contains(e.target) || this.panel.contains(e.target)) return;
      this.close();
    });

    this.panel.addEventListener("click", (e) => {
      if (e.target.closest("a")) this.close();
    });
  }

  isOpen() {
    return !this.panel.hidden;
  }

  toggle() {
    if (this.isOpen()) this.close();
    else this.open();
  }

  open() {
    this.panel.hidden = false;
    this.btn.setAttribute("aria-expanded", "true");
  }

  close() {
    this.panel.hidden = true;
    this.btn.setAttribute("aria-expanded", "false");
  }
}

export default MobileMenu;
