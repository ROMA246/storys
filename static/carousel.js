document.addEventListener('DOMContentLoaded', () => {
  const track = document.querySelector('.carousel-track');
  if (!track) return;
  const slides = Array.from(track.children);
  if (!slides.length) return;
  let index = 0;

  function update() {
    const w = slides[0].getBoundingClientRect().width;
    track.style.transform = `translateX(-${index * w}px)`;
  }

  window.addEventListener('resize', update);

  const next = document.querySelector('.next');
  const prev = document.querySelector('.prev');
  if (next) next.addEventListener('click', ()=>{ index = (index+1)%slides.length; update(); });
  if (prev) prev.addEventListener('click', ()=>{ index = (index-1+slides.length)%slides.length; update(); });

  setInterval(()=>{ index=(index+1)%slides.length; update(); }, 5000);

  update();
});
