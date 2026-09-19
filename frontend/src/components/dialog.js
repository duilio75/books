// Thin wrapper around <dialog>: open/close plus [data-dialog-close] buttons.
// Subclass it for dialogs that carry their own content and behaviour.
class Dialog {
  constructor(el) {
    this.el = el;

    this.el.querySelectorAll("[data-dialog-close]").forEach((btn) => {
      btn.addEventListener("click", () => this.close());
    });
  }

  // Query inside this dialog only, so several dialogs can live on one page.
  $(selector) {
    return this.el.querySelector(selector);
  }

  $$(selector) {
    return Array.from(this.el.querySelectorAll(selector));
  }

  isOpen() {
    return this.el.open;
  }

  open() {
    this.el.showModal();
  }

  close() {
    this.el.close();
  }
}

export default Dialog;
