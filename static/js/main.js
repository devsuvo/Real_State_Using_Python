/* Crystal Bay Estates — front-end behaviour */
(function () {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^|;\\s*)" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[2]) : "";
  }
  const csrfToken = () => getCookie("csrftoken") || ($("input[name=csrfmiddlewaretoken]") || {}).value || "";

  function safeStorage(kind) {
    try {
      const s = window[kind];
      const k = "__cb_test__";
      s.setItem(k, "1");
      s.removeItem(k);
      return s;
    } catch (e) {
      return null;
    }
  }

  /* ---------- Header: solid on scroll + back-to-top ---------- */
  const header = $("#siteHeader");
  const toTop = $(".back-to-top");
  function onScroll() {
    const y = window.scrollY;
    if (header) header.classList.toggle("is-scrolled", y > 60);
    if (toTop) toTop.classList.toggle("is-visible", y > 600);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  /* ---------- Hero background slider ---------- */
  const slides = $$(".hero-slide");
  const dots = $$(".hero-dots button");
  if (slides.length > 1) {
    let current = 0;
    let timer;
    const show = (i) => {
      slides[current].classList.remove("is-active");
      if (dots[current]) dots[current].classList.remove("is-active");
      current = (i + slides.length) % slides.length;
      slides[current].classList.add("is-active");
      if (dots[current]) dots[current].classList.add("is-active");
    };
    const start = () => { timer = setInterval(() => show(current + 1), 6000); };
    dots.forEach((dot) => dot.addEventListener("click", () => {
      clearInterval(timer);
      show(+dot.dataset.slide);
      start();
    }));
    start();
  }

  /* ---------- Swipers ---------- */
  if (window.Swiper) {
    if ($(".featured-swiper")) {
      new Swiper(".featured-swiper", {
        slidesPerView: 1.08,
        spaceBetween: 16,
        grabCursor: true,
        navigation: { nextEl: ".featured-next", prevEl: ".featured-prev" },
        breakpoints: {
          576: { slidesPerView: 1.5, spaceBetween: 20 },
          768: { slidesPerView: 2, spaceBetween: 24 },
          1200: { slidesPerView: 3, spaceBetween: 28 },
        },
      });
    }
    if ($(".testimonial-swiper")) {
      new Swiper(".testimonial-swiper", {
        slidesPerView: 1,
        spaceBetween: 20,
        autoplay: { delay: 6500, disableOnInteraction: false },
        pagination: { el: ".testimonial-swiper .swiper-pagination", clickable: true },
        breakpoints: { 768: { slidesPerView: 2, spaceBetween: 24 }, 1200: { slidesPerView: 3, spaceBetween: 28 } },
      });
    }
    if ($(".gallery-main")) {
      let thumbs = null;
      if ($(".gallery-thumbs")) {
        thumbs = new Swiper(".gallery-thumbs", {
          slidesPerView: 3.5,
          spaceBetween: 10,
          watchSlidesProgress: true,
          breakpoints: { 576: { slidesPerView: 5 }, 992: { slidesPerView: 7 } },
        });
      }
      new Swiper(".gallery-main", {
        loop: false,
        spaceBetween: 0,
        keyboard: { enabled: true },
        navigation: { nextEl: ".gallery-next", prevEl: ".gallery-prev" },
        thumbs: thumbs ? { swiper: thumbs } : undefined,
      });
    }
  }

  /* ---------- Counters ---------- */
  const counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10) || 0;
        const duration = 1600;
        const startTime = performance.now();
        const step = (now) => {
          const p = Math.min((now - startTime) / duration, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(target * eased).toLocaleString();
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        io.unobserve(el);
      });
    }, { threshold: 0.4 });
    counters.forEach((el) => io.observe(el));
  } else {
    counters.forEach((el) => { el.textContent = (+el.dataset.count).toLocaleString(); });
  }

  /* ---------- Reveal on scroll ---------- */
  const revealTargets = $$(".section-heading, .property-card, .feature-card, .type-card, .city-card, .pricing-card, .agent-card, .post-card, .value-card, .info-card");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const rio = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          rio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealTargets.forEach((el) => {
      if (el.closest(".swiper")) return;
      el.classList.add("reveal");
      rio.observe(el);
    });
  }

  /* ---------- Favorites ---------- */
  function updateFavCount(count) {
    $$("[data-fav-count]").forEach((el) => {
      el.textContent = count;
      el.hidden = !count;
    });
  }
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-fav]");
    if (!btn) return;
    e.preventDefault();
    fetch(btn.dataset.url, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken(), "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
    })
      .then((r) => r.json())
      .then((data) => {
        $$(`[data-fav="${btn.dataset.fav}"]`).forEach((b) => {
          b.classList.toggle("is-active", data.active);
          b.setAttribute("aria-pressed", data.active ? "true" : "false");
          b.classList.remove("pop");
          void b.offsetWidth;
          b.classList.add("pop");
        });
        updateFavCount(data.count);
        if (!data.active) {
          const item = $(`[data-fav-item="${btn.dataset.fav}"]`);
          if (item) {
            item.style.transition = "opacity .3s";
            item.style.opacity = "0";
            setTimeout(() => item.remove(), 300);
          }
        }
      })
      .catch(() => {});
  });

  /* ---------- Share / copy link ---------- */
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-share]");
    if (!btn) return;
    const url = window.location.href;
    if (navigator.share) {
      navigator.share({ title: document.title, url }).catch(() => {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => toast("Link copied to clipboard"));
    }
  });

  /* ---------- Agent social icons (inside a link) ---------- */
  document.addEventListener("click", (e) => {
    const s = e.target.closest(".agent-card-social [data-href]");
    if (!s) return;
    e.preventDefault();
    window.open(s.dataset.href, "_blank", "noopener");
  });

  /* ---------- Auto-submit sort select ---------- */
  $$("[data-autosubmit]").forEach((el) => el.addEventListener("change", () => el.form.submit()));

  /* ---------- Toasts ---------- */
  function dismissToast(t) {
    t.classList.add("is-hiding");
    setTimeout(() => t.remove(), 300);
  }
  function toast(text) {
    let stack = $(".toast-stack");
    if (!stack) {
      stack = document.createElement("div");
      stack.className = "toast-stack";
      document.body.appendChild(stack);
    }
    const t = document.createElement("div");
    t.className = "cb-toast";
    t.innerHTML = '<i class="bi bi-check2-circle"></i><span></span><button type="button" class="cb-toast-close" aria-label="Close">&times;</button>';
    t.querySelector("span").textContent = text;
    stack.appendChild(t);
    setTimeout(() => dismissToast(t), 4000);
  }
  $$(".cb-toast").forEach((t) => setTimeout(() => dismissToast(t), 6000));
  document.addEventListener("click", (e) => {
    const close = e.target.closest(".cb-toast-close");
    if (close) dismissToast(close.closest(".cb-toast"));
  });

  /* ---------- Popup ---------- */
  const popupEl = $("#sitePopup");
  if (popupEl && window.bootstrap) {
    const id = popupEl.dataset.popupId;
    const freq = popupEl.dataset.frequency;
    const delay = (parseInt(popupEl.dataset.delay, 10) || 0) * 1000;
    const key = "cb_popup_" + id;
    const local = safeStorage("localStorage");
    const session = safeStorage("sessionStorage");
    const periods = { day: 864e5, week: 6048e5 };

    let shouldShow = true;
    if (freq === "session" && session && session.getItem(key)) shouldShow = false;
    if (periods[freq] && local) {
      const last = parseInt(local.getItem(key) || "0", 10);
      if (Date.now() - last < periods[freq]) shouldShow = false;
    }
    if (local && local.getItem(key + "_done")) shouldShow = false; // already submitted the form

    const remember = () => {
      if (freq === "session" && session) session.setItem(key, "1");
      if (periods[freq] && local) local.setItem(key, String(Date.now()));
    };

    if (shouldShow) {
      const modal = new bootstrap.Modal(popupEl);
      setTimeout(() => {
        // Don't interrupt if another modal or the mobile menu is open
        if (document.querySelector(".modal.show, .offcanvas.show")) return;
        modal.show();
        remember();
      }, delay);
    }

    const form = $(".popup-form", popupEl);
    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const err = $(".popup-error", form);
        const name = form.elements.name.value.trim();
        const email = form.elements.email.value.trim();
        if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
          err.hidden = false;
          return;
        }
        err.hidden = true;
        const btn = form.querySelector("button[type=submit]");
        btn.disabled = true;
        fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "XMLHttpRequest" },
          credentials: "same-origin",
        })
          .then((r) => r.json())
          .then((data) => {
            if (!data.ok) throw new Error("invalid");
            $(".popup-content", popupEl).hidden = true;
            $(".popup-success", popupEl).hidden = false;
            if (local) local.setItem(key + "_done", "1");
          })
          .catch(() => { err.hidden = false; })
          .finally(() => { btn.disabled = false; });
      });
    }
  }
})();
