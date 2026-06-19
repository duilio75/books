
// This is the style entry file
import "../styles/index.css";
import "aos/dist/aos.css";

// We can import other JS file as we like
import Jumbotron from "../components/jumbotron";
import AOS from "aos";

window.document.addEventListener("DOMContentLoaded", function () {
  window.console.log("dom ready");

  // Find elements and initialize
  for (const elem of document.querySelectorAll(Jumbotron.selector())) {
    new Jumbotron(elem);
  }

  AOS.init({
    once: true,
  });
});

