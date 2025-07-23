  const texts = document.querySelectorAll("#text-rotator .rotating-text");
  let current = 0;

  setInterval(() => {
    texts[current].classList.remove("active");
    const next = (current + 1) % texts.length;

    setTimeout(() => {
      texts[next].classList.add("active");
      current = next;
    }, 300); // delay between fade out and next fade in
  }, 4000);
