import Dialog from "./dialog";

const REVIEWS_URL = "/api/books/reviews/";

function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return m ? m.pop() : "";
}

// "Leave a Review" dialog. Any page that includes partials/review_dialog.html
// gets it: a button carrying data-book='{"volumeId":…,"title":…}' opens it,
// or call open(book) directly.
class ReviewDialog extends Dialog {
  static selector() {
    return "#review-dialog";
  }

  static trigger() {
    return "[data-book]";
  }

  constructor(el) {
    super(el);
    this.form = this.$("#rdlg-form");
    this.success = this.$("#rdlg-success");
    this.error = this.$("#rdlg-error");
    this.rating = this.$("#rdlg-rating");
    this.starButtons = this.$$("#star-row button");

    this.form.addEventListener("submit", (e) => this.submit(e));

    this.starButtons.forEach((btn, i) => {
      btn.addEventListener("click", () => this.setStars(i + 1));
    });

    // Delegated so it also covers buttons rendered after page load, such as
    // the search results.
    document.addEventListener("click", (e) => {
      const btn = e.target.closest(ReviewDialog.trigger());
      if (!btn) return;
      this.open(JSON.parse(btn.dataset.book));
    });
  }

  // book: { volumeId, isbn, title, authors, coverUrl, description }
  open(book) {
    this.$("#rdlg-title").textContent = book.title || "";
    this.$("#rdlg-author").textContent = book.authors || "";

    const cover = this.$("#rdlg-cover");
    cover.src = book.coverUrl || "";
    cover.style.display = book.coverUrl ? "" : "none";

    this.$("#rdlg-volume-id").value = book.volumeId || "";
    this.$("#rdlg-isbn").value = book.isbn || "";
    this.$("#rdlg-book-title").value = book.title || "";
    this.$("#rdlg-book-author").value = book.authors || "";
    this.$("#rdlg-book-description").value = book.description || "";
    this.$("#rdlg-book-cover").value = book.coverUrl || "";
    this.$("#rdlg-text").value = "";

    this.error.textContent = "";
    this.success.classList.add("hidden");
    this.form.classList.remove("hidden");
    this.setStars(0);

    super.open();
  }

  setStars(n) {
    this.rating.value = n;
    this.starButtons.forEach((btn, i) => {
      btn.textContent = i < n ? "★" : "☆";
      btn.classList.toggle("text-yellow-400", i < n);
      btn.classList.toggle("text-gray-300", i >= n);
    });
  }

  async submit(e) {
    e.preventDefault();
    const rating = parseInt(this.rating.value, 10);
    const reviewText = this.$("#rdlg-text").value.trim();
    if (!rating) { this.error.textContent = "Please select a rating."; return; }
    if (!reviewText) { this.error.textContent = "Please write a review."; return; }
    this.error.textContent = "";

    const payload = {
      volume_id: this.$("#rdlg-volume-id").value,
      isbn: this.$("#rdlg-isbn").value,
      title: this.$("#rdlg-book-title").value,
      author: this.$("#rdlg-book-author").value,
      cover_url: this.$("#rdlg-book-cover").value,
      description: this.$("#rdlg-book-description").value,
      rating: rating,
      review_text: reviewText,
    };

    try {
      const res = await fetch(REVIEWS_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json();
        this.error.textContent = JSON.stringify(err);
        return;
      }
      this.form.classList.add("hidden");
      this.success.classList.remove("hidden");
    } catch (throwError) {
      console.error(throwError);
      this.error.textContent = "Network error. Please try again.";
    }
  }
}

export default ReviewDialog;
