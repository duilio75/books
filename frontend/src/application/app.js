
// This is the style entry file
import "../styles/index.css";
import "aos/dist/aos.css";

// We can import other JS file as we like
import AOS from "aos";
import $ from "jquery";
import PasswordToggle from "../components/password-toggle";
import MessageToast from "../components/message-toast";
import BookSearch from "../components/search-book";
import MobileMenu from "../components/mobile-menu";
import ReviewDialog from "../components/review-dialog";

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

  const reviewDialog = document.querySelector(ReviewDialog.selector());
  if (reviewDialog) new ReviewDialog(reviewDialog);

  const menuToggle = document.querySelector(MobileMenu.selector());
  if (menuToggle) new MobileMenu(menuToggle);

  const termsDialog = document.getElementById('terms-dialog');
  if (termsDialog) termsDialog.showModal();


  AOS.init({
    once: true,
  });
});

