
// This is the style entry file
import "../styles/index.css";
import "aos/dist/aos.css";

// We can import other JS file as we like
import AOS from "aos";
import $ from "jquery";
import PasswordToggle from "../components/password-toggle";
import MessageToast from "../components/message-toast";
import BookSearch from "../components/search-book";

$(function () {
  window.console.log("jquery ready");

  for (const btn of document.querySelectorAll(PasswordToggle.selector())) {
    new PasswordToggle(btn);
  }

  for (const el of document.querySelectorAll(MessageToast.selector())) {
    new MessageToast(el);
  }

  const bookSearchForm = document.querySelector(BookSearch.selector());
  if (bookSearchForm) new BookSearch(bookSearchForm);

  const termsDialog = document.getElementById('terms-dialog');
  if (termsDialog) termsDialog.showModal();


  AOS.init({
    once: true,
  });
});

