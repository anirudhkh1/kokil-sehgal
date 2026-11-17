/* Kokil Sehgal: small progressive enhancements. The page works without this file. */
(function () {
  'use strict';

  var EMAIL = 'hello@kokilsehgal.com';
  var root = document.documentElement;

  /* Fade sections in as they scroll into view.
     The inline script in <head> adds .reveal-ready only when motion is allowed
     and IntersectionObserver exists, so content is never hidden otherwise. */
  window.__revealInit = true;
  if (root.classList.contains('reveal-ready')) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('[data-reveal]').forEach(function (el) { io.observe(el); });
  }

  /* FAQ: keep one answer open at a time. Modern browsers do this natively via
     <details name="faq">; this covers older ones. */
  var faqs = document.querySelectorAll('.faq-item');
  faqs.forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (!item.open) return;
      faqs.forEach(function (other) { if (other !== item) other.open = false; });
    });
  });

  /* Contact form: open the visitor's email app with the message filled in. */
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var f = new FormData(form);
      var name = (f.get('name') || '').toString().trim();
      var body =
        'Name: ' + name + '\n' +
        'Email: ' + f.get('email') + '\n' +
        'Website or Instagram: ' + (f.get('site') || '-') + '\n' +
        'What I need: ' + (f.get('need') || '-') + '\n\n' +
        (f.get('message') || '');
      var subject = 'New project inquiry from ' + (name || 'website');
      window.location.href =
        'mailto:' + EMAIL +
        '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(body);
      var note = document.getElementById('form-note');
      if (note) note.hidden = false;
    });
  }

  /* Footer year */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
