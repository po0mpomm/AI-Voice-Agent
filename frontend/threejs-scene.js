(function() {
  'use strict';
  
  function initThreeJS() {
    if (typeof THREE === 'undefined') {
      console.log('⏳ Waiting for Three.js to load...');
      setTimeout(initThreeJS, 100);
      return;
    }
    console.log('🎨 Three.js loaded, initializing 3D scene...');
    
    const THREE = window.THREE;
    let scene, camera, renderer, particles, particleSystem;
    let mouseX = 0, mouseY = 0;
    let windowHalfX = window.innerWidth / 2;
    let windowHalfY = window.innerHeight / 2;

    const canvas = document.getElementById('threejs-canvas');
    if (!canvas) {
      setTimeout(initThreeJS, 100);
      return;
    }

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ 
      canvas: canvas, 
      alpha: true, 
      antialias: true 
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);

    camera.position.z = 5;

    const shapes = [];
    const geometryTypes = [
      new THREE.IcosahedronGeometry(0.3, 0),
      new THREE.OctahedronGeometry(0.3, 0),
      new THREE.TetrahedronGeometry(0.3, 0),
      new THREE.TorusGeometry(0.2, 0.1, 8, 16),
    ];

    for (let i = 0; i < 15; i++) {
      const geometry = geometryTypes[Math.floor(Math.random() * geometryTypes.length)];
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color().setHSL(0.6 + Math.random() * 0.15, 0.5, 0.6),
        transparent: true,
        opacity: 0.5,
        emissive: new THREE.Color().setHSL(0.6 + Math.random() * 0.15, 0.4, 0.2),
        shininess: 80,
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      );
      mesh.rotation.set(
        Math.random() * Math.PI,
        Math.random() * Math.PI,
        Math.random() * Math.PI
      );
      mesh.userData = {
        speed: Math.random() * 0.02 + 0.01,
        rotationSpeed: {
          x: (Math.random() - 0.5) * 0.02,
          y: (Math.random() - 0.5) * 0.02,
          z: (Math.random() - 0.5) * 0.02,
        },
      };
      scene.add(mesh);
      shapes.push(mesh);
    }

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const light1 = new THREE.DirectionalLight(0x6366f1, 0.5);
    light1.position.set(5, 5, 5);
    scene.add(light1);

    const light2 = new THREE.DirectionalLight(0x8b5cf6, 0.4);
    light2.position.set(-5, -5, -5);
    scene.add(light2);
    
    const light3 = new THREE.DirectionalLight(0x3b82f6, 0.3);
    light3.position.set(0, 5, -5);
    scene.add(light3);

    const particleCount = 2000;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 20;
      positions[i + 1] = (Math.random() - 0.5) * 20;
      positions[i + 2] = (Math.random() - 0.5) * 20;

      const color = new THREE.Color().setHSL(Math.random(), 0.7, 0.6);
      colors[i] = color.r;
      colors[i + 1] = color.g;
      colors[i + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.08,
      vertexColors: true,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
    });

    particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);

    const rings = [];
    const ringGeometry = new THREE.RingGeometry(2, 2.5, 64);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: 0x6366f1,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.3,
    });

    for (let i = 0; i < 3; i++) {
      const ring = new THREE.Mesh(ringGeometry, ringMaterial.clone());
      ring.rotation.x = Math.PI / 2;
      ring.position.z = -3 - i * 2;
      ring.userData = {
        rotationSpeed: 0.005 + i * 0.002,
        initialZ: ring.position.z,
      };
      scene.add(ring);
      rings.push(ring);
    }

    function onMouseMove(event) {
      mouseX = (event.clientX - windowHalfX) * 0.01;
      mouseY = (event.clientY - windowHalfY) * 0.01;
    }

    function onWindowResize() {
      windowHalfX = window.innerWidth / 2;
      windowHalfY = window.innerHeight / 2;

      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }

    document.addEventListener('mousemove', onMouseMove, false);
    window.addEventListener('resize', onWindowResize, false);

    function animate() {
      requestAnimationFrame(animate);

      shapes.forEach((shape, index) => {
        shape.rotation.x += shape.userData.rotationSpeed.x * 2;
        shape.rotation.y += shape.userData.rotationSpeed.y * 2;
        shape.rotation.z += shape.userData.rotationSpeed.z * 2;
        
        shape.position.y += Math.sin(Date.now() * shape.userData.speed + index) * 0.02;
        shape.position.x += Math.cos(Date.now() * shape.userData.speed + index) * 0.02;
        shape.position.z += Math.sin(Date.now() * shape.userData.speed * 0.5 + index) * 0.01;
      });

      if (particleSystem) {
        particleSystem.rotation.y += 0.003;
        particleSystem.rotation.x += 0.001;
        const positions = particleSystem.geometry.attributes.position.array;
        for (let i = 1; i < positions.length; i += 3) {
          positions[i] += Math.sin(Date.now() * 0.002 + i) * 0.003;
          positions[i + 2] += Math.cos(Date.now() * 0.001 + i) * 0.002;
        }
        particleSystem.geometry.attributes.position.needsUpdate = true;
      }

      rings.forEach((ring, index) => {
        ring.rotation.z += ring.userData.rotationSpeed;
        ring.position.z = ring.userData.initialZ + Math.sin(Date.now() * 0.0005 + index) * 0.5;
      });

      camera.position.x += (mouseX * 2 - camera.position.x) * 0.1;
      camera.position.y += (-mouseY * 2 - camera.position.y) * 0.1;
      camera.lookAt(scene.position);
      
      camera.rotation.z = Math.sin(Date.now() * 0.0005) * 0.05;

      renderer.render(scene, camera);
    }

    animate();
    console.log('✅ Three.js scene initialized and animating!');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThreeJS);
  } else {
    setTimeout(initThreeJS, 100);
  }
})();
