/* Main animations and interactive constellation using Anime.js */
(function(){
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Small entrance for static sections (CV fallback)
  if(!prefersReduced){
    const seqTargets = document.querySelectorAll('.cv-header .name, .cv-header .title, .cv-header .summary');
    anime.timeline({easing: 'easeOutExpo', duration: 650})
      .add({targets: seqTargets, translateY: [30,0], opacity: [0,1], delay: anime.stagger(80)});
  }

  // ------------------- Universe / bubbles -------------------
  const scene = document.getElementById('bubble-scene');
  const detailPanel = document.getElementById('detail-panel');
  const detailContent = document.getElementById('detail-content');
  const closeDetail = document.getElementById('close-detail');

  let bubbles = Array.isArray(window.BUBBLES) ? window.BUBBLES : [];
  let elements = {};

  function createBubbleNode(data){
    const el = document.createElement('div');
    el.className = 'bubble small';
    el.dataset.id = data.id || data.label;
    el.style.background = data.color || '#7c3aed';
    el.style.color = '#fff';
    if(data.type === 'center'){
      el.classList.add('center');
      const photo = data.photo || '/static/portafoliosapp/img/profile.jpg';
      el.innerHTML = `
        <img class="photo" src="${photo}" alt="${data.name || data.label}">
        <div class="center-content">
          <div class="name">${data.name || data.label}</div>
          <div class="title">${data.title || ''}</div>
        </div>`;
    } else {
      el.innerHTML = `<div class="icon">${data.icon || ''}</div><div class="label">${data.label}</div>`;
    }
    el.setAttribute('role','button');
    el.setAttribute('tabindex','0');
    return el;
  }

  function placeBubbles(){
    const rect = scene.getBoundingClientRect();
    const cx = rect.width/2;
    const cy = rect.height/2;
    const radius = Math.min(cx,cy) - 140;
    const primary = bubbles.find(b=>b.type==='center') || bubbles[0];

    // create center bubble
    const centerEl = createBubbleNode(primary);
    scene.appendChild(centerEl);
    // position center using its real size
    const cw = centerEl.offsetWidth || 260;
    const ch = centerEl.offsetHeight || 260;
    centerEl.style.left = (cx - cw/2) + 'px';
    centerEl.style.top = (cy - ch/2) + 'px';
    elements[primary.id] = centerEl;

    // create orbiting bubbles
    const others = bubbles.filter(b=>b.id !== primary.id);
    others.forEach((b,i)=>{
      const angle = (i / others.length) * Math.PI*2 + (Math.random()*0.6 - 0.3);
      const x = cx + Math.cos(angle) * (radius * (0.6 + Math.random()*0.35)) - 46;
      const y = cy + Math.sin(angle) * (radius * (0.6 + Math.random()*0.35)) - 46;
      const el = createBubbleNode(b);
      el.classList.add('small');
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      scene.appendChild(el);
      elements[b.id] = el;

      // subtle floating animation
      if(!prefersReduced){
        anime({
          targets: el,
          translateY: [0, (Math.random()*18)-9],
          translateX: [0, (Math.random()*18)-9],
          duration: 3000 + Math.random()*4000,
          direction: 'alternate',
          easing: 'easeInOutSine',
          loop: true
        });
      }

      // interactions
      el.addEventListener('click', ()=> focusBubble(b.id));
      el.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' || e.key === ' ') focusBubble(b.id); });
    });

    // center click to show profile details
    centerEl.addEventListener('click', ()=> focusBubble(primary.id));
    centerEl.addEventListener('keydown', (e)=>{ if(e.key === 'Enter' || e.key === ' ') focusBubble(primary.id); });

    // entry animation
    if(!prefersReduced){
      anime.timeline()
        .add({targets: Object.values(elements), scale: [0.2,1], opacity: [0,1], delay: anime.stagger(80)})
        .add({targets: Object.values(elements), translateZ: 0, duration: 1200});
    }
  }

  function focusBubble(id){
    const selected = bubbles.find(b=>b.id===id);
    if(!selected) return;

    // animate others away
    Object.keys(elements).forEach(key=>{
      const el = elements[key];
      if(key === id){
        anime({targets: el, scale: [1,1.25], duration: 600, easing: 'easeOutExpo'});
      } else {
        anime({targets: el, scale: [1,0.6], opacity: [1,0.12], duration: 600, easing: 'easeOutExpo'});
      }
    });

    // show detail panel
    if(selected.children){
      // show list of children as subitems in detail
      let html = `<h3>${selected.label}</h3><ul>`;
      selected.children.forEach(c=>{ html += `<li><strong>${c.label}</strong>: ${c.text}</li>`; });
      html += `</ul>`;
      detailContent.innerHTML = html;
    } else if(selected.content){
      detailContent.innerHTML = `<h3>${selected.label}</h3><p>${selected.content}</p>`;
    } else {
      detailContent.innerHTML = `<h3>${selected.label}</h3><p>Más información próximamente.</p>`;
    }

    detailPanel.style.display = 'block';
    detailPanel.setAttribute('aria-hidden','false');
  }

  function resetView(){
    Object.keys(elements).forEach(k=>{
      const el = elements[k];
      anime({targets: el, scale: 1, opacity: 1, duration: 420, easing: 'easeOutExpo'});
    });
    detailPanel.style.display = 'none';
    detailPanel.setAttribute('aria-hidden','true');
  }

  closeDetail.addEventListener('click', resetView);

  // initialize once DOM is ready
  function init(){
    if(!scene) return;
    // create stars canvas simple background
    const canvas = document.getElementById('stars');
    if(canvas){
      canvas.width = canvas.clientWidth;
      canvas.height = canvas.clientHeight;
      const ctx = canvas.getContext('2d');
      for(let i=0;i<80;i++){
        ctx.fillStyle = 'rgba(255,255,255,'+(Math.random()*0.12)+')';
        const x = Math.random()*canvas.width;
        const y = Math.random()*canvas.height;
        const r = Math.random()*1.8;
        ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
      }
    }

    placeBubbles();
  }

  window.addEventListener('load', init);
  window.addEventListener('resize', ()=>{ /* simple reload to reposition */ location.reload(); });

})();
