/**
 * TikTok Report Helper - Animations
 * Created by Murad Tadesse
 * 
 * Advanced animations for the TikTok Report Helper web app.
 * This file handles all animations, transitions, and interactive visual effects
 * to create an engaging and polished user experience.
 */

// Initialize animations when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Initialize animation observers
  AnimationManager.initialize();
  
  // Set up scroll animations
  ScrollAnimations.initialize();
  
  // Initialize typing animations
  TypingAnimations.initialize();
  
  // Initialize hover effects
  HoverEffects.initialize();
  
  // Initialize ripple effects for buttons
  RippleEffects.initialize();
});

/**
 * Animation Manager - handles the main animation logic
 */
const AnimationManager = {
  initialize() {
    // Set up animation observer for elements that should animate when visible
    this.setupIntersectionObserver();
    
    // Trigger initial animations for visible elements
    this.animateVisibleElements();
    
    // Set up staggered animations
    this.setupStaggeredAnimations();
  },
  
  setupIntersectionObserver() {
    // Options for the observer
    const options = {
      root: null, // relative to viewport
      rootMargin: '0px',
      threshold: 0.1 // trigger when 10% of the element is visible
    };
    
    // Create observer
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target;
          element.classList.add('animate');
          
          // Unobserve after animation has started
          this.observer.unobserve(element);
        }
      });
    }, options);
    
    // Observe all elements with data-animation attribute
    document.querySelectorAll('[data-animation]').forEach(element => {
      this.observer.observe(element);
    });
  },
  
  animateVisibleElements() {
    // Animate all elements that are already visible on load
    document.querySelectorAll('[data-animation]').forEach(element => {
      if (this.isElementInViewport(element)) {
        element.classList.add('animate');
        
        // Unobserve if it's being observed
        if (this.observer) {
          this.observer.unobserve(element);
        }
      }
    });
  },
  
  setupStaggeredAnimations() {
    // Set up staggered animations for lists and grids
    document.querySelectorAll('.stagger-reveal').forEach(container => {
      const children = container.children;
      const isVisible = this.isElementInViewport(container);
      
      if (isVisible) {
        container.classList.add('animate');
      } else {
        // Observe the container
        this.observer.observe(container);
      }
    });
  },
  
  isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    
    return (
      rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.left <= (window.innerWidth || document.documentElement.clientWidth) &&
      rect.bottom >= 0 &&
      rect.right >= 0
    );
  }
};

/**
 * Scroll Animations - handles animations triggered by scrolling
 */
const ScrollAnimations = {
  initialize() {
    this.lastScrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Add parallax effects
    this.setupParallaxEffects();
    
    // Add scroll direction classes to the body
    this.setupScrollDirectionClasses();
    
    // Add progress indicators for reading
    this.setupScrollProgress();
  },
  
  setupParallaxEffects() {
    const parallaxElements = document.querySelectorAll('[data-parallax]');
    
    if (parallaxElements.length > 0) {
      window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        parallaxElements.forEach(element => {
          const speed = parseFloat(element.getAttribute('data-parallax')) || 0.5;
          element.style.transform = `translateY(${scrollTop * speed}px)`;
        });
      }, { passive: true });
    }
  },
  
  setupScrollDirectionClasses() {
    window.addEventListener('scroll', () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      
      // Compare current scroll position with the previous one
      if (scrollTop > this.lastScrollTop) {
        document.body.classList.add('scroll-down');
        document.body.classList.remove('scroll-up');
      } else {
        document.body.classList.add('scroll-up');
        document.body.classList.remove('scroll-down');
      }
      
      this.lastScrollTop = scrollTop;
    }, { passive: true });
  },
  
  setupScrollProgress() {
    const progressBar = document.getElementById('scroll-progress');
    
    if (progressBar) {
      window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollPercentage = (scrollTop / scrollHeight) * 100;
        
        progressBar.style.width = `${scrollPercentage}%`;
      }, { passive: true });
    }
  }
};

/**
 * Typing Animations - creates typewriter-like effects
 */
const TypingAnimations = {
  initialize() {
    document.querySelectorAll('[data-typing]').forEach(element => {
      this.setupTypingAnimation(element);
    });
  },
  
  setupTypingAnimation(element) {
    // Store the original text
    const originalText = element.textContent;
    
    // Clear the original text
    element.textContent = '';
    
    // Add a cursor
    const cursor = document.createElement('span');
    cursor.className = 'typewriter-cursor';
    cursor.textContent = '|';
    element.appendChild(cursor);
    
    // Set typing speed
    const speed = parseInt(element.getAttribute('data-typing')) || 50;
    
    // Start typing animation when element is in viewport
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.typeText(element, originalText, cursor, 0, speed);
          observer.unobserve(element);
        }
      });
    }, { threshold: 0.5 });
    
    observer.observe(element);
  },
  
  typeText(element, text, cursor, index, speed) {
    if (index < text.length) {
      // Insert next character
      element.insertBefore(document.createTextNode(text.charAt(index)), cursor);
      
      // Continue with next character
      setTimeout(() => {
        this.typeText(element, text, cursor, index + 1, speed);
      }, speed);
    }
  }
};

