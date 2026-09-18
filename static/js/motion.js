(() => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const menuToggle = $('.menu-toggle');
  const navigation = $('.header-actions');
  menuToggle?.addEventListener('click', () => {
    const open = !navigation.classList.contains('is-open');
    navigation.classList.toggle('is-open', open);
    menuToggle.setAttribute('aria-expanded', String(open));
  });

  const revealItems = $$('[data-reveal], .card, .filters, .form-card, .cart-summary, .pd-gallery-main');
  if (reducedMotion || !('IntersectionObserver' in window)) {
    revealItems.forEach((element) => element.classList.add('is-visible'));
  } else {
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          currentObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px' });
    revealItems.forEach((element) => observer.observe(element));
  }

  const passwordToggle = $('[data-password-toggle]');
  passwordToggle?.addEventListener('click', () => {
    const input = $('.password-field input');
    if (!input) return;
    const showing = input.type === 'text';
    input.type = showing ? 'password' : 'text';
    passwordToggle.setAttribute('aria-pressed', String(!showing));
    passwordToggle.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
  });

  const heroSlides = $$('[data-hero-slide]');
  if (heroSlides.length > 1 && !reducedMotion) {
    let current = 0;
    const currentText = $('.hero-current');
    const progress = $('.hero-progress i');
    window.setInterval(() => {
      heroSlides[current].classList.remove('is-current');
      current = (current + 1) % heroSlides.length;
      heroSlides[current].classList.add('is-current');
      if (currentText) currentText.textContent = String(current + 1).padStart(2, '0');
      if (progress) progress.style.transform = `scaleX(${(current + 1) / heroSlides.length})`;
    }, 6000);
  }

  const catalog = $('[data-catalog]');
  if (catalog) {
    const items = $$('[data-catalog-item]', catalog);
    const controls = $$('[data-catalog-control]', catalog);
    const position = $('[data-catalog-position]', catalog);
    const isRtl = document.documentElement.dir === 'rtl';
    let current = 0;
    const select = (index) => {
      current = (index + items.length) % items.length;
      items.forEach((item, itemIndex) => item.classList.toggle('is-active', itemIndex === current));
      items.forEach((item, itemIndex) => {
        const active = itemIndex === current;
        item.toggleAttribute('inert', !active);
        item.setAttribute('aria-hidden', String(!active));
      });
      controls.forEach((control, controlIndex) => {
        const active = controlIndex === current;
        control.classList.toggle('is-active', active);
        control.setAttribute('aria-pressed', String(active));
      });
      if (position) position.textContent = String(current + 1).padStart(2, '0');
    };
    controls.forEach((control) => control.addEventListener('click', () => select(Number(control.dataset.index))));
    $('[data-catalog-prev]', catalog)?.addEventListener('click', () => select(current - 1));
    $('[data-catalog-next]', catalog)?.addEventListener('click', () => select(current + 1));
    catalog.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') { event.preventDefault(); select(current + (isRtl ? 1 : -1)); }
      if (event.key === 'ArrowRight') { event.preventDefault(); select(current + (isRtl ? -1 : 1)); }
    });
    select(0);
  }

  const book = $('[data-book]');
  if (book) {
    const pages = $$('[data-book-page]', book);
    const position = $('[data-book-position]', book);
    let current = 0;
    const select = (index) => {
      current = (index + pages.length) % pages.length;
      pages.forEach((page, pageIndex) => page.classList.toggle('is-active', pageIndex === current));
      if (position) position.textContent = String(current + 1).padStart(2, '0');
    };
    $('[data-book-prev]', book)?.addEventListener('click', () => select(current - 1));
    $('[data-book-next]', book)?.addEventListener('click', () => select(current + 1));
  }
})();
