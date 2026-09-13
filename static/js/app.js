// EduBridge — Core Application Script
document.addEventListener('DOMContentLoaded', function() {
  // Animated Counters
  document.querySelectorAll('[data-counter]').forEach(el => {
    const target = parseInt(el.dataset.counter, 10);
    if (isNaN(target)) return;
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          let c = 0;
          const step = Math.max(1, target / 90);
          const t = setInterval(() => {
            c += step;
            if (c >= target) {
              c = target;
              clearInterval(t);
            }
            el.textContent = Math.floor(c).toLocaleString();
          }, 16);
          obs.unobserve(el);
        }
      });
    });
    obs.observe(el);
  });

  // Auto-dismiss Toast Messages
  const toastBox = document.getElementById('toastBox');
  if (toastBox) {
    setTimeout(() => {
      toastBox.style.transition = 'opacity 0.5s ease';
      toastBox.style.opacity = '0';
      setTimeout(() => toastBox.remove(), 500);
    }, 4500);
  }

  // Initialize AOS animation library if present
  if (typeof AOS !== 'undefined') {
    AOS.init({ duration: 600, once: true, offset: 30 });
  }

  // Dynamic Progress Bars (reads data-progress="XX")
  document.querySelectorAll('[data-progress]').forEach(el => {
    const val = el.getAttribute('data-progress');
    if (val !== null && val !== '') {
      el.style.width = val + '%';
    }
  });

  // Console Brand Banner
  console.log('%c🎓 EduBridge — AI Higher-Education Platform', 'color:#0284C7;font-size:16px;font-weight:bold;');
});
