async function fetchQuotes() {
  console.log("enter");
  const res = await fetch("./quotes.json");
  return res.json();
}

function getRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// window.document$.subscribe(async () => {
//   const el = document.getElementById("daily-quote");
//   if (!el) return;

//   const quotes = await fetchQuotes();
//   console.log(quotes);
//   const quote = getRandom(quotes);

//   el.style.opacity = 0;

//   setTimeout(() => {
//     el.textContent = quote;
//     el.style.opacity = 1;
//   }, 50);
// });
window.document$.subscribe(async () => {
  console.log("enter");
  const el = document.getElementById("daily-quote");
  if (!el) return;

  try {
    const quotes = await fetchQuotes();
    console.log(quotes);
  } catch (err) {
    console.error("fetchQuotes error:", err);
  }
});
