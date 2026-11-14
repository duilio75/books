// Searches the books API and renders the result cards. Reviewing is handled by
// ReviewDialog, which picks up the [data-book] buttons rendered here.
class BookSearch {
  static selector() {
    return "#book-search-form";
  }

  constructor(form) {
    this.form = form;
    this.input = document.getElementById("book-search-input");
    this.resultsEl = document.getElementById("book-results");

    this.form.addEventListener("submit", (e) => this.search(e));

    // A review saved from a result card creates the book if it was missing:
    // give that card its "View Book" button.
    document.addEventListener("review:created", (e) => this.showViewButton(e.detail));

    // /search/?q=... renders the input pre-filled: run that search right away.
    if (this.input.value.trim()) this.runSearch();
  }

  search(e) {
    e.preventDefault();
    return this.runSearch();
  }

  async runSearch() {
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

  showViewButton(review) {
    if (!review._url_alias) return;
    const card = this.resultsEl.querySelector('[data-volume-id="' + CSS.escape(review.volume_id) + '"]');
    if (!card || card.querySelector("[data-view-book]")) return;
    const actions = card.querySelector("[data-actions]");
    actions.outerHTML = this.renderActions(actions.innerHTML, review._url_alias);
  }

  // The card's bottom buttons: "Leave a Review" always, plus "View Book" once
  // the book is in the library (urlAlias set).
  renderActions(reviewBtn, urlAlias) {
    if (!urlAlias) {
      return '<span data-actions class="mt-auto flex rounded-b-lg overflow-hidden">' + reviewBtn + "</span>";
    }
    const viewBtn = '<a data-view-book href="/book/' + urlAlias + '/" class="flex-1 bg-blue-600 py-2 text-center text-xs font-semibold text-white hover:bg-blue-700">View Book</a>';
    return '<span data-actions class="mt-auto flex flex-col divide-y divide-blue-500 rounded-b-lg overflow-hidden">'
      + reviewBtn
      + viewBtn
      + "</span>";
  }

  renderResult(item) {
    const info = item.volumeInfo;
    const thumb = info.imageLinks && info.imageLinks.thumbnail ? info.imageLinks.thumbnail : "";
    const title = info.title || "Unknown title";
    const authors = info.authors ? info.authors.join(", ") : "";
    const inDb = item._in_db;
    const description = info.description || "";
    const volumeId = item.id || "";
    const isbn = (info.industryIdentifiers || []).map((x) => x.identifier).join(",");
    const coverUrl = thumb;
    // data-book is ReviewDialog's trigger: the payload it carries is what
    // ReviewDialog.open() expects.
    const bookAttr = JSON.stringify({ volumeId, isbn, title, authors, coverUrl, description }).replace(/"/g, "&quot;");
    const reviewBtn = '<button type="button" data-book="' + bookAttr + '" class="flex-1 bg-blue-100 py-2 text-center text-xs font-semibold text-gray-600 cursor-pointer hover:bg-blue-200">Leave a Review</button>';
    const btn = this.renderActions(reviewBtn, inDb ? item._url_alias : "");
    return '<span data-volume-id="' + volumeId.replace(/"/g, "&quot;") + '" class="flex flex-col overflow-hidden rounded-lg border ' + (inDb ? "border-green-400 ring-2 ring-green-300" : "border-gray-200") + ' bg-white shadow-sm">'
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
}

export default BookSearch;
