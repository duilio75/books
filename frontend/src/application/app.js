
// This is the style entry file
import "../styles/index.css";
import "aos/dist/aos.css";

// We can import other JS file as we like
import AOS from "aos";
import $ from "jquery";
import PasswordToggle from "../components/password-toggle";

$(function () {
  window.console.log("jquery ready");

  for (const btn of document.querySelectorAll(PasswordToggle.selector())) {
    new PasswordToggle(btn);
  }

  const termsDialog = document.getElementById('terms-dialog');
  if (termsDialog) termsDialog.showModal();


  AOS.init({
    once: true,
  });
});

