
function createFloatingParticles() {
  const particlesContainer = document.getElementById('particles-container');
  if (!particlesContainer) {
    console.warn('Particles container not found');
    return;
  }

  particlesContainer.innerHTML = '';

  for (let i = 0; i < 60; i++) {
    const particle = document.createElement('div');
    particle.className = 'floating-particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 5 + 's';
    particle.style.animationDuration = (Math.random() * 4 + 3) + 's';
    particle.style.width = (Math.random() * 6 + 6) + 'px';
    particle.style.height = particle.style.width;
    particlesContainer.appendChild(particle);
  }
  console.log('Created', particlesContainer.children.length, 'floating particles');
}

function animateGradient() {
}

function createCursorTrail() {
  const trail = [];
  const trailLength = 20;
  
  for (let i = 0; i < trailLength; i++) {
    const dot = document.createElement('div');
    dot.className = 'cursor-trail';
    dot.style.opacity = (trailLength - i) / trailLength * 0.5;
    dot.style.transform = `scale(${(trailLength - i) / trailLength})`;
    document.body.appendChild(dot);
    trail.push({ element: dot, x: 0, y: 0 });
  }
  
  let mouseX = 0, mouseY = 0;
  let trailX = 0, trailY = 0;
  
  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });
  
  function animateTrail() {
    trailX += (mouseX - trailX) * 0.1;
    trailY += (mouseY - trailY) * 0.1;
    
    trail.forEach((dot, index) => {
      const nextDot = trail[index + 1] || { x: trailX, y: trailY };
      dot.x += (nextDot.x - dot.x) * 0.3;
      dot.y += (nextDot.y - dot.y) * 0.3;
      
      dot.element.style.left = dot.x + 'px';
      dot.element.style.top = dot.y + 'px';
    });
    
    requestAnimationFrame(animateTrail);
  }
  
  animateTrail();
}

function typeWriter(element, text, speed = 30) {
  let i = 0;
  element.textContent = '';
  
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  
  type();
}

function animateRecordingButton(button) {
  if (!button) return;
  
  let scale = 1;
  let growing = true;
  
  const pulse = setInterval(() => {
    if (button.classList.contains('recording')) {
      scale += growing ? 0.02 : -0.02;
      if (scale >= 1.15) growing = false;
      if (scale <= 1.0) growing = true;
      button.style.transform = `scale(${scale})`;
    } else {
      clearInterval(pulse);
      button.style.transform = 'scale(1)';
    }
  }, 50);
}

function animateWelcomeScreen() {
  const welcomeIcon = document.getElementById('welcome-icon-3d');
  if (!welcomeIcon) return;
  
  let rotation = 0;
  let floatY = 0;
  let floatDirection = 1;
  
  setInterval(() => {
    rotation += 2;
    floatY += floatDirection * 0.5;
    
    if (floatY > 15) floatDirection = -1;
    if (floatY < -15) floatDirection = 1;
    
    welcomeIcon.style.transform = `
      translateY(${floatY}px) 
      rotateY(${rotation}deg) 
      rotateX(${Math.sin(rotation * 0.1) * 10}deg)
      scale(${1 + Math.sin(rotation * 0.05) * 0.1})
    `;
  }, 50);
}

function createRippleEffect(element) {
  element.addEventListener('click', function(e) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  });
}

function addGlowEffect(selector) {
  const elements = document.querySelectorAll(selector);
  elements.forEach(el => {
    el.addEventListener('mouseenter', function() {
      this.style.boxShadow = '0 0 30px rgba(102, 126, 234, 0.8), 0 0 60px rgba(102, 126, 234, 0.4)';
      this.style.transform = 'translateY(-5px) scale(1.05)';
    });
    
    el.addEventListener('mouseleave', function() {
      this.style.boxShadow = '';
      this.style.transform = '';
    });
  });
}

function initAllAnimations() {
  console.log('🎨 Initializing animations...');
  
  setTimeout(() => {
    createFloatingParticles();
    animateGradient();
    createCursorTrail();
    animateWelcomeScreen();
    
    const buttons = document.querySelectorAll('button, .tag, .message-content');
    buttons.forEach(createRippleEffect);
    console.log('Added ripple effects to', buttons.length, 'elements');
    
    addGlowEffect('.mic-button');
    addGlowEffect('.send-button');
    addGlowEffect('.tag');
    
    const micButton = document.getElementById('mic-button');
    if (micButton) {
      const observer = new MutationObserver(() => {
        animateRecordingButton(micButton);
      });
      observer.observe(micButton, { attributes: true, attributeFilter: ['class'] });
    }
    
    console.log('✨ All animations initialized successfully!');
  }, 100);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllAnimations);
} else {
  initAllAnimations();
}

window.animations = {
  typeWriter,
  createRippleEffect,
  animateRecordingButton
};

