// EduBridge — Dashboard Progress Animator
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('[data-progress]').forEach(function(el) {
    const val = el.getAttribute('data-progress');
    if (val !== null && val !== '') {
      el.style.width = val + '%';
    }
  });
});
