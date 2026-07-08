class MessageToast {
  static selector() {
    return ".toast-item";
  }

  constructor(el) {
    this.el = el;
    requestAnimationFrame(() => this.el.classList.remove("translate-y-[-120%]"));
    setTimeout(() => this.dismiss(), 4000);
  }

  dismiss() {
    this.el.classList.add("opacity-0", "translate-y-[-120%]");
    this.el.addEventListener("transitionend", () => this.el.remove());
  }
}

export default MessageToast;
