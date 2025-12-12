async function fetchQuotes() {
  const res = await fetch("../quotes.json");
  return res.json();
}

function getRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

window.document$.subscribe(async () => {
  const box = document.getElementById("daily-quote");
  const textEl = document.getElementById("quote-text");
  const metaEl = document.getElementById("quote-meta");

  if (!box || !textEl || !metaEl) return;

  try {
    const quotes = await fetchQuotes();
    const q = getRandom(quotes);

    // fade out
    box.style.opacity = 0;

    setTimeout(() => {
      // quote text
      textEl.textContent = q.quote;

      // author + optional link
      if (q.author && q.source) {
        metaEl.innerHTML = `<a href="${q.source}" target="_blank" rel="noopener noreferrer" style="text-decoration: underline;">${q.author}</a>`;
      } else if (q.author) {
        metaEl.textContent = q.author;
      } else {
        metaEl.textContent = "";
      }

      // fade in
      box.style.opacity = 1;
    }, 120);
  } catch (err) {
    console.error("fetchQuotes error:", err);
  }
});
