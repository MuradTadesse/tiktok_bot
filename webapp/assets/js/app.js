/**
 * TikTok Report Helper - Advanced Web App
 * Created by Murad Tadesse
 * 
 * This file contains the core functionality for the TikTok Report Helper web app.
 * It integrates with the Telegram WebApp API and provides a modern, intuitive user
 * experience for reporting harmful TikTok accounts.
 */

// Initialize main application
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize Telegram WebApp
  const tg = window.Telegram.WebApp;
  tg.expand();
  
  // Apply theme
  ThemeManager.initialize();
  
  // Initialize components
  ProgressManager.initialize();
  CarouselManager.initialize();
  CopyManager.initialize();
  
  // Parse parameters
  const params = UrlManager.parseParams();
  const reportData = {
    targetAccount: params.account || '@effoyyt',
    reason: params.reason || 'Hate speech and hateful behaviors',
    campaignId: params.campaign || '1',
    description: params.description || 'This account consistently posts content containing hate speech targeting ethnic groups.'
  };
  
  // Update UI with target information
  UIManager.updateTargetInfo(reportData);
  
  // Setup navigation
  NavigationManager.initialize(reportData);
  
  // Add analytics tracking
  AnalyticsManager.trackPageView('report-webapp');
  
  // Log initialization
  console.log('TikTok Report WebApp initialized', { reportData });
  
  // Initialize splash screen
  SplashScreen.hide();
});

/**
 * Theme Manager - handles theme detection and application
 */
