/**
 * TikTok Report Helper - Carousel Component
 * Created by Murad Tadesse
 * 
 * Advanced carousel functionality for image galleries and step instructions.
 * Provides smooth transitions, touch support, and keyboard navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize all carousels on the page
  const carousels = document.querySelectorAll('.carousel');
  
  carousels.forEach(carousel => {
    new Carousel(carousel);
  });
});

/**
 * Carousel class for handling image galleries
 */
class Carousel {
  constructor(element) {
    // Element references
    this.carousel = element;
    this.container = element.querySelector('.carousel-container');
    this.slides = element.querySelectorAll('.carousel-slide');
    this.dotsContainer = element.querySelector('.carousel-dots');
    this.prevBtn = element.querySelector('.carousel-prev');
    this.nextBtn = element.querySelector('.carousel-next');
    
    // State
    this.currentIndex = 0;
    this.slidesCount = this.slides.length;
    this.animating = false;
    this.autoplayInterval = null;
    
    // Options (can be set via data attributes)
    this.autoplay = this.carousel.dataset.autoplay === 'true';
    this.autoplaySpeed = parseInt(this.carousel.dataset.autoplaySpeed) || 5000;
    this.pauseOnHover = this.carousel.dataset.pauseOnHover !== 'false';
    this.loop = this.carousel.dataset.loop !== 'false';
    this.animation = this.carousel.dataset.animation || 'slide'; // slide, fade
    
    // Initialize only if we have slides
    if (this.slidesCount > 0) {
      this.init();
    }
  }
  
  /**
   * Initialize the carousel
   */
  init() {
    // Create dots if container exists
    if (this.dotsContainer) {
      this.createDots();
    }
    
    // Add event listeners
    this.addEventListeners();
    
    // Set initial state
    this.goToSlide(0);
    
    // Start autoplay if enabled
    if (this.autoplay) {
      this.startAutoplay();
    }
    
    // Add animation classes based on animation type
    if (this.animation === 'fade') {
      this.carousel.classList.add('carousel-fade');
    }
  }
  
  /**
   * Create navigation dots
   */
  createDots() {
    this.dotsContainer.innerHTML = '';
    
    for (let i = 0; i < this.slidesCount; i++) {
      const dot = document.createElement('span');
      dot.classList.add('carousel-dot');
      dot.setAttribute('data-index', i);
      
      if (i === 0) {
        dot.classList.add('active');
      }
      
      this.dotsContainer.appendChild(dot);
    }
  }
  
  /**
   * Add all event listeners
   */
  addEventListeners() {
    // Navigation button events
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.prev();
      });
    }
    
    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.next();
      });
    }
    
    // Dot navigation events
    if (this.dotsContainer) {
      this.dotsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('carousel-dot')) {
          const index = parseInt(e.target.getAttribute('data-index'));
          this.goToSlide(index);
        }
      });
    }
    
    // Touch events for swipe
    let touchStartX = 0;
    let touchEndX = 0;
    const threshold = 50; // Minimum distance required for swipe
    
    this.carousel.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    this.carousel.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      
      // Detect swipe direction and navigate
      if (touchStartX - touchEndX > threshold) {
        this.next();
      } else if (touchEndX - touchStartX > threshold) {
        this.prev();
      }
    }, { passive: true });
    
    // Keyboard navigation when carousel is focused
    this.carousel.tabIndex = 0;
    this.carousel.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        this.prev();
      } else if (e.key === 'ArrowRight') {
        this.next();
      }
    });
    
    // Pause autoplay on hover if enabled
    if (this.autoplay && this.pauseOnHover) {
      this.carousel.addEventListener('mouseenter', () => {
        this.stopAutoplay();
      });
      
      this.carousel.addEventListener('mouseleave', () => {
        this.startAutoplay();
      });
    }
    
    // Resize event for responsive adjustments
    window.addEventListener('resize', this.debouncedResize.bind(this));
  }
  
  /**
   * Navigate to the previous slide
   */
  prev() {
    if (this.animating) return;
    
    let index = this.currentIndex - 1;
    
    if (index < 0) {
      if (this.loop) {
        index = this.slidesCount - 1;
      } else {
        return;
      }
    }
    
    this.goToSlide(index);
  }
  
  /**
   * Navigate to the next slide
   */
  next() {
    if (this.animating) return;
    
    let index = this.currentIndex + 1;
    
    if (index >= this.slidesCount) {
      if (this.loop) {
        index = 0;
      } else {
        return;
      }
    }
    
    this.goToSlide(index);
  }
  
  /**
   * Go to a specific slide
   */
  goToSlide(index) {
    if (this.animating || index === this.currentIndex) return;
    
    this.animating = true;
    const prevIndex = this.currentIndex;
    this.currentIndex = index;
    
    // Update container position
    if (this.animation === 'fade') {
      // For fade animation
      this.slides[prevIndex].classList.remove('active');
      this.slides[this.currentIndex].classList.add('active');
    } else {
      // For slide animation
      this.container.style.transform = `translateX(-${index * 100}%)`;
    }
    
    // Update active dot
    if (this.dotsContainer) {
      const dots = this.dotsContainer.querySelectorAll('.carousel-dot');
      dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
      });
    }
    
    // Reset autoplay timer
    if (this.autoplay) {
      this.restartAutoplay();
    }
    
    // Reset animating state after transition
    setTimeout(() => {
      this.animating = false;
    }, 300); // Match transition duration
    
    // Trigger custom event
    this.carousel.dispatchEvent(new CustomEvent('carousel:slide-changed', {
      detail: {
        currentIndex: this.currentIndex,
        previousIndex: prevIndex
      }
    }));
  }
  
  /**
   * Start autoplay
   */
  startAutoplay() {
    if (this.autoplayInterval) return;
    
    this.autoplayInterval = setInterval(() => {
      this.next();
    }, this.autoplaySpeed);
  }
  
  /**
   * Stop autoplay
   */
  stopAutoplay() {
    if (this.autoplayInterval) {
      clearInterval(this.autoplayInterval);
      this.autoplayInterval = null;
    }
  }
  
  /**
   * Restart autoplay
   */
  restartAutoplay() {
    this.stopAutoplay();
    this.startAutoplay();
  }
  
  /**
   * Handle resize events (debounced)
   */
  debouncedResize() {
    clearTimeout(this.resizeTimer);
    this.resizeTimer = setTimeout(() => {
      this.refreshCarousel();
    }, 250);
  }
  
  /**
   * Refresh carousel calculation and positioning
   */
  refreshCarousel() {
    // Reset the position to current slide
    if (this.animation !== 'fade') {
      this.container.style.transform = `translateX(-${this.currentIndex * 100}%)`;
    }
  }
}

/**
 * Create a global carousel API for manual control
 */
window.CarouselAPI = {
  instances: {},
  
  /**
   * Register a carousel instance
   */
  register(id, carouselInstance) {
    this.instances[id] = carouselInstance;
  },
  
  /**
   * Get a carousel instance by its ID
   */
  get(id) {
    return this.instances[id];
  },
  
  /**
   * Go to a specific slide in a carousel
   */
  goToSlide(id, index) {
    const carousel = this.get(id);
    if (carousel) {
      carousel.goToSlide(index);
    }
  },
  
  /**
   * Go to the next slide in a carousel
   */
  next(id) {
    const carousel = this.get(id);
    if (carousel) {
      carousel.next();
    }
  },
  
  /**
   * Go to the previous slide in a carousel
   */
  prev(id) {
    const carousel = this.get(id);
    if (carousel) {
      carousel.prev();
    }
  }
};
