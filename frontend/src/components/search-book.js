class BookSearch {
  static selector() {
    return "#book-search-form";
  }

  constructor(form) {
    this.form = form;
    this.input = document.getElementById("book-search-input");
    this.resultsEl = document.getElementById("book-results");
    this.dialog = document.getElementById("review-dialog");
    this.reviewForm = document.getElementById("rdlg-form");
    this.starButtons = document.querySelectorAll("#star-row button");
    this.selectedRating = 0;

    this.form.addEventListener("submit", (e) => this.search(e));
    this.resultsEl.addEventListener("click", (e) => this.onResultsClick(e));
    this.reviewForm.addEventListener("submit", (e) => this.submitReview(e));

    this.starButtons.forEach((btn, i) => {
      btn.addEventListener("click", () => this.setStars(i + 1));
    });

    document.querySelectorAll("[data-dialog-close]").forEach((btn) => {
      btn.addEventListener("click", () => this.dialog.close());
    });
  }

  async search(e) {
    e.preventDefault();
    const query = this.input.value.trim();
    if (!query) return;
    this.resultsEl.innerHTML = '<p class="col-span-full text-sm text-gray-500">Searching…</p>';
    try {
      const res = await fetch("/api/books/search/?q=" + encodeURIComponent(query));
      const data = await res.json();
      if (data.error) {
        const msg = (typeof data.error === "string" ? data.error : data.error.message) || "An error occurred.";
        this.resultsEl.innerHTML = '<p class="col-span-full text-sm text-red-500">' + msg + "</p>";
        return;
      }
      if (!data.items || data.items.length === 0) {
        this.resultsEl.innerHTML = '<p class="col-span-full text-sm text-gray-500">No books found.</p>';
        return;
      }
      this.resultsEl.innerHTML = data.items.map((item) => this.renderResult(item)).join("");
    } catch (throwError) {
      console.error(throwError);
      this.resultsEl.innerHTML = '<p class="col-span-full text-sm text-red-500">Something went wrong. Please try again.</p>';
    }
  }

  renderResult(item) {
    const info = item.volumeInfo;
    const thumb = info.imageLinks && info.imageLinks.thumbnail ? info.imageLinks.thumbnail : "";
    const title = info.title || "Unknown title";
    const authors = info.authors ? info.authors.join(", ") : "";
    const inDb = item._in_db;
    const description = info.description || "";
    //console.log(info);
    const volumeId = item.id || "";
    const isbn = (info.industryIdentifiers || []).map((x) => x.identifier).join(",");
    const coverUrl = thumb;
    const bookAttr = JSON.stringify({ volumeId, isbn, title, authors, coverUrl, description }).replace(/"/g, "&quot;");
    const reviewBtn = '<button type="button" data-book="' + bookAttr + '" class="flex-1 bg-blue-100 py-2 text-center text-xs font-semibold text-gray-600 hover:bg-blue-200">Leave a Review</button>';
    const btn = inDb
      ? '<span class="mt-auto flex flex-col divide-y divide-blue-500 rounded-b-lg overflow-hidden">'
        + reviewBtn
        + '<a href="/book/' + item._url_alias + '/" class="flex-1 bg-blue-600 py-2 text-center text-xs font-semibold text-white hover:bg-blue-700">View Book</a>'
        + "</span>"
      : '<span class="mt-auto flex rounded-b-lg overflow-hidden">' + reviewBtn + "</span>";
    return '<span class="flex flex-col overflow-hidden rounded-lg border ' + (inDb ? "border-green-400 ring-2 ring-green-300" : "border-gray-200") + ' bg-white shadow-sm">'
      + '<span class="relative">'
      + (thumb
          ? '<img src="' + thumb + '" alt="' + title.replace(/"/g, "&quot;") + '" class="h-40 w-full object-cover" />'
          : '<span class="flex h-40 items-center justify-center bg-gray-100 text-gray-400 text-xs">No cover</span>')
      + (inDb ? '<span class="absolute right-2 top-2 rounded-full bg-green-500 px-2 py-0.5 text-[10px] font-semibold text-white shadow">In Library</span>' : "")
      + "</span>"
      + '<span class="flex flex-col flex-1 p-3">'
      + '<p class="text-xs font-semibold text-gray-800 line-clamp-2">' + title + "</p>"
      + (authors ? '<p class="mt-1 text-xs text-gray-500 line-clamp-1">' + authors + "</p>" : "")
      + "</span>"
      + btn
      + "</span>";
  }

  onResultsClick(e) {
    const btn = e.target.closest("[data-book]");
    if (!btn) return;
    this.openReviewDialog(JSON.parse(btn.dataset.book));
  }

  openReviewDialog(book) {
    document.getElementById("rdlg-title").textContent = book.title;
    document.getElementById("rdlg-author").textContent = book.authors || "";
    document.getElementById("rdlg-cover").src = book.coverUrl || "";
    document.getElementById("rdlg-cover").style.display = book.coverUrl ? "" : "none";
    document.getElementById("rdlg-volume-id").value = book.volumeId;
    document.getElementById("rdlg-isbn").value = book.isbn;
    document.getElementById("rdlg-book-title").value = book.title;
    document.getElementById("rdlg-book-author").value = book.authors || "";
    document.getElementById("rdlg-book-description").value = book.description || "";
    document.getElementById("rdlg-book-cover").value = book.coverUrl || "";
    document.getElementById("rdlg-rating").value = "";
    document.getElementById("rdlg-text").value = "";
    document.getElementById("rdlg-error").textContent = "";
    document.getElementById("rdlg-success").classList.add("hidden");
    document.getElementById("rdlg-form").classList.remove("hidden");
    this.setStars(0);
    this.dialog.showModal();
  }

  setStars(n) {
    this.selectedRating = n;
    document.getElementById("rdlg-rating").value = n;
    this.starButtons.forEach((btn, i) => {
      btn.textContent = i < n ? "★" : "☆";
      btn.classList.toggle("text-yellow-400", i < n);
      btn.classList.toggle("text-gray-300", i >= n);
    });
  }

  async submitReview(e) {
    e.preventDefault();
    const rating = parseInt(document.getElementById("rdlg-rating").value, 10);
    const reviewText = document.getElementById("rdlg-text").value.trim();
    const errEl = document.getElementById("rdlg-error");
    if (!rating) { errEl.textContent = "Please select a rating."; return; }
    if (!reviewText) { errEl.textContent = "Please write a review."; return; }
    errEl.textContent = "";
    const payload = {
      volume_id: document.getElementById("rdlg-volume-id").value,
      isbn: document.getElementById("rdlg-isbn").value,
      title: document.getElementById("rdlg-book-title").value,
      author: document.getElementById("rdlg-book-author").value,
      cover_url: document.getElementById("rdlg-book-cover").value,
      description: document.getElementById("rdlg-book-description").value,
      rating: rating,
      review_text: reviewText,
    };
    try {
      const res = await fetch("/api/books/reviews/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": this.getCookie("csrftoken") },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json();
        errEl.textContent = JSON.stringify(err);
        return;
      }
      document.getElementById("rdlg-form").classList.add("hidden");
      document.getElementById("rdlg-success").classList.remove("hidden");
    } catch (throwError) {
      console.error(throwError);
      errEl.textContent = "Network error. Please try again.";
    }
  }

  getCookie(name) {
    const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return m ? m.pop() : "";
  }
}

export default BookSearch;