const ThemeManager = {
  initialize() {
    this.applyTelegramTheme();
    this.setupThemeToggle();
    this.applyPreferredTheme();
  },
  
  applyTelegramTheme() {
    const root = document.documentElement;
    const tg = window.Telegram.WebApp;
    
    if (!tg.themeParams) return;
    
    // Convert hex to rgb for CSS variables
    const hexToRgb = (hex) => {
      const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
      hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
      
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : null;
    };
    
    // Set RGB versions of colors for opacity support
    if (tg.themeParams.button_color) {
      root.style.setProperty('--tg-theme-button-color-rgb', hexToRgb(tg.themeParams.button_color));
    }
    
    if (tg.themeParams.text_color) {
      root.style.setProperty('--tg-theme-text-color-rgb', hexToRgb(tg.themeParams.text_color));
    }
    
    if (tg.themeParams.hint_color) {
      root.style.setProperty('--tg-theme-hint-color-rgb', hexToRgb(tg.themeParams.hint_color));
    }
    
    // Apply theme to main button
    const mainButton = tg.MainButton;
    if (mainButton) {
      mainButton.setParams({
        text: 'Continue',
        color: tg.themeParams.button_color,
        text_color: tg.themeParams.button_text_color,
        is_visible: false
      });
    }
  },
  
  setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark-theme');
      
      const isDark = document.body.classList.contains('dark-theme');
      localStorage.setItem('preferred-theme', isDark ? 'dark' : 'light');
      
      // Update toggle icon
      const icon = themeToggle.querySelector('.icon');
      if (isDark) {
        icon.innerHTML = '<path d="M12 3a9 9 0 1 0 9 9 9.1 9.1 0 0 0-9-9zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm0-12.5a1 1 0 0 0 1-1v-1a1 1 0 0 0-2 0v1a1 1 0 0 0 1 1zm0 13a1 1 0 0 0-1 1v1a1 1 0 0 0 2 0v-1a1 1 0 0 0-1-1zm7.4-10a1 1 0 0 0 .7-1.7l-.7-.7a1 1 0 0 0-1.4 1.4l.7.7a1 1 0 0 0 .7.3zM4.6 19.5a1 1 0 0 0-.7 1.7l.7.7a1 1 0 1 0 1.4-1.4l-.7-.7a1 1 0 0 0-.7-.3zM21 11h-1a1 1 0 0 0 0 2h1a1 1 0 0 0 0-2zM4 11H3a1 1 0 0 0 0 2h1a1 1 0 0 0 0-2zm15.4 8.5a1 1 0 0 0-1.4 1.4l.7.7a1 1 0 0 0 1.4-1.4zM4.6 4.5a1 1 0 0 0 .7-.3l.7-.7a1 1 0 0 0-1.4-1.4l-.7.7a1 1 0 0 0 .7 1.7z"/>';
      } else {
        icon.innerHTML = '<path d="M12.3 22h-.1a10.3 10.3 0 0 1-7.3-3.6A10.1 10.1 0 0 1 2 11a10.3 10.3 0 0 1 3.6-7.3A10.1 10.1 0 0 1 12 2h.1a1 1 0 0 1 .7.3 1 1 0 0 1 .3.7 5 5 0 0 0 .9 2.8 5.3 5.3 0 0 0 2.3 1.9 5 5 0 0 0 2.8.9 1 1 0 0 1 1 1 10.3 10.3 0 0 1-3.6 7.3A10.1 10.1 0 0 1 12.3 22zm-1.9-18a8.2 8.2 0 0 0-5.4 2.3A8.2 8.2 0 0 0 4 16.9a8.2 8.2 0 0 0 2.3 4.9 8.2 8.2 0 0 0 5.5 2.2h.5a8.2 8.2 0 0 0 5.3-3.5 8.2 8.2 0 0 0 2.2-5.8 7 7 0 0 1-7-7 8.2 8.2 0 0 0-2.4 1.3z"/>';
      }
      
      // Analytics
      AnalyticsManager.trackEvent('toggle_theme', { theme: isDark ? 'dark' : 'light' });
    });
  },
  
  applyPreferredTheme() {
    // Set initial theme based on preference
    const savedTheme = localStorage.getItem('preferred-theme');
    const themeToggle = document.getElementById('theme-toggle');
    
    if (savedTheme) {
      document.body.classList.toggle('dark-theme', savedTheme === 'dark');
      
      // Update toggle icon if element exists
      if (themeToggle) {
        const icon = themeToggle.querySelector('.icon');
        if (icon) {
          if (savedTheme === 'dark') {
            icon.innerHTML = '<path d="M12 3a9 9 0 1 0 9 9 9.1 9.1 0 0 0-9-9zm0 16a7 7 0 1 1 7-7 7 7 0 0 1-7 7zm0-12.5a1 1 0 0 0 1-1v-1a1 1 0 0 0-2 0v1a1 1 0 0 0 1 1zm0 13a1 1 0 0 0-1 1v1a1 1 0 0 0 2 0v-1a1 1 0 0 0-1-1zm7.4-10a1 1 0 0 0 .7-1.7l-.7-.7a1 1 0 0 0-1.4 1.4l.7.7a1 1 0 0 0 .7.3zM4.6 19.5a1 1 0 0 0-.7 1.7l.7.7a1 1 0 1 0 1.4-1.4l-.7-.7a1 1 0 0 0-.7-.3zM21 11h-1a1 1 0 0 0 0 2h1a1 1 0 0 0 0-2zM4 11H3a1 1 0 0 0 0 2h1a1 1 0 0 0 0-2zm15.4 8.5a1 1 0 0 0-1.4 1.4l.7.7a1 1 0 0 0 1.4-1.4zM4.6 4.5a1 1 0 0 0 .7-.3l.7-.7a1 1 0 0 0-1.4-1.4l-.7.7a1 1 0 0 0 .7 1.7z"/>';
          } else {
            icon.innerHTML = '<path d="M12.3 22h-.1a10.3 10.3 0 0 1-7.3-3.6A10.1 10.1 0 0 1 2 11a10.3 10.3 0 0 1 3.6-7.3A10.1 10.1 0 0 1 12 2h.1a1 1 0 0 1 .7.3 1 1 0 0 1 .3.7 5 5 0 0 0 .9 2.8 5.3 5.3 0 0 0 2.3 1.9 5 5 0 0 0 2.8.9 1 1 0 0 1 1 1 10.3 10.3 0 0 1-3.6 7.3A10.1 10.1 0 0 1 12.3 22zm-1.9-18a8.2 8.2 0 0 0-5.4 2.3A8.2 8.2 0 0 0 4 16.9a8.2 8.2 0 0 0 2.3 4.9 8.2 8.2 0 0 0 5.5 2.2h.5a8.2 8.2 0 0 0 5.3-3.5 8.2 8.2 0 0 0 2.2-5.8 7 7 0 0 1-7-7 8.2 8.2 0 0 0-2.4 1.3z"/>';
          }
        }
      }
    } else if (window.matchMedia) {
      // Use system preference if no saved preference
      const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
      document.body.classList.toggle('dark-theme', darkModeQuery.matches);
      
      // Listen for changes in system theme
      darkModeQuery.addEventListener('change', (e) => {
        if (!localStorage.getItem('preferred-theme')) {
          document.body.classList.toggle('dark-theme', e.matches);
        }
      });
    }
  }
};

/**
 * Progress Manager - handles progress bar and steps
 */
