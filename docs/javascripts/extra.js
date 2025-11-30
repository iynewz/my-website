const quotes = [
  "Stay hungry. Stay foolish.",
  "Talk is cheap. Show me the code.",
  "Simple is better than complex.",
  "Premature optimization is the root of all evil.",
  "Make it work, make it right, make it fast.",
  "The only way to learn a new language is to write programs in it.",
  "Code is like humor. When you have to explain it, it’s bad.",
  "Programs must be written for people to read, and only incidentally for machines to execute.",
];

function getRandomQuote() {
  return quotes[Math.floor(Math.random() * quotes.length)];
}

window.document$.subscribe(() => {
  const el = document.getElementById("daily-quote");
  if (!el) return;

  const quote = getRandomQuote();

  // 为了让 instant navigation 也有动画：先透明
  el.style.opacity = 0;

  // 小延迟，让浏览器有机会应用透明状态
  setTimeout(() => {
    el.textContent = quote;
    el.style.opacity = 1; // fade-in
  }, 50);
});
