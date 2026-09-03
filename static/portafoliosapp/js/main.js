(function(){
  // Animación principal con anime.js
  const timeline = anime.timeline({
    easing: 'easeOutExpo',
    duration: 700,
  });

  timeline.add({
    targets: '.name',
    translateY: [40, 0],
    opacity: [0, 1],
    duration: 900,
  })
  .add({
    targets: '.role',
    translateY: [20, 0],
    opacity: [0, 1],
    offset: '-=350'
  })
  .add({
    targets: '.intro',
    translateY: [12, 0],
    opacity: [0, 1],
    offset: '-=450'
  })
  .add({
    targets: '.contact',
    opacity: [0,1],
    translateY: [6,0],
    offset: '-=420'
  })
  .add({
    targets: '.skill-item',
    scale: [0.8, 1],
    opacity: [0,1],
    delay: anime.stagger(80),
    offset: '-=300'
  });

  // Pequeña animación de fondo opcional
  anime({
    targets: '.hero',
    boxShadow: [
      '0 6px 24px rgba(2,6,23,0.2)',
      '0 18px 48px rgba(124,58,237,0.06)'
    ],
    direction: 'alternate',
    easing: 'easeInOutSine',
    duration: 3000,
    loop: true
  });
})();