const ProgressManager = {
  initialize() {
    this.progressBar = document.getElementById('progress-bar');
    this.progressSteps = document.querySelectorAll('.progress-step');
    
    // Set initial progress
    this.update(1, this.progressSteps.length);
    
    // Add animations to progress steps
    this.progressSteps.forEach((step, index) => {
      step.style.animationDelay = `${index * 0.1}s`;
    });
  },
  
  update(currentStep, totalSteps) {
    if (!this.progressBar || !this.progressSteps.length) return;
    
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    this.progressBar.style.width = `${progress}%`;
    
    this.progressSteps.forEach((step, index) => {
      const stepNum = index + 1;
      step.classList.remove('active', 'completed');
      
      if (stepNum < currentStep) {
        step.classList.add('completed');
        step.innerHTML = '<svg class="icon" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
      } else if (stepNum === currentStep) {
        step.classList.add('active');
      }
    });
  }
};

/**
 * Carousel Manager - handles image carousels
 */
const CarouselManager = {
  initialize() {
    this.carousels = document.querySelectorAll('.carousel');
    
    this.carousels.forEach(carousel => {
      const container = carousel.querySelector('.carousel-container');
      const slides = carousel.querySelectorAll('.carousel-slide');
      const dotsContainer = carousel.querySelector('.carousel-dots');
      const prevBtn = carousel.querySelector('.carousel-prev');
      const nextBtn = carousel.querySelector('.carousel-next');
      
      if (!container || !slides.length) return;
      
      // Create dots
      if (dotsContainer) {
        slides.forEach((_, index) => {
          const dot = document.createElement('span');
          dot.classList.add('carousel-dot');
          if (index === 0) dot.classList.add('active');
          dot.addEventListener('click', () => this.goToSlide(carousel, index));
          dotsContainer.appendChild(dot);
        });
      }
      
      // Set initial state
      carousel.currentSlide = 0;
      this.updateCarousel(carousel);
      
      // Add event listeners
      if (prevBtn) prevBtn.addEventListener('click', () => this.navigate(carousel, -1));
      if (nextBtn) nextBtn.addEventListener('click', () => this.navigate(carousel, 1));
      
      // Add swipe support
      let touchStartX = 0;
      let touchEndX = 0;
      
      container.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });
      
      container.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        this.handleSwipe(carousel, touchStartX, touchEndX);
      }, { passive: true });
    });
  },
  
  handleSwipe(carousel, touchStartX, touchEndX) {
    const threshold = 50;
    if (touchStartX - touchEndX > threshold) {
      this.navigate(carousel, 1); // Swipe left
    } else if (touchEndX - touchStartX > threshold) {
      this.navigate(carousel, -1); // Swipe right
    }
  },
  
  navigate(carousel, direction) {
    const container = carousel.querySelector('.carousel-container');
    const slides = carousel.querySelectorAll('.carousel-slide');
    
    if (!container || !slides.length) return;
    
    carousel.currentSlide = (carousel.currentSlide + direction + slides.length) % slides.length;
    this.updateCarousel(carousel);
    
    // Analytics
    AnalyticsManager.trackEvent('carousel_navigate', {
      direction: direction > 0 ? 'next' : 'prev',
      slide_index: carousel.currentSlide
    });
  },
  
  goToSlide(carousel, index) {
    carousel.currentSlide = index;
    this.updateCarousel(carousel);
    
    // Analytics
    AnalyticsManager.trackEvent('carousel_go_to_slide', {
      slide_index: index
    });
  },
  
  updateCarousel(carousel) {
    const container = carousel.querySelector('.carousel-container');
    const dots = carousel.querySelectorAll('.carousel-dot');
    
    if (!container) return;
    
    container.style.transform = `translateX(-${carousel.currentSlide * 100}%)`;
    
    // Update dots
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === carousel.currentSlide);
    });
  }
};

/**
 * Copy Manager - handles copy to clipboard functionality
 */
const CopyManager = {
  initialize() {
    this.copyButtons = document.querySelectorAll('.copy-btn');
    
    this.copyButtons.forEach(button => {
      button.addEventListener('click', () => {
        const parent = button.parentNode;
        const content = parent.querySelector('.copy-content');
        
        if (!content) return;
        
        // Copy text to clipboard
        navigator.clipboard.writeText(content.textContent)
          .then(() => {
            this.showCopiedTooltip(button);
            
            // Analytics
            AnalyticsManager.trackEvent('text_copied', {
              text_length: content.textContent.length
            });
          })
          .catch(err => {
            console.error('Could not copy text:', err);
            
            // Fallback copy method for older browsers
            this.fallbackCopy(content.textContent);
          });
      });
    });
  },
  
  showCopiedTooltip(button) {
    const tooltip = button.querySelector('.tooltip');
    if (!tooltip) return;
    
    const originalText = tooltip.textContent;
    tooltip.textContent = 'Copied!';
    
    setTimeout(() => {
      tooltip.textContent = originalText;
    }, 2000);
  },
  
  fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      document.execCommand('copy');
    } catch (err) {
      console.error('Fallback: Oops, unable to copy', err);
    }
    
    document.body.removeChild(textArea);
  }
};

