/* ═══════════════════════════════════════════════════════════
   InstaCard Landing Page — JavaScript
   - Smooth scroll navigation
   - Scroll-triggered animations (IntersectionObserver)
   - Mobile menu toggle
   - Email form validation
   - Counter animation for social proof
   - Header scroll state
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ─── HEADER SCROLL STATE ─────────────────────────────── */
  const header = document.getElementById('header');

  const handleHeaderScroll = () => {
    if (window.scrollY > 20) {
      header.classList.add('is-scrolled');
    } else {
      header.classList.remove('is-scrolled');
    }
  };

  window.addEventListener('scroll', handleHeaderScroll, { passive: true });
  handleHeaderScroll(); // Initial check


  /* ─── MOBILE MENU TOGGLE ──────────────────────────────── */
  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileLinks = document.querySelectorAll('.mobile-menu__link');

  const toggleMenu = () => {
    const isOpen = mobileMenu.classList.toggle('is-open');
    menuToggle.classList.toggle('is-active');
    menuToggle.setAttribute('aria-expanded', isOpen);
    mobileMenu.setAttribute('aria-hidden', !isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  };

  menuToggle.addEventListener('click', toggleMenu);

  mobileLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (mobileMenu.classList.contains('is-open')) {
        toggleMenu();
      }
    });
  });


  /* ─── SMOOTH SCROLL FOR ANCHOR LINKS ──────────────────── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;

      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });


  /* ─── SCROLL-TRIGGERED ANIMATIONS ─────────────────────── */
  const animateElements = document.querySelectorAll('.animate-on-scroll');

  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -60px 0px',
    threshold: 0.1
  };

  const animationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        animationObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);

  animateElements.forEach(el => animationObserver.observe(el));


  /* ─── COUNTER ANIMATION (Social Proof Numbers) ────────── */
  const counterElements = document.querySelectorAll('.social-proof__number[data-target]');

  const animateCounter = (element) => {
    const target = parseInt(element.dataset.target, 10);
    const duration = 2000;
    const start = performance.now();

    const updateCounter = (currentTime) => {
      const elapsed = currentTime - start;
      const progress = Math.min(elapsed / duration, 1);

      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);

      const current = Math.round(eased * target);

      if (target >= 1000) {
        element.textContent = current.toLocaleString('en-US');
      } else {
        element.textContent = current;
      }

      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      }
    };

    requestAnimationFrame(updateCounter);
  };

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counterElements.forEach(el => counterObserver.observe(el));


  /* ─── EMAIL FORM VALIDATION & SUBMISSION ──────────────── */
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const handleFormSubmit = (formId, inputId, buttonId) => {
    const form = document.getElementById(formId);
    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);

    if (!form || !input || !button) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const email = input.value.trim();

      // Reset states
      input.classList.remove('is-error', 'is-success');

      if (!email) {
        input.classList.add('is-error');
        input.focus();
        shakeElement(input.closest('.hero__input-wrapper, .footer__input-wrapper'));
        return;
      }

      if (!emailRegex.test(email)) {
        input.classList.add('is-error');
        input.focus();
        shakeElement(input.closest('.hero__input-wrapper, .footer__input-wrapper'));
        return;
      }

      // Simulate submission
      const originalText = button.innerHTML;
      button.innerHTML = `
        <svg class="spinner" width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2" stroke-dasharray="40 60" stroke-linecap="round">
            <animateTransform attributeName="transform" type="rotate" from="0 10 10" to="360 10 10" dur="0.8s" repeatCount="indefinite"/>
          </circle>
        </svg>
        Sending...
      `;
      button.style.pointerEvents = 'none';

      setTimeout(() => {
        input.classList.add('is-success');
        input.value = '';
        button.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M16.667 5L7.5 14.167 3.333 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          You're on the list!
        `;
        button.classList.add('is-success');

        // Reset after 3 seconds
        setTimeout(() => {
          button.innerHTML = originalText;
          button.style.pointerEvents = '';
          button.classList.remove('is-success');
          input.classList.remove('is-success');
        }, 3000);
      }, 1200);
    });
  };

  // Shake animation for invalid input
  const shakeElement = (element) => {
    if (!element) return;
    element.style.animation = 'shake 0.4s ease-out';
    element.addEventListener('animationend', () => {
      element.style.animation = '';
    }, { once: true });
  };

  // Add shake keyframes dynamically
  const shakeKeyframes = `
    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20% { transform: translateX(-6px); }
      40% { transform: translateX(6px); }
      60% { transform: translateX(-4px); }
      80% { transform: translateX(4px); }
    }
  `;
  const styleEl = document.createElement('style');
  styleEl.textContent = shakeKeyframes;
  document.head.appendChild(styleEl);

  // Initialize both forms
  handleFormSubmit('hero-form', 'hero-email', 'hero-submit');
  handleFormSubmit('footer-form', 'footer-email', 'footer-submit');


  /* ─── ACTIVE NAV LINK HIGHLIGHT ───────────────────────── */
  const navLinks = document.querySelectorAll('.header__nav-link');
  const sections = document.querySelectorAll('section[id]');

  const highlightNav = () => {
    const scrollPos = window.scrollY + 100;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');

      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('is-active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('is-active');
          }
        });
      }
    });
  };

  window.addEventListener('scroll', highlightNav, { passive: true });


  /* ─── INTERACTIVE WALLET & NFC SIMULATOR (BOVAcard + CloudCard Style) ─── */
  const walletStage = document.getElementById('wallet-stage');
  const stepCards = document.querySelectorAll('.wallet-step-card');
  const autoPlayBtn = document.getElementById('wallet-auto-play');
  const autoPlayText = document.getElementById('wallet-auto-text');
  
  let currentWalletStep = 1;
  let autoPlayTimer = null;
  let isAutoPlaying = false;

  const setWalletStep = (step) => {
    currentWalletStep = step;
    if (walletStage) {
      walletStage.setAttribute('data-active-step', step);
    }

    stepCards.forEach(card => {
      const cardStep = parseInt(card.getAttribute('data-step'), 10);
      if (cardStep === step) {
        card.classList.add('is-active');
      } else {
        card.classList.remove('is-active');
      }
    });
  };

  // Step card clicks & keyboard navigation
  stepCards.forEach(card => {
    card.addEventListener('click', () => {
      stopAutoPlay();
      const step = parseInt(card.getAttribute('data-step'), 10);
      setWalletStep(step);
    });

    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        stopAutoPlay();
        const step = parseInt(card.getAttribute('data-step'), 10);
        setWalletStep(step);
      }
    });
  });

  // Auto-play demo cycle
  const startAutoPlay = () => {
    isAutoPlaying = true;
    if (autoPlayBtn) {
      autoPlayBtn.classList.add('is-playing');
      if (autoPlayText) autoPlayText.textContent = 'Pause Demo';
    }
    
    autoPlayTimer = setInterval(() => {
      const nextStep = currentWalletStep >= 3 ? 1 : currentWalletStep + 1;
      setWalletStep(nextStep);
    }, 3200);
  };

  const stopAutoPlay = () => {
    isAutoPlaying = false;
    if (autoPlayTimer) {
      clearInterval(autoPlayTimer);
      autoPlayTimer = null;
    }
    if (autoPlayBtn) {
      autoPlayBtn.classList.remove('is-playing');
      if (autoPlayText) autoPlayText.textContent = 'Play Demo Animation';
    }
  };

  if (autoPlayBtn) {
    autoPlayBtn.addEventListener('click', () => {
      if (isAutoPlaying) {
        stopAutoPlay();
      } else {
        startAutoPlay();
      }
    });
  }

  // Scroll-driven triggering when user scrolls into the interactive-wallet section
  const interactiveSection = document.getElementById('interactive-wallet');
  if (interactiveSection) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (!isAutoPlaying) {
            const rect = interactiveSection.getBoundingClientRect();
            const sectionHeight = rect.height;
            const windowHeight = window.innerHeight;

            // When section is in visible viewport focus
            if (rect.top <= windowHeight * 0.45 && rect.bottom >= windowHeight * 0.45) {
              const progress = (windowHeight * 0.45 - rect.top) / sectionHeight;
              if (progress < 0.35) {
                if (currentWalletStep !== 1) setWalletStep(1);
              } else if (progress < 0.70) {
                if (currentWalletStep !== 2) setWalletStep(2);
              } else {
                if (currentWalletStep !== 3) setWalletStep(3);
              }
            }
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // Initialize Step 1
  setWalletStep(1);


  /* ─── SMART OCR SCANNER SIMULATION (CamCard Style) ─── */
  const ocrSection = document.getElementById('ocr-scanner');
  if (ocrSection) {
    const leadAvatar = ocrSection.querySelector('.scanner-lead-card__avatar');
    const leadName = ocrSection.querySelector('.scanner-lead-card__info h5');
    const leadTitle = ocrSection.querySelector('.scanner-lead-card__info p');

    const sampleLeads = [
      { avatar: 'SJ', name: 'Sarah Jenkins', role: 'Managing Director · Meridian Partners', color: 'linear-gradient(135deg, #F59E0B, #EC4899)' },
      { avatar: 'KT', name: 'Kenji Tanaka (田中 健二)', role: 'VP of Deep Learning · Tokyo', color: 'linear-gradient(135deg, #0EA5E9, #6366F1)' },
      { avatar: 'ER', name: 'Elena Rostova', role: 'Executive Creative Director · Berlin', color: 'linear-gradient(135deg, #10B981, #0EA5E9)' },
      { avatar: 'OA', name: 'Omar Al-Mansoor (عمر المنصور)', role: 'Head of Investments · Dubai', color: 'linear-gradient(135deg, #F59E0B, #D97706)' },
      { avatar: 'DC', name: 'Dr. David Chen', role: 'Chief Medical Officer · San Francisco', color: 'linear-gradient(135deg, #8B5CF6, #EC4899)' }
    ];

    let leadIndex = 0;
    setInterval(() => {
      leadIndex = (leadIndex + 1) % sampleLeads.length;
      const current = sampleLeads[leadIndex];

      const leadCard = ocrSection.querySelector('.scanner-lead-card');
      if (leadCard) {
        leadCard.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
        leadCard.style.opacity = '0.35';
        leadCard.style.transform = 'scale(0.96)';
        
        setTimeout(() => {
          if (leadAvatar) {
            leadAvatar.textContent = current.avatar;
            leadAvatar.style.background = current.color;
          }
          if (leadName) leadName.textContent = current.name;
          if (leadTitle) leadTitle.textContent = current.role;

          leadCard.style.opacity = '1';
          leadCard.style.transform = 'scale(1)';
        }, 250);
      }
    }, 4200);
  }

  /* ─── SECTION 2: CAMCARD HERO HANDS SCROLL MEET (GSAP ScrollTrigger) ─── */
  // AI AGENT NOTE: Hiệu ứng 2 bàn tay xích lại gần nhau khi cuộn trang
  function initCamCardHandsScroll() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
      console.warn('GSAP or ScrollTrigger not loaded');
      return;
    }

    const heroStage = document.getElementById('camcard-hands-stage');
    if (!heroStage) return;

    gsap.registerPlugin(ScrollTrigger);

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: heroStage,
        start: 'top 85%',
        end: 'bottom 45%',
        scrub: 1.2,
      }
    });

    // AI AGENT NOTE: Bàn tay trái từ vị trí biên trái trượt về giữa để chạm tay phải
    tl.to('.camcard-hand--left', {
      xPercent: 50,
      rotation: 0,
      ease: 'power2.out'
    });

    // AI AGENT NOTE: Bàn tay phải từ vị trí biên phải trượt về giữa đồng thời ("<")
    tl.to('.camcard-hand--right', {
      xPercent: -50,
      rotation: 0,
      ease: 'power2.out'
    }, '<');

    // AI AGENT NOTE: Khi 2 điện thoại vừa chạm nhau, đèn kết nối NFC bừng sáng
    tl.to('#camcard-connect-badge', {
      opacity: 1,
      scale: 1,
      duration: 0.35,
      ease: 'back.out(1.7)'
    }, '-=0.25');
  }

  initCamCardHandsScroll();

});