/**
 * Hover Effects - handles advanced hover animations
 */
const HoverEffects = {
  initialize() {
    // Apply magnetic hover effect to buttons
    this.setupMagneticEffect();
    
    // Apply hover highlight effect to cards
    this.setupHighlightEffect();
    
    // Apply 3D tilt effect
    this.setupTiltEffect();
  },
  
  setupMagneticEffect() {
    document.querySelectorAll('[data-magnetic]').forEach(element => {
      element.addEventListener('mousemove', (e) => {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        const strength = parseFloat(element.getAttribute('data-magnetic')) || 0.2;
        
        element.style.transform = `translate(${x * strength}px, ${y * strength}px)`;
      });
      
      element.addEventListener('mouseleave', () => {
        element.style.transform = 'translate(0px, 0px)';
      });
    });
  },
  
  setupHighlightEffect() {
    document.querySelectorAll('[data-highlight]').forEach(element => {
      element.addEventListener('mouseenter', () => {
        element.classList.add('highlight-pulse');
      });
      
      element.addEventListener('animationend', () => {
        element.classList.remove('highlight-pulse');
      });
    });
  },
  
  setupTiltEffect() {
    document.querySelectorAll('[data-tilt]').forEach(element => {
      element.addEventListener('mousemove', (e) => {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const percentX = (x - centerX) / centerX;
        const percentY = (y - centerY) / centerY;
        
        const tiltAmount = parseFloat(element.getAttribute('data-tilt')) || 10;
        const tiltX = tiltAmount * percentY * -1;
        const tiltY = tiltAmount * percentX;
        
        element.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
      });
      
      element.addEventListener('mouseleave', () => {
        element.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
      });
    });
  }
};

/**
 * Ripple Effects - adds material design-like ripple on click
 */
const RippleEffects = {
  initialize() {
    document.querySelectorAll('[data-ripple]').forEach(element => {
      element.addEventListener('mousedown', (e) => {
        this.createRipple(element, e);
      });
    });
  },
  
  createRipple(element, e) {
    // Remove old ripples
    const ripples = element.querySelectorAll('.ripple');
    ripples.forEach(ripple => {
      if (ripple.offsetWidth > 0) {
        ripple.remove();
      }
    });
    
    // Create ripple element
    const ripple = document.createElement('span');
    ripple.className = 'ripple';
    element.appendChild(ripple);
    
    // Set position and size
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
    
    // Add active class
    ripple.classList.add('active');
    
    // Remove the ripple after animation
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }
};

/**
 * Highlight Manager - highlights elements of interest
 */
const HighlightManager = {
  highlightElement(selector, duration = 3000) {
    const element = document.querySelector(selector);
    
    if (!element) return;
    
    // Create highlight circle
    const circle = document.createElement('div');
    circle.classList.add('highlight-circle');
    
    // Position circle over the element
    const rect = element.getBoundingClientRect();
    circle.style.left = `${rect.left + rect.width / 2 - 24}px`;
    circle.style.top = `${rect.top + rect.height / 2 - 24}px`;
    
    // Add to DOM
    document.body.appendChild(circle);
    
    // Remove after duration
    setTimeout(() => {
      circle.remove();
    }, duration);
    
    return circle;
  }
};

/**
 * Utility for creating smooth transitions between steps
 */
const TransitionEffects = {
  fadeOut(element, callback, duration = 300) {
    element.style.transition = `opacity ${duration}ms ease`;
    element.style.opacity = '0';
    
    setTimeout(() => {
      if (callback) callback();
    }, duration);
  },
  
  fadeIn(element, duration = 300) {
    element.style.transition = `opacity ${duration}ms ease`;
    element.style.opacity = '0';
    
    // Force reflow
    void element.offsetWidth;
    
    element.style.opacity = '1';
  },
  
  slideOut(element, direction = 'left', callback, duration = 300) {
    element.style.transition = `transform ${duration}ms ease`;
    
    let transform;
    switch (direction) {
      case 'left':
        transform = 'translateX(-100%)';
        break;
      case 'right':
        transform = 'translateX(100%)';
        break;
      case 'up':
        transform = 'translateY(-100%)';
        break;
      case 'down':
        transform = 'translateY(100%)';
        break;
      default:
        transform = 'translateX(-100%)';
    }
    
    element.style.transform = transform;
    
    setTimeout(() => {
      if (callback) callback();
    }, duration);
  },
  
  slideIn(element, fromDirection = 'right', duration = 300) {
    let initialTransform;
    switch (fromDirection) {
      case 'left':
        initialTransform = 'translateX(-100%)';
        break;
      case 'right':
        initialTransform = 'translateX(100%)';
        break;
      case 'up':
        initialTransform = 'translateY(-100%)';
        break;
      case 'down':
        initialTransform = 'translateY(100%)';
        break;
      default:
        initialTransform = 'translateX(100%)';
    }
    
    element.style.transition = 'none';
    element.style.transform = initialTransform;
    
    // Force reflow
    void element.offsetWidth;
    
    element.style.transition = `transform ${duration}ms ease`;
    element.style.transform = 'translate(0, 0)';
  }
};