/**
 * URL Manager - handles URL parameters
 */
const UrlManager = {
  parseParams() {
    const query = window.location.search.substring(1);
    const tg = window.Telegram.WebApp;
    
    // Check Telegram WebApp start params first (they take precedence)
    if (tg.initDataUnsafe && tg.initDataUnsafe.start_param) {
      try {
        // Try to parse as JSON
        return JSON.parse(decodeURIComponent(tg.initDataUnsafe.start_param));
      } catch (e) {
        // If not JSON, try as URL params
        return this.parseQueryString(tg.initDataUnsafe.start_param);
      }
    }
    
    // Fall back to URL query params
    return this.parseQueryString(query);
  },
  
  parseQueryString(queryString) {
    const params = {};
    const queries = queryString.split('&');
    
    queries.forEach(query => {
      const [key, value] = query.split('=');
      if (key && value) {
        params[decodeURIComponent(key)] = decodeURIComponent(value);
      }
    });
    
    return params;
  }
};

/**
 * UI Manager - handles UI updates
 */
const UIManager = {
  updateTargetInfo(data) {
    document.querySelectorAll('[data-target="account"]').forEach(el => {
      el.textContent = data.targetAccount;
    });
    
    document.querySelectorAll('[data-target="reason"]').forEach(el => {
      el.textContent = data.reason;
    });
    
    document.querySelectorAll('[data-target="description"]').forEach(el => {
      el.textContent = data.description || '';
    });
    
    // Update the TikTok URL
    const tiktokUrl = `https://www.tiktok.com/${data.targetAccount.replace('@', '')}`;
    
    document.querySelectorAll('[data-href="tiktok"]').forEach(el => {
      el.href = tiktokUrl;
    });
    
    // Set avatar initials
    document.querySelectorAll('.target-avatar-text').forEach(el => {
      el.textContent = data.targetAccount.replace('@', '').charAt(0).toUpperCase();
    });
  },
  
  updateUIForStep(stepNumber) {
    // Additional UI updates based on current step
    if (stepNumber === 1) {
      // First step - intro animations
      const animatedElements = document.querySelectorAll('[data-animation]');
      
      animatedElements.forEach(el => {
        el.classList.add('animate');
      });
    }
    
    if (stepNumber === 6) {
      // Last step - show confetti
      EffectsManager.showConfetti();
    }
  }
};

/**
 * Navigation Manager - handles step navigation
 */
