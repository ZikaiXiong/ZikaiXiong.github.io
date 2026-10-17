// Hover previews: hovering a badge with data-preview expands a looping clip of that demo
// under the paper entry. Only on devices with a real hover (touch devices just follow the link).
document.addEventListener('DOMContentLoaded', function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Teaching-tool cards: play the clip while the pointer is over the card.
  document.querySelectorAll('.tool-card').forEach(function (card) {
    var video = card.querySelector('video');
    if (!video || still) return;
    card.addEventListener('mouseenter', function () {
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    });
    card.addEventListener('mouseleave', function () { video.pause(); });
  });

  document.querySelectorAll('.pub-preview').forEach(function (box) {
    var entry = box.closest('li');
    var badges = entry.querySelectorAll('.pub-badge[data-preview]');
    var cards = box.querySelectorAll('.pub-preview-card');
    var closeTimer = null;
    box.hidden = false;

    function show(key) {
      clearTimeout(closeTimer);
      cards.forEach(function (card) {
        var on = card.dataset.preview === key;
        var video = card.querySelector('video');
        card.classList.toggle('is-active', on);
        if (on && !still) {
          var p = video.play();
          if (p && p.catch) p.catch(function () {});
        } else {
          video.pause();
        }
      });
      box.classList.add('is-open');
    }

    function scheduleClose() {
      clearTimeout(closeTimer);
      closeTimer = setTimeout(function () {
        box.classList.remove('is-open');
        cards.forEach(function (card) { card.querySelector('video').pause(); });
      }, 350);
    }

    badges.forEach(function (badge) {
      badge.addEventListener('mouseenter', function () { show(badge.dataset.preview); });
      badge.addEventListener('mouseleave', scheduleClose);
      badge.addEventListener('focus', function () { show(badge.dataset.preview); });
      badge.addEventListener('blur', scheduleClose);
    });
    box.addEventListener('mouseenter', function () { clearTimeout(closeTimer); });
    box.addEventListener('mouseleave', scheduleClose);
  });
});
