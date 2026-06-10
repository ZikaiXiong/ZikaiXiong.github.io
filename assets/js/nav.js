// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', function () {
  var btn = document.querySelector('.nav-toggle');
  var menu = document.querySelector('.nav-links');
  if (!btn || !menu) return;

  btn.addEventListener('click', function () {
    var open = menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  menu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });
});