const NavigationManager = {
  initialize(reportData) {
    this.reportData = reportData;
    this.steps = document.querySelectorAll('.step');
    this.currentStep = 1;
    this.totalSteps = this.steps.length;
    
    // Show initial step
    this.showStep(this.currentStep);
    
    // Set up next buttons
    document.querySelectorAll('[data-action="next"]').forEach(button => {
      button.addEventListener('click', () => {
        this.nextStep();
      });
    });
    
    // Set up back buttons
    document.querySelectorAll('[data-action="back"]').forEach(button => {
      button.addEventListener('click', () => {
        this.prevStep();
      });
    });
    
    // Set up complete button
    document.querySelectorAll('[data-action="complete"]').forEach(button => {
      button.addEventListener('click', () => {
        this.completeReport();
      });
    });
    
    // Set up Telegram MainButton if available
    const tg = window.Telegram.WebApp;
    if (tg.MainButton) {
      tg.MainButton.onClick(() => {
        if (this.currentStep === this.totalSteps) {
          this.completeReport();
        } else {
          this.nextStep();
        }
      });
    }
  },
  
  showStep(step) {
    this.steps.forEach((stepEl, index) => {
      stepEl.classList.toggle('active', index + 1 === step);
      
      // Add entrance animations
      if (index + 1 === step) {
        const animatedElements = stepEl.querySelectorAll('[data-animation]');
        animatedElements.forEach(el => {
          el.classList.add('animate');
        });
      }
    });
    
    // Update progress bar
    ProgressManager.update(step, this.totalSteps);
    
    // Update UI elements for this step
    UIManager.updateUIForStep(step);
    
    // Update Main Button text based on step
    const tg = window.Telegram.WebApp;
    if (tg.MainButton) {
      if (step === this.totalSteps) {
        tg.MainButton.setText('Complete Reporting');
      } else {
        tg.MainButton.setText('Continue');
      }
      
      tg.MainButton.show();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Analytics
    AnalyticsManager.trackEvent('view_step', { step_number: step });
  },
  
  nextStep() {
    if (this.currentStep < this.totalSteps) {
      this.currentStep++;
      this.showStep(this.currentStep);
      
      // Analytics
      AnalyticsManager.trackEvent('next_step', { 
        from_step: this.currentStep - 1, 
        to_step: this.currentStep 
      });
    }
  },
  
  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.showStep(this.currentStep);
      
      // Analytics
      AnalyticsManager.trackEvent('prev_step', { 
        from_step: this.currentStep + 1, 
        to_step: this.currentStep 
      });
    }
  },
  
  completeReport() {
    // Send data back to Telegram WebApp
    const tg = window.Telegram.WebApp;
    
    // Create a payload with all necessary data
    const payload = {
      action: 'report_completed',
      target: this.reportData.targetAccount,
      reason: this.reportData.reason,
      campaign: this.reportData.campaignId,
      timestamp: new Date().toISOString(),
      user_agent: navigator.userAgent,
      screen_size: `${window.innerWidth}x${window.innerHeight}`
    };
    
    // Show celebration effects
    EffectsManager.showConfetti();
    
    // Analytics
    AnalyticsManager.trackEvent('complete_report', { 
      target_account: this.reportData.targetAccount, 
      reason: this.reportData.reason 
    });
    
    // Send data and close WebApp
    tg.sendData(JSON.stringify(payload));
    
    // Close WebApp after a slight delay
    setTimeout(() => {
      tg.close();
    }, 1500);
  }
};

/**
 * Effects Manager - handles visual effects
 */
const EffectsManager = {
  showConfetti() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#00ffff', '#ff00ff', '#ffffff'];
    const numConfetti = 150;
    
    for (let i = 0; i < numConfetti; i++) {
      this.createConfettiPiece(colors[Math.floor(Math.random() * colors.length)]);
    }
  },
  
  createConfettiPiece(color) {
    const confetti = document.createElement('div');
    confetti.classList.add('confetti');
    
    // Random properties
    const size = Math.random() * 10 + 5;
    const angle = Math.random() * 360;
    const x = Math.random() * window.innerWidth;
    const y = -20;
    const duration = Math.random() * 3 + 2;
    const delay = Math.random() * 0.5;
    
    confetti.style.width = `${size}px`;
    confetti.style.height = `${size}px`;
    confetti.style.backgroundColor = color;
    confetti.style.transform = `rotate(${angle}deg)`;
    confetti.style.left = `${x}px`;
    confetti.style.top = `${y}px`;
    confetti.style.opacity = '1';
    confetti.style.transition = `transform ${duration}s ease-out, top ${duration}s ease-in, opacity ${duration/4}s ${duration*0.75}s ease-out`;
    confetti.style.transitionDelay = `${delay}s`;
    
    document.body.appendChild(confetti);
    
    // Trigger animation
    setTimeout(() => {
      confetti.style.transform = `rotate(${angle + 360 * 3}deg)`;
      confetti.style.top = `${window.innerHeight + 100}px`;
      confetti.style.opacity = '0';
    }, 50);
    
    // Remove after animation completes
    setTimeout(() => {
      confetti.remove();
    }, duration * 1000 + delay * 1000 + 1000);
  }
};

/**
 * Analytics Manager - handles event tracking
 */
const AnalyticsManager = {
  trackPageView(page) {
    console.log('Track page view:', page);
    // Implementation would connect to your actual analytics system
    
    // Example GA4 implementation:
    if (typeof gtag !== 'undefined') {
      gtag('event', 'page_view', {
        page_title: document.title,
        page_location: window.location.href,
        page_path: page
      });
    }
  },
  
  trackEvent(event, params) {
    console.log('Track event:', event, params);
    // Implementation would connect to your actual analytics system
    
    // Example GA4 implementation:
    if (typeof gtag !== 'undefined') {
      gtag('event', event, params);
    }
  }
};

/**
 * Splash Screen - handles initial loading screen
 */
const SplashScreen = {
  hide() {
    const splash = document.getElementById('splash-screen');
    if (splash) {
      splash.classList.add('fade-out');
      setTimeout(() => {
        splash.remove();
      }, 500);
    }
  }
};
