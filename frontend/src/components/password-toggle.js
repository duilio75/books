class PasswordToggle {
  static selector() {
    return "[data-password-toggle]";
  }

  constructor(btn) {
    this.btn = btn;
    this.input = document.getElementById(btn.dataset.passwordToggle);
    if (!this.input) return;
    btn.addEventListener("click", () => this.toggle());
  }

  toggle() {
    const show = this.input.type === "password";
    this.input.type = show ? "text" : "password";
    this.btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
    this.btn.querySelector("[data-icon-show]").classList.toggle("hidden", show);
    this.btn.querySelector("[data-icon-hide]").classList.toggle("hidden", !show);
  }
}

export default PasswordToggle;
