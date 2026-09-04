(function () {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scene = document.getElementById("bubble-scene");
  const panel = document.getElementById("detail-panel");
  const content = document.getElementById("detail-content");
  const toggleButton = document.getElementById("toggle-detail");
  const closeButton = document.getElementById("close-detail");
  const canvas = document.getElementById("stars");
  const dataLines = document.getElementById("data-lines");
  const scanline = document.querySelector(".scanline");
  const statusPanels = document.querySelectorAll(".status-panel");
  let simulationModal = null;
  let imageModal = null;
  const imageZoomState = {
    scale: 1,
    x: 0,
    y: 0,
    dragging: false,
    startX: 0,
    startY: 0,
    originX: 0,
    originY: 0,
    touchDistance: 0,
  };
  const deviceMemory = navigator.deviceMemory || 8;
  const performanceLite = prefersReduced || window.innerWidth < 900 || (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4) || deviceMemory <= 4;
  const bubbles = Array.isArray(window.BUBBLES) ? window.BUBBLES : [];
  const animeDriver = window.anime || Object.assign(
    (options) => {
      if (typeof options.complete === "function") options.complete();
    },
    {
      remove: () => {},
      stagger: () => 0,
      timeline: () => ({ add: () => ({ add: () => {} }) }),
    }
  );

  if (!scene || !bubbles.length) return;

  document.documentElement.classList.toggle("perf-lite", performanceLite);

  let currentLevel = "home";
  let activeId = "profile";
  let resizeTimer = null;

  const centerData = bubbles.find((bubble) => bubble.type === "center") || bubbles[0];
  const mainBubbles = bubbles.filter((bubble) => bubble.id !== centerData.id);

  function escapeHTML(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function readViewport() {
    const viewport = window.visualViewport;
    return {
      width: Math.round(viewport?.width || window.innerWidth),
      height: Math.round(viewport?.height || window.innerHeight),
    };
  }

  function fitNodeScale(childCount = 0, viewport = readViewport()) {
    const width = viewport.width;
    const height = viewport.height;
    const compact = width < 900;
    const phone = width < 600;
    const landscape = width > height;
    const denseChildren = childCount > 6;
    const root = document.documentElement;
    const limit = (value, min, max) => Math.max(min, Math.min(max, value));
    const topReserve = compact ? (landscape ? 86 : 142) : 164;
    const usableHeight = Math.max(280, height - topReserve);
    const usableWidth = Math.max(280, width - (compact ? 20 : 44));
    const landscapePhone = phone && landscape;

    const coreSize = compact
      ? limit(Math.min(width * (landscapePhone ? 0.22 : 0.31), usableHeight * 0.23), landscapePhone ? 90 : 108, landscapePhone ? 132 : 148)
      : limit(Math.min(usableWidth * 0.17, usableHeight * 0.31), 188, 246);
    const nodeSize = compact
      ? limit(Math.min(width * (landscapePhone ? 0.13 : 0.2), usableHeight * 0.14), landscapePhone ? 58 : 70, landscapePhone ? 88 : 98)
      : limit(Math.min(usableWidth * 0.13, usableHeight * 0.19), 118, 172);
    const childSize = denseChildren
      ? (compact
        ? limit(Math.min(width * (landscapePhone ? 0.12 : 0.2), usableHeight * 0.13), landscapePhone ? 56 : 66, landscapePhone ? 84 : 96)
        : limit(Math.min(width * 0.12, usableHeight * 0.21), 118, 176))
      : (compact
        ? limit(Math.min(width * (landscapePhone ? 0.13 : 0.23), usableHeight * 0.16), landscapePhone ? 58 : 74, landscapePhone ? 92 : 112)
        : limit(Math.min(usableWidth * 0.2, usableHeight * 0.34), 152, 238));
    const moduleChildSize = childCount > 12
      ? (compact
        ? limit(Math.min(width * (landscapePhone ? 0.13 : 0.17), usableHeight * 0.09), 50, landscapePhone ? 70 : 78)
        : limit(Math.min(usableWidth * 0.11, usableHeight * 0.14), 78, 118))
      : (compact
        ? limit(childSize * 0.82, landscapePhone ? 48 : 58, landscapePhone ? 76 : 90)
        : limit(childSize * 0.78, 118, 176));

    root.style.setProperty("--core-size", `${coreSize}px`);
    root.style.setProperty("--node-size", `${nodeSize}px`);
    root.style.setProperty("--child-size", `${childSize}px`);
    root.style.setProperty("--module-child-size", `${moduleChildSize}px`);
  }

  function adaptViewport({ render = true } = {}) {
    const { width, height } = readViewport();
    const root = document.documentElement;
    const compact = width < 900;
    const phone = width < 600;
    const portrait = height >= width;

    root.style.setProperty("--viewport-width", `${width}px`);
    root.style.setProperty("--viewport-height", `${height}px`);
    root.classList.toggle("viewport-compact", compact);
    root.classList.toggle("viewport-phone", phone);
    root.classList.toggle("viewport-portrait", portrait);

    fitNodeScale(currentLevel === "children" ? (bubbles.find((bubble) => bubble.id === activeId)?.children || []).length : 0, { width, height });
    drawTechField();

    if (render) relayoutCurrentScene();
  }

  // Force a consistent viewport/layout recalculation to avoid transient
  // reflow issues when the detail panel is shown/hidden or moved to the side.
  function stabilizeLayout() {
    adaptViewport({ render: false });
    // eslint-disable-next-line no-unused-expressions
    document.body.offsetHeight;
    relayoutCurrentScene();
    window.setTimeout(() => {
      adaptViewport({ render: false });
      relayoutCurrentScene();
    }, 180);
  }

  function adjustCenterForPanel() {
    try {
      const viewport = readViewport();
      const phone = viewport.width < 600;
      const landscape = viewport.width > viewport.height;
      if (!phone || !landscape || !document.body.classList.contains("children-panel")) return;

      const sceneRect = scene.getBoundingClientRect();
      const maxShift = Math.min(36, Math.max(18, sceneRect.width * 0.04));
      const safeX = Math.max(60, Math.min(sceneRect.width - 60, sceneRect.width / 2 - maxShift));
      const safeY = Math.max(120, Math.min(sceneRect.height - 80, sceneRect.height / 2 + 8));

      if (currentLevel === "children") {
        const parentBubble = scene.querySelector(".module-parent");
        if (parentBubble) setPosition(parentBubble, safeX, safeY);
        return;
      }

      const centerEl = scene.querySelector(".bubble.center");
      if (centerEl) setPosition(centerEl, safeX, safeY);
    } catch (e) {
      // ignore errors intentionally
    }
  }

  function logLayoutEvent(name, extra = {}) {
    try {
      const viewport = readViewport();
      const entry = {
        time: Date.now(),
        name,
        level: currentLevel,
        viewport,
        orientation: viewport.width > viewport.height ? "landscape" : "portrait",
        bodyClasses: document.body.className,
        extra,
      };
      const key = "layoutMetrics";
      const raw = localStorage.getItem(key);
      const arr = raw ? JSON.parse(raw) : [];
      arr.push(entry);
      if (arr.length > 120) arr.splice(0, arr.length - 120);
      localStorage.setItem(key, JSON.stringify(arr));
      // eslint-disable-next-line no-console
      console.info("layoutMetric", entry);
    } catch (e) {
      // ignore storage errors
    }
  }

  function scheduleViewportAdapt() {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => adaptViewport(), 180);
  }

  function relayoutCurrentScene() {
    fitNodeScale(currentLevel === "children" ? (bubbles.find((bubble) => bubble.id === activeId)?.children || []).length : 0);
    drawTechField();
    clearConnectors();

    if (currentLevel === "children") {
      const active = bubbles.find((bubble) => bubble.id === activeId);
      if (!active) return;

      const parentBubble = scene.querySelector(".module-parent");
      const childElements = Array.from(scene.querySelectorAll(".module-child"));
      const rect = scene.getBoundingClientRect();
      const viewport = readViewport();
      const phonePanel = viewport.width < 600 && document.body.classList.contains("panel-open") && !document.body.classList.contains("panel-collapsed");
      const parentY = phonePanel
        ? Math.max(270, Math.min(rect.height - 68, rect.height * 0.68))
        : rect.height / 2 + 8;
      if (parentBubble) setPosition(parentBubble, rect.width / 2, parentY);
      graphLayout(active.children || [], "children").forEach(({ x, y }, index) => {
        if (childElements[index]) setPosition(childElements[index], x, y);
      });
      requestAnimationFrame(() => drawConnectors(parentBubble, childElements));
      return;
    }

    const center = scene.querySelector(".bubble.center");
    const primaryNodes = Array.from(scene.querySelectorAll(".bubble.primary:not(.module-parent)"));
    const rect = scene.getBoundingClientRect();
    if (center) setPosition(center, rect.width / 2, rect.height / 2 + 8);
    graphLayout(mainBubbles, "home").forEach(({ x, y }, index) => {
      if (primaryNodes[index]) setPosition(primaryNodes[index], x, y);
    });
    requestAnimationFrame(() => drawConnectors(center, primaryNodes));
  }

  function measureBubble(mode) {
    const probe = document.createElement("button");
    probe.type = "button";
    probe.className = `bubble ${mode}`;
    probe.style.visibility = "hidden";
    scene.appendChild(probe);
    const size = probe.getBoundingClientRect().width;
    probe.remove();
    return size || 120;
  }

  function drawTechField() {
    if (!canvas) return;

    const ratio = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    canvas.width = width * ratio;
    canvas.height = height * ratio;

    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);

    const maxPoints = performanceLite ? 24 : 44;
    const pointCount = Math.min(maxPoints, Math.max(performanceLite ? 14 : 22, Math.round((width * height) / (performanceLite ? 68000 : 46000))));
    const points = Array.from({ length: pointCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 1.8 + 0.6,
      a: Math.random() * 0.38 + 0.14,
    }));

    ctx.lineWidth = 1;
    points.forEach((point, index) => {
      for (let next = index + 1; next < points.length; next += 1) {
        const target = points[next];
        const distance = Math.hypot(point.x - target.x, point.y - target.y);
        if (distance < (performanceLite ? 125 : 155)) {
          ctx.strokeStyle = `rgba(53, 242, 167, ${performanceLite ? 0.06 - distance / 2600 : 0.1 - distance / 1900})`;
          ctx.beginPath();
          ctx.moveTo(point.x, point.y);
          ctx.lineTo(target.x, target.y);
          ctx.stroke();
        }
      }
    });

    points.forEach((point, index) => {
      ctx.fillStyle = index % 4 === 0 ? `rgba(255, 78, 205, ${point.a})` : `rgba(53, 242, 167, ${point.a})`;
      ctx.beginPath();
      ctx.arc(point.x, point.y, point.r, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.strokeStyle = "rgba(24, 216, 255, 0.08)";
    for (let y = 0; y < height; y += performanceLite ? 140 : 110) {
      ctx.beginPath();
      ctx.moveTo(0, y + 0.5);
      ctx.lineTo(width, y + 0.5);
      ctx.stroke();
    }
  }

  function bootMotion() {
    if (prefersReduced) return;

    if (!performanceLite) {
      animeDriver({
        targets: scanline,
        translateY: ["-100%", "285%"],
        duration: 7200,
        easing: "easeInOutSine",
        loop: true,
      });
    }

    animeDriver({
      targets: statusPanels,
      opacity: [0, 1],
      translateY: [16, 0],
      delay: animeDriver.stagger(130),
      duration: 700,
      easing: "easeOutExpo",
    });
  }

  function makeFrame() {
    if (scene.querySelector(".tech-frame")) return;

    const frame = document.createElement("div");
    frame.className = "tech-frame";
    scene.appendChild(frame);

    if (!prefersReduced && !performanceLite) {
      animeDriver({
        targets: frame,
        rotate: ["0deg", "360deg"],
        duration: 42000,
        easing: "linear",
        loop: true,
      });
    }
  }

  function makeModuleFrame() {
    const frame = document.createElement("div");
    frame.className = "module-frame";
    scene.appendChild(frame);

    if (!prefersReduced && !performanceLite) {
      animeDriver({
        targets: frame,
        opacity: [0, 1],
        scale: [0.78, 1],
        rotate: [-2, 0],
        duration: 1100,
        easing: "easeOutExpo",
      });
    }

    return frame;
  }

  function graphLayout(items, mode) {
    const rect = scene.getBoundingClientRect();
    const viewport = readViewport();
    const compact = viewport.width < 900;
    const phone = viewport.width < 600;
    const panelOpen = document.body.classList.contains("panel-open") && !document.body.classList.contains("panel-collapsed");
    const nodeSize = measureBubble(mode === "children" ? "child module-child" : "primary");
    const margin = nodeSize / 2 + (compact ? 8 : 22);
    const desktopHome = [
      [0.3, 0.3], [0.5, 0.14], [0.7, 0.3],
      [0.27, 0.56], [0.73, 0.56], [0.38, 0.77], [0.62, 0.77],
    ];
    const mobileHome = panelOpen && phone
      ? [
        [0.28, 0.22], [0.72, 0.22], [0.23, 0.4],
        [0.77, 0.4], [0.31, 0.58], [0.69, 0.58], [0.5, 0.72],
      ]
      : [
        [0.27, 0.26], [0.73, 0.26], [0.23, 0.48],
        [0.77, 0.48], [0.31, 0.69], [0.69, 0.69], [0.5, 0.84],
      ];
    const desktopChildren = [
      [0.34, 0.28], [0.66, 0.28], [0.31, 0.5],
      [0.69, 0.5], [0.4, 0.72], [0.6, 0.72],
    ];
    const mobileChildren = panelOpen && phone
      ? [
        [0.5, 0.12], [0.25, 0.34], [0.75, 0.34],
        [0.32, 0.58], [0.68, 0.58], [0.5, 0.78],
      ]
      : [
        [0.31, 0.25], [0.69, 0.25], [0.28, 0.44],
        [0.72, 0.44], [0.35, 0.62], [0.65, 0.62],
      ];
    const orbitPoints = (count) => Array.from({ length: count }, (_, index) => {
      const angle = -Math.PI / 2 + (Math.PI * 2 * index) / count;
      const radiusX = compact ? (phone && panelOpen ? 0.24 : 0.28) : 0.32;
      const radiusY = compact ? (phone && panelOpen ? 0.22 : 0.28) : 0.34;
      const centerY = phone && panelOpen ? 0.34 : 0.48;
      return [0.5 + Math.cos(angle) * radiusX, centerY + Math.sin(angle) * radiusY];
    });
    const points = mode === "children"
      ? (items.length > 6 ? orbitPoints(items.length) : (compact ? mobileChildren : desktopChildren))
      : (compact ? mobileHome : desktopHome);

    const nodes = items.map((item, index) => {
      const point = points[index % points.length];
      const topSafe = compact
        ? (phone ? (panelOpen ? (mode === "children" ? 150 : 152) : 176) : 132)
        : margin;
      const bottomSafe = compact
        ? (phone && panelOpen ? (mode === "children" ? 34 : 16) : 34)
        : margin;
      const layoutHeight = Math.max(160, rect.height - topSafe - bottomSafe);
      const x = Math.max(margin, Math.min(rect.width - margin, rect.width * point[0]));
      const y = Math.max(topSafe, Math.min(rect.height - bottomSafe, topSafe + layoutHeight * point[1]));
      return { item, x, y, topSafe, bottomSafe };
    });

    return solidifyLayout(nodes, {
      rect,
      nodeSize,
      margin,
      mode,
      compact,
      phone,
      panelOpen,
    });
  }

  function solidifyLayout(nodes, options) {
    if (!nodes.length) return nodes;

    const { rect, nodeSize, margin, mode, compact, phone, panelOpen } = options;
    const topSafe = nodes[0].topSafe || margin;
    const bottomSafe = nodes[0].bottomSafe || margin;
    const minDistance = nodeSize * (phone ? 1.16 : compact ? 1.1 : 1.04);
    const bounds = {
      left: margin,
      right: Math.max(margin, rect.width - margin),
      top: topSafe,
      bottom: Math.max(topSafe, rect.height - bottomSafe),
    };
    const parentObstacle = mode === "children"
      ? {
        x: rect.width / 2,
        y: phone && panelOpen ? Math.max(270, Math.min(rect.height - 68, rect.height * 0.68)) : rect.height / 2 + 8,
        radius: nodeSize * (phone ? 0.92 : 0.82),
      }
      : null;

    const clampNode = (node) => {
      node.x = Math.max(bounds.left, Math.min(bounds.right, node.x));
      node.y = Math.max(bounds.top, Math.min(bounds.bottom, node.y));
    };

    for (let iteration = 0; iteration < 14; iteration += 1) {
      for (let current = 0; current < nodes.length; current += 1) {
        for (let next = current + 1; next < nodes.length; next += 1) {
          const a = nodes[current];
          const b = nodes[next];
          const dx = b.x - a.x || 0.01;
          const dy = b.y - a.y || 0.01;
          const distance = Math.hypot(dx, dy);
          if (distance >= minDistance) continue;

          const push = (minDistance - distance) / 2;
          const nx = dx / distance;
          const ny = dy / distance;
          a.x -= nx * push;
          a.y -= ny * push;
          b.x += nx * push;
          b.y += ny * push;
          clampNode(a);
          clampNode(b);
        }
      }

      if (parentObstacle) {
        nodes.forEach((node) => {
          const dx = node.x - parentObstacle.x || 0.01;
          const dy = node.y - parentObstacle.y || 0.01;
          const distance = Math.hypot(dx, dy);
          const required = parentObstacle.radius + nodeSize * 0.72;
          if (distance >= required) return;

          const push = required - distance;
          node.x += (dx / distance) * push;
          node.y += (dy / distance) * push;
          clampNode(node);
        });
      }
    }

    return nodes.map(({ item, x, y }) => ({ item, x, y }));
  }

  function clearConnectors() {
    if (!dataLines) return;
    const existing = Array.from(dataLines.querySelectorAll("*"));
    if (existing.length) animeDriver.remove(existing);
    dataLines.innerHTML = "";
  }

  function drawConnectors(centerElement, nodeElements) {
    if (!dataLines || !centerElement || !nodeElements.length) return;

    const rect = scene.getBoundingClientRect();
    const centerRect = centerElement.getBoundingClientRect();
    const start = {
      x: centerRect.left + centerRect.width / 2 - rect.left,
      y: centerRect.top + centerRect.height / 2 - rect.top,
    };

    dataLines.setAttribute("viewBox", `0 0 ${rect.width} ${rect.height}`);
    dataLines.innerHTML = nodeElements.map((node, index) => {
      const nodeRect = node.getBoundingClientRect();
      const end = {
        x: nodeRect.left + nodeRect.width / 2 - rect.left,
        y: nodeRect.top + nodeRect.height / 2 - rect.top,
      };
      const bend = Math.abs(end.x - start.x) > 160 ? (start.x + end.x) / 2 : start.x;
      const path = `M ${start.x} ${start.y} L ${bend} ${start.y} L ${bend} ${end.y} L ${end.x} ${end.y}`;
      if (performanceLite) {
        return `
          <path class="connector" d="${path}" pathLength="800" />
          <circle class="connector-node" cx="${end.x}" cy="${end.y}" r="2" />
        `;
      }
      return `
        <path class="connector-glow" d="${path}" />
        <path class="connector" d="${path}" pathLength="800" />
        <circle class="connector-node" cx="${end.x}" cy="${end.y}" r="2.2" />
        <circle class="connector-pulse" cx="${start.x}" cy="${start.y}" r="2" data-pulse="${index}" />
      `;
    }).join("");

    if (prefersReduced) return;

    const lines = dataLines.querySelectorAll(".connector");
    animeDriver({
      targets: lines,
      opacity: [0, 1],
      delay: animeDriver.stagger(70),
      duration: 420,
      easing: "easeOutQuart",
    });
    if (performanceLite) return;
    animeDriver({
      targets: lines,
      strokeDashoffset: [0, -800],
      delay: animeDriver.stagger(160, { start: 700 }),
      duration: 2200,
      loop: true,
      easing: "linear",
    });
    animeDriver({
      targets: dataLines.querySelectorAll(".connector-pulse"),
      r: [2, 5, 2],
      opacity: [0.25, 1, 0.25],
      delay: animeDriver.stagger(180),
      duration: 1700,
      loop: true,
      easing: "easeInOutSine",
    });
  }

  function iconHTML(data, alt = "") {
    if (data.image) {
      return `<img class="icon node-image" src="${escapeHTML(data.image)}" alt="${escapeHTML(alt)}" loading="lazy" decoding="async" />`;
    }
    return `<i class="icon bi ${escapeHTML(data.icon || "bi-circle")}" aria-hidden="true"></i>`;
  }

  function bubbleHTML(data, variant) {
    if (variant === "center") {
      const chips = (data.stats || [])
        .map((stat) => `<span class="stat-chip">${escapeHTML(stat)}</span>`)
        .join("");

      return `
        <div class="bubble-content">
          ${iconHTML(data, "")}
          <span class="center-name">${escapeHTML(data.name || data.label)}</span>
          ${data.tagline ? `<span class="center-tagline">${escapeHTML(data.tagline)}</span>` : ""}
          <span class="center-title">${escapeHTML(data.title || "")}</span>
          ${data.subtitle ? `<span class="center-subtitle">${escapeHTML(data.subtitle)}</span>` : ""}
          <span class="node-meta">${escapeHTML((data.stats || []).join(" · ") || "PERFIL TÉCNICO")}</span>
          <span class="stat-row">${chips}</span>
        </div>
      `;
    }

    return `
      <div class="bubble-content">
        ${iconHTML(data, "")}
        <span class="label">${escapeHTML(data.label)}</span>
        ${(data.level || data.badge) ? `<span class="level-tag">${escapeHTML(data.level || data.badge)}</span>` : ""}
        <span class="node-meta">${escapeHTML(data.kind === "skill" ? `TECH // ${data.icon || "NODE"}` : data.kind === "certificate" ? `CERT // ${data.icon || "NODE"}` : (data.id || data.kind || "node")).toUpperCase()}</span>
        ${data.text ? `<span class="micro">${escapeHTML(data.text)}</span>` : ""}
      </div>
    `;
  }

  function createBubble(data, variant) {
    const element = document.createElement("button");
    element.type = "button";
    element.className = `bubble ${variant}`;
    element.dataset.id = data.id || data.label;
    element.setAttribute("aria-label", data.label || data.name || "Nodo");
    element.style.setProperty("--bubble-color", data.color || centerData.color || "#35f2a7");
    element.innerHTML = bubbleHTML(data, variant);
    element.addEventListener("click", () => handleBubble(data, variant));
    return element;
  }

  function setPosition(element, x, y) {
    const width = element.offsetWidth || 120;
    const height = element.offsetHeight || 120;
    element.style.left = `${x - width / 2}px`;
    element.style.top = `${y - height / 2}px`;
  }

  function animateIn(targets) {
    if (prefersReduced) return;

    animeDriver.remove(targets);
    animeDriver({
      targets,
      scale: [0.45, 1],
      opacity: [0, 1],
      rotate: [-4, 0],
      delay: animeDriver.stagger(80),
      duration: 760,
      easing: "easeOutExpo",
    });

    animeDriver({
      targets: targets.map((target) => target.querySelector(".icon")),
      opacity: [0.35, 1],
      scale: [0.6, 1],
      delay: animeDriver.stagger(70, { start: 120 }),
      duration: 520,
      easing: "easeOutBack",
    });

    targets.forEach((target, index) => {
      if (!performanceLite) target.classList.add("is-floating");
      target.style.setProperty("--float-delay", `${index * 140}ms`);
    });
  }

  function clearScene(callback) {
    const oldBubbles = Array.from(scene.querySelectorAll(".bubble"));
    const oldModuleStacks = Array.from(scene.querySelectorAll(".module-stack"));
    clearConnectors();
    scene.querySelectorAll(".tech-frame, .module-frame").forEach((frame) => frame.remove());
    if (!oldBubbles.length) {
      oldModuleStacks.forEach((stack) => stack.remove());
      callback();
      return;
    }

    animeDriver.remove(oldBubbles);

    if (prefersReduced) {
      oldBubbles.forEach((element) => element.remove());
      oldModuleStacks.forEach((stack) => stack.remove());
      callback();
      return;
    }

    animeDriver({
      targets: oldBubbles,
      scale: 0.28,
      opacity: 0,
      delay: animeDriver.stagger(28),
      duration: 260,
      easing: "easeInQuad",
      complete: () => {
        oldBubbles.forEach((element) => element.remove());
        oldModuleStacks.forEach((stack) => stack.remove());
        callback();
      },
    });
  }

  function renderHome() {
    currentLevel = "home";
    activeId = centerData.id;
    fitNodeScale();
    hidePanel();

    // Ensure CSS that positions the detail panel for "children" is disabled
    document.body.classList.remove("children-panel");
    logLayoutEvent("level:home", { activeId });

    clearScene(() => {
      makeFrame();

      const rect = scene.getBoundingClientRect();
      const center = createBubble(centerData, "center");
      scene.appendChild(center);
      setPosition(center, rect.width / 2, rect.height / 2 + 8);

      const nodes = graphLayout(mainBubbles, "home");
      const created = [center];
      const children = [];

      nodes.forEach(({ item, x, y }) => {
        const element = createBubble(item, "primary");
        scene.appendChild(element);
        setPosition(element, x, y);
        created.push(element);
        children.push(element);
      });

      animateIn(created);
      requestAnimationFrame(() => drawConnectors(center, children));
    });
  }

  function renderChildren(parent) {
    const children = parent.children || [];
    currentLevel = "children";
    activeId = parent.id;
    document.body.classList.add("panel-open");
    // mark that children panel logic is active so CSS can render the panel to the right
    document.body.classList.add("children-panel");
    logLayoutEvent("level:children", { activeId: parent.id });
    // mark that children panel logic is active so CSS can render the panel to the right
    document.body.classList.add("children-panel");
    fitNodeScale(children.length);

    clearScene(() => {
      const moduleFrame = makeModuleFrame();

      const parentBubble = createBubble(parent, "primary");
      parentBubble.classList.add("module-parent");
      scene.appendChild(parentBubble);

      const created = [parentBubble];
      const childElements = [];
      const rect = scene.getBoundingClientRect();

      setPosition(parentBubble, rect.width / 2, rect.height / 2 + 8);

      children.forEach((item, index) => {
        const element = createBubble(
          {
            ...item,
            id: `${parent.id}-${index}`,
            color: item.color || parent.color,
            icon: item.icon || "bi-circle",
            kind: item.kind || "skill",
          },
          "child module-child"
        );
        scene.appendChild(element);
        created.push(element);
        childElements.push(element);
      });

      graphLayout(children, "children").forEach(({ x, y }, index) => {
        setPosition(childElements[index], x, y);
      });

      animateIn(created);
      if (!prefersReduced) {
        animeDriver({
          targets: moduleFrame,
          boxShadow: [
            "0 0 26px rgba(24, 216, 255, 0.04), inset 0 0 28px rgba(53, 242, 167, 0.02)",
            "0 0 90px rgba(24, 216, 255, 0.13), inset 0 0 70px rgba(53, 242, 167, 0.08)",
            "0 0 46px rgba(24, 216, 255, 0.07), inset 0 0 44px rgba(53, 242, 167, 0.04)",
          ],
          duration: 1800,
          easing: "easeInOutSine",
        });
      }
      showPanel(parent);
      requestAnimationFrame(() => drawConnectors(parentBubble, childElements));
    });
  }

  function handleBubble(data, variant) {
    if (
      currentLevel === "children" &&
      (variant === "center" || (variant === "primary" && data.id === activeId))
    ) {
      renderHome();
      return;
    }

    if (data.children && data.children.length) {
      renderChildren(data);
      return;
    }

    showPanel(data);
  }

  function renderSections(data) {
    if (!Array.isArray(data.sections) || !data.sections.length) return "";

    return data.sections.map((section) => `
      <section class="detail-section" aria-label="${escapeHTML(section.heading)}">
        <div class="detail-section-heading"><i class="bi ${escapeHTML(section.icon || "bi-list-check")}" aria-hidden="true"></i> ${escapeHTML(section.heading).toUpperCase()}</div>
        <ul class="detail-list">
          ${(section.items || []).map((detail) => `<li>${escapeHTML(detail)}</li>`).join("")}
        </ul>
      </section>
    `).join("");
  }

  function renderArchitecture(data) {
    if (!Array.isArray(data.architecture) || !data.architecture.length) return "";

    return `
      <section class="detail-section" aria-label="Arquitectura">
        <div class="detail-section-heading"><i class="bi bi-diagram-3" aria-hidden="true"></i> ARQUITECTURA</div>
        <ol class="architecture-flow">
          ${data.architecture.map((step) => `<li>${escapeHTML(step)}</li>`).join("")}
        </ol>
      </section>
    `;
  }

  function renderGallery(data) {
    if (!Array.isArray(data.gallery) || !data.gallery.length) return "";
    const heading = data.kind === "certificate" || data.kind === "degree" ? "EVIDENCIA ADICIONAL" : "PANTALLAS ANONIMIZADAS";
    const aria = data.kind === "certificate" || data.kind === "degree" ? "Evidencia adicional" : "Pantallas de ControlBins";

    return `
      <section class="detail-section" aria-label="${aria}">
        <div class="detail-section-heading"><i class="bi bi-images" aria-hidden="true"></i> ${heading}</div>
        <div class="case-gallery">
          ${data.gallery.map((image) => `
            <figure>
              <button class="image-preview-trigger" type="button" data-image-preview data-image-src="${escapeHTML(image.src)}" data-image-alt="${escapeHTML(image.alt || "Evidencia visual")}" data-image-caption="${escapeHTML(image.caption || "")}" aria-label="Ver imagen en grande">
                <img src="${escapeHTML(image.src)}" alt="${escapeHTML(image.alt || "Evidencia visual")}" loading="lazy" decoding="async" onerror="this.closest('figure').hidden=true">
              </button>
              ${image.caption ? `<figcaption>${escapeHTML(image.caption)}</figcaption>` : ""}
            </figure>
          `).join("")}
        </div>
      </section>
    `;
  }

  function renderEvidence(data) {
    const evidence = data.evidence;
    if (!evidence || !evidence.src) return "";

    return `
      <section class="certificate-evidence" aria-label="Evidencia visual">
        <div class="detail-section-heading"><i class="bi bi-file-earmark-image" aria-hidden="true"></i> EVIDENCIA</div>
        <figure>
          <button class="image-preview-trigger" type="button" data-image-preview data-image-src="${escapeHTML(evidence.src)}" data-image-alt="${escapeHTML(evidence.alt || data.label || "Certificado")}" data-image-caption="${escapeHTML(evidence.caption || "")}" aria-label="Ver certificado en grande">
            <img src="${escapeHTML(evidence.src)}" alt="${escapeHTML(evidence.alt || data.label || "Certificado")}" loading="lazy" decoding="async" onerror="this.closest('.certificate-evidence').hidden=true">
          </button>
          ${evidence.caption ? `<figcaption>${escapeHTML(evidence.caption)}</figcaption>` : ""}
        </figure>
      </section>
    `;
  }

  function renderCredentialMeta(data) {
    const values = [
      data.issuer ? ["Institución", data.issuer] : null,
      data.date ? ["Fecha", data.date] : null,
      data.badge ? ["Credencial", data.badge] : null,
    ].filter(Boolean);
    if (!values.length || !(data.kind === "certificate" || data.kind === "degree")) return "";

    return `
      <div class="credential-meta" aria-label="Datos de la credencial">
        ${values.map(([label, value]) => `
          <span>
            <small>${escapeHTML(label)}</small>
            <strong>${escapeHTML(value)}</strong>
          </span>
        `).join("")}
      </div>
    `;
  }

  function renderSimulation(data) {
    const simulation = data.simulation;
    if (!simulation || !Array.isArray(simulation.steps) || !simulation.steps.length) return "";

    return `
      <section class="sync-simulation sync-simulation-card" aria-label="${escapeHTML(simulation.title || "Caso de uso de sincronizacion")}">
        <div class="simulation-heading">
          <span><i class="bi bi-cpu" aria-hidden="true"></i> CASO DE USO / SINCRONIZACION</span>
          <button class="simulation-run" type="button" data-sim-open>Ver caso de uso</button>
        </div>
        <p class="simulation-copy">${escapeHTML(simulation.summary || "Flujo offline-first de ControlBins explicado como simulacion visual.")}</p>
      </section>
    `;
  }

  function renderSimulationExperience(data) {
    const simulation = data.simulation;
    if (!simulation || !Array.isArray(simulation.steps) || !simulation.steps.length) return "";

    const sample = simulation.sample || {};
    const fields = Object.entries(sample)
      .map(([key, value]) => `
        <div class="sim-field">
          <span>${escapeHTML(key.replaceAll("_", " "))}</span>
          <strong>${escapeHTML(String(value))}</strong>
        </div>
      `)
      .join("");

    return `
      <section class="sync-simulation" aria-label="${escapeHTML(simulation.title || "Simulación de sincronización")}">
        <div class="simulation-heading">
          <span><i class="bi bi-cpu" aria-hidden="true"></i> ${escapeHTML(simulation.title || "Flujo de sincronización").toUpperCase()}</span>
          <span class="simulation-controls">
            <button class="simulation-run" type="button" data-sim-run>Simular flujo</button>
            <button class="simulation-run simulation-step" type="button" data-sim-step>Paso a paso</button>
          </span>
        </div>
        ${simulation.summary ? `<p class="simulation-copy">${escapeHTML(simulation.summary)}</p>` : ""}
        <div class="simulation-stage">
          <div class="sim-phone" aria-label="Formulario Android anonimizado">
            <span class="sim-phone-bar"></span>
            <div class="sim-phone-title">Ingreso de bin</div>
            <div class="sim-form">${fields}</div>
          </div>
          <div class="sim-pipeline" aria-label="Pipeline offline-first">
            <span class="sim-packet" aria-hidden="true"></span>
            ${simulation.steps.map((step, index) => `
              <article class="sim-node" data-sim-node="${index}" role="button" tabindex="0">
                <i class="bi ${escapeHTML(step.icon || "bi-circle")}" aria-hidden="true"></i>
                <strong>${escapeHTML(step.label)}</strong>
                <span>${escapeHTML(step.detail)}</span>
              </article>
            `).join("")}
          </div>
        </div>
        <div class="sim-log" aria-live="polite">Dato listo para guardar localmente.</div>
      </section>
    `;
  }

  function showPanel(data) {
    const items = data.children || [];
    const itemHTML = items
      .map(
        (item, index) => `
          <button class="detail-item detail-item-button" type="button" data-detail-index="${index}" aria-label="Abrir detalle de ${escapeHTML(item.label)}">
            <span class="detail-item-icon">${item.image ? `<img class="detail-item-image" src="${escapeHTML(item.image)}" alt="Logo de ${escapeHTML(item.label)}" loading="lazy" decoding="async" />` : `<i class="bi ${escapeHTML(item.icon || "bi-circle")}" aria-hidden="true"></i>`}</span>
            <strong>${escapeHTML(item.label)}</strong>
            ${(item.level || item.badge) ? `<span class="detail-level">${escapeHTML(item.level || item.badge)}</span>` : ""}
            <span>${escapeHTML(item.text || item.content || "Selecciona para ver el detalle completo.")}</span>
          </button>
        `
      )
      .join("");
    const leafDescription = data.text || data.description;
    const valueHTML = leafDescription && !items.length
      ? `<section class="detail-description"><div class="detail-section-heading"><i class="bi bi-info-circle" aria-hidden="true"></i> DETALLE DEL NODO</div><p class="detail-copy detail-value">${escapeHTML(leafDescription)}</p></section>`
      : "";
    const detailsHTML = Array.isArray(data.details) && data.details.length
      ? `
        <section class="detail-section" aria-label="Responsabilidades y logros">
          <div class="detail-section-heading"><i class="bi bi-list-check" aria-hidden="true"></i> RESPONSABILIDADES / LOGROS</div>
          <ul class="detail-list">
            ${data.details.map((detail) => `<li>${escapeHTML(detail)}</li>`).join("")}
          </ul>
        </section>
      `
      : "";
    const noteHTML = data.note
      ? `<p class="case-note"><i class="bi bi-shield-lock" aria-hidden="true"></i>${escapeHTML(data.note)}</p>`
      : "";
    const tagsHTML = Array.isArray(data.tags) && data.tags.length
      ? `
        <div class="detail-tags" aria-label="Tecnologías y conceptos">
          ${data.tags.map((tag) => `<span>${escapeHTML(tag)}</span>`).join("")}
        </div>
      `
      : "";
    const relatedProject = data.related_project || null;
    const projectCardHTML = relatedProject || data.href
      ? `
        <div class="project-card" aria-label="${escapeHTML(relatedProject ? (relatedProject.label || "Proyecto relacionado") : "Proyecto relacionado")}">
          <div class="project-card-header">
            <span class="project-card-kicker">Proyecto</span>
            <span class="project-card-badge">Abrir</span>
          </div>
          <h3 class="project-card-title">${escapeHTML(relatedProject ? (relatedProject.label || "Proyecto") : (data.label || "Proyecto"))}</h3>
          <p class="project-card-copy">${escapeHTML(relatedProject ? (relatedProject.text || relatedProject.content || "Abre el proyecto para revisar el caso completo.") : (data.text || data.content || "Abre el enlace para revisar el proyecto completo."))}</p>
          ${relatedProject ? `<button class="project-cta" type="button" data-related-project>Ver proyecto <span aria-hidden="true">↗</span></button>` : ""}
          ${data.href ? `<a class="detail-action" href="${escapeHTML(data.href)}" target="_blank" rel="noopener">Abrir enlace <span aria-hidden="true">&#8599;</span></a>` : ""}
        </div>
      `
      : "";
    const actionHTML = data.href && !relatedProject
      ? `<a class="detail-action" href="${escapeHTML(data.href)}" target="_blank" rel="noopener">Abrir enlace <span aria-hidden="true">&#8599;</span></a>`
      : "";
    const routeHTML = data.route
      ? `
        <section class="route-module" aria-label="Trayectoria hacia INACAP Sede La Serena">
          <div class="route-heading">
            <span><i class="bi bi-sign-turn-right-fill" aria-hidden="true"></i> RUTA / INACAP</span>
            <span class="route-status">GPS listo bajo autorización</span>
          </div>
          <div class="route-viewport">
            <svg class="route-svg" viewBox="0 0 420 170" role="img" aria-label="Trayectoria desde la posición actual hasta INACAP">
              <defs>
                <linearGradient id="route-gradient" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#18d8ff" />
                  <stop offset="100%" stop-color="#35f2a7" />
                </linearGradient>
                <filter id="route-glow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="4" result="blur" />
                  <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                </filter>
              </defs>
              <path class="route-grid-line" d="M0 34H420 M0 85H420 M0 136H420 M70 0V170 M210 0V170 M350 0V170" />
              <path class="route-path-glow" d="M24 132 C92 24 138 151 210 82 S326 18 396 40" />
              <path class="route-path" d="M24 132 C92 24 138 151 210 82 S326 18 396 40" />
              <path class="route-progress" d="M24 132 C92 24 138 151 210 82 S326 18 396 40" />
              <circle class="route-node route-origin" cx="24" cy="132" r="7" />
              <circle class="route-node route-destination" cx="396" cy="40" r="7" />
              <circle class="route-runner" cx="0" cy="0" r="5" />
              <text class="route-label" x="16" y="157">POSICIÓN ACTUAL</text>
              <text class="route-label route-label-end" x="302" y="28">INACAP / LA SERENA</text>
            </svg>
            <div class="route-hud" aria-live="polite">
              <span class="route-distance">-- km</span>
              <span class="route-location">Ubicación pendiente</span>
            </div>
          </div>
          <div class="route-footer">
            <span>La ubicación se solicita solo al trazar la ruta.</span>
            <button class="route-action" type="button" data-route-action>Trazar ruta</button>
            <a class="route-map-link" href="${escapeHTML(data.map_link || data.directions_link || "#")}" target="_blank" rel="noopener">Abrir Maps <span aria-hidden="true">&#8599;</span></a>
          </div>
        </section>
      `
      : "";
    const mapHTML = data.map_embed && !data.route
      ? `
        <section class="map-module" aria-label="Ubicación de INACAP La Serena">
          <div class="map-heading">
            <span><i class="signal-dot"></i> INACAP / LA SERENA</span>
            <span>MAPS.LINK</span>
          </div>
          <div class="map-viewport">
            <iframe
              src="${escapeHTML(data.map_embed)}"
              title="Mapa de INACAP Sede La Serena"
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
            ></iframe>
            <span class="map-scan" aria-hidden="true"></span>
            <span class="map-pulse" aria-hidden="true"></span>
          </div>
          <div class="map-footer">
            <span>${escapeHTML(data.map_address || "Ubicación académica")}</span>
            <a href="${escapeHTML(data.map_link || data.map_embed)}" target="_blank" rel="noopener">Abrir Maps <span aria-hidden="true">&#8599;</span></a>
          </div>
        </section>
      `
      : "";

    content.innerHTML = `
      <p class="detail-eyebrow">${escapeHTML(currentLevel === "children" ? "Módulo activo" : "Perfil base")}</p>
      <h2 class="detail-title">${escapeHTML(data.label || data.name)}</h2>
      ${data.content ? `<p class="detail-copy">${escapeHTML(data.content)}</p>` : ""}
      ${valueHTML}
      ${detailsHTML}
      ${renderCredentialMeta(data)}
      ${renderSections(data)}
      ${renderArchitecture(data)}
      ${renderSimulation(data)}
      ${tagsHTML}
      ${renderEvidence(data)}
      ${renderGallery(data)}
      ${noteHTML}
      ${projectCardHTML}
      ${actionHTML}
      ${itemHTML ? `<div class="detail-grid">${itemHTML}</div>` : ""}
      ${routeHTML}
      ${mapHTML}
    `;

    content.querySelectorAll("[data-detail-index]").forEach((itemButton) => {
      itemButton.addEventListener("click", () => {
        const item = items[Number(itemButton.dataset.detailIndex)];
        if (item) showPanel(item);
      });
    });

    content.querySelectorAll("[data-route-action]").forEach((routeButton) => {
      routeButton.addEventListener("click", () => startRoute(data, routeButton));
    });

    content.querySelectorAll("[data-related-project]").forEach((projectButton) => {
      projectButton.addEventListener("click", () => {
        if (relatedProject) showPanel(relatedProject);
      });
    });

    content.querySelectorAll("[data-sim-open]").forEach((simButton) => {
      simButton.addEventListener("click", () => openSimulationModal(data));
    });

    content.querySelectorAll("[data-image-preview]").forEach((previewButton) => {
      previewButton.addEventListener("click", () => openImageModal({
        src: previewButton.dataset.imageSrc,
        alt: previewButton.dataset.imageAlt,
        caption: previewButton.dataset.imageCaption,
      }));
    });

    panel.style.display = "block";
    document.body.classList.add("panel-open");
    document.body.classList.remove("panel-collapsed");
    requestAnimationFrame(() => relayoutCurrentScene());
    window.setTimeout(relayoutCurrentScene, 280);
    panel.setAttribute("aria-hidden", "false");
    panel.classList.remove("is-collapsed");
    if (toggleButton) {
      toggleButton.setAttribute("aria-expanded", "true");
      toggleButton.setAttribute("aria-label", "Minimizar panel");
      toggleButton.setAttribute("title", "Minimizar panel");
      toggleButton.innerHTML = '<i class="bi bi-dash-lg" aria-hidden="true"></i>';
    }
    panel.classList.add("is-loading");
    window.setTimeout(() => panel.classList.remove("is-loading"), prefersReduced ? 0 : 240);

    // Force a stable layout after the panel is shown so nodes are positioned
    // correctly relative to the resized scene (especially on mobile landscape).
    stabilizeLayout();

    if (!prefersReduced) {
      animeDriver.remove(panel);
      animeDriver({
        targets: panel,
        opacity: [0, 1],
        translateX: [34, 0],
        duration: 420,
        easing: "easeOutExpo",
      });

      const routePath = panel.querySelector(".route-path");
      const routeRunner = panel.querySelector(".route-runner");
      if (routePath) {
        const routeLength = typeof routePath.getTotalLength === "function" ? routePath.getTotalLength() : 800;
        routePath.style.strokeDasharray = routeLength;
        routePath.style.strokeDashoffset = routeLength;
        animeDriver({
          targets: routePath,
          strokeDashoffset: [routeLength, 0],
          duration: 1800,
          easing: "easeInOutSine",
        });

        if (!performanceLite && routeRunner && typeof animeDriver.path === "function") {
          const motionPath = animeDriver.path(routePath);
          animeDriver({
            targets: routeRunner,
            translateX: motionPath("x"),
            translateY: motionPath("y"),
            rotate: motionPath("angle"),
            duration: 2600,
            easing: "linear",
            loop: true,
          });
        }
      }
    }
    // log event for diagnostics
    logLayoutEvent("panel:show", { id: data.id || data.label, level: currentLevel });
    stabilizeLayout();
  }

  function ensureSimulationModal() {
    if (simulationModal) return simulationModal;

    simulationModal = document.createElement("div");
    simulationModal.className = "simulation-modal";
    simulationModal.setAttribute("aria-hidden", "true");
    simulationModal.innerHTML = `
      <div class="simulation-backdrop" data-sim-close></div>
      <section class="simulation-dialog" role="dialog" aria-modal="true" aria-labelledby="simulation-title">
        <button class="icon-button simulation-close" type="button" data-sim-close aria-label="Cerrar caso de uso" title="Cerrar">
          <i class="bi bi-x-lg" aria-hidden="true"></i>
        </button>
        <div class="simulation-dialog-content"></div>
      </section>
    `;
    document.body.appendChild(simulationModal);
    simulationModal.querySelectorAll("[data-sim-close]").forEach((button) => {
      button.addEventListener("click", closeSimulationModal);
    });
    return simulationModal;
  }

  function openSimulationModal(data) {
    const modal = ensureSimulationModal();
    const modalContent = modal.querySelector(".simulation-dialog-content");
    if (!modalContent) return;

    modalContent.innerHTML = `
      <p class="detail-eyebrow">Caso de uso</p>
      <h2 id="simulation-title" class="detail-title">${escapeHTML(data.label || "ControlBins")}</h2>
      <p class="detail-copy">${escapeHTML(data.text || "Flujo de sincronizacion offline-first.")}</p>
      ${renderSimulationExperience(data)}
    `;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");

    const runButton = modal.querySelector("[data-sim-run]");
    if (runButton) runButton.addEventListener("click", () => runSyncSimulation(data, runButton, modal));
    const stepButton = modal.querySelector("[data-sim-step]");
    if (stepButton) stepButton.addEventListener("click", () => stepSyncSimulation(data, stepButton, modal));
    modal.querySelectorAll("[data-sim-node]").forEach((node) => {
      node.addEventListener("click", () => markSimulationStep(data, Number(node.dataset.simNode), modal, { completePrevious: true, movePacket: true }));
      node.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          markSimulationStep(data, Number(node.dataset.simNode), modal, { completePrevious: true, movePacket: true });
        }
      });
    });

    if (!prefersReduced) {
      const dialog = modal.querySelector(".simulation-dialog");
      animeDriver.remove(dialog);
      animeDriver({
        targets: dialog,
        opacity: [0, 1],
        translateY: [26, 0],
        scale: [0.98, 1],
        duration: 360,
        easing: "easeOutExpo",
      });
    }
  }

  function closeSimulationModal() {
    if (!simulationModal) return;
    simulationModal.classList.remove("is-open");
    simulationModal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
  }

  function ensureImageModal() {
    if (imageModal) return imageModal;

    imageModal = document.createElement("div");
    imageModal.className = "image-modal";
    imageModal.setAttribute("aria-hidden", "true");
    imageModal.innerHTML = `
      <div class="image-modal-backdrop" data-image-close></div>
      <section class="image-dialog" role="dialog" aria-modal="true" aria-labelledby="image-modal-title">
        <button class="icon-button image-close" type="button" data-image-close aria-label="Cerrar imagen" title="Cerrar">
          <i class="bi bi-x-lg" aria-hidden="true"></i>
        </button>
        <div class="image-toolbar" aria-label="Controles de zoom">
          <button class="icon-button" type="button" data-image-zoom="out" aria-label="Alejar imagen" title="Alejar">
            <i class="bi bi-zoom-out" aria-hidden="true"></i>
          </button>
          <span class="image-zoom-label" aria-live="polite">100%</span>
          <button class="icon-button" type="button" data-image-zoom="in" aria-label="Acercar imagen" title="Acercar">
            <i class="bi bi-zoom-in" aria-hidden="true"></i>
          </button>
          <button class="icon-button" type="button" data-image-zoom="reset" aria-label="Restablecer zoom" title="Restablecer">
            <i class="bi bi-arrows-angle-contract" aria-hidden="true"></i>
          </button>
        </div>
        <figure class="image-dialog-figure">
          <div class="image-viewport">
            <img class="image-dialog-img" src="" alt="" draggable="false">
          </div>
          <figcaption id="image-modal-title" class="image-dialog-caption"></figcaption>
        </figure>
      </section>
    `;
    document.body.appendChild(imageModal);
    imageModal.querySelectorAll("[data-image-close]").forEach((button) => {
      button.addEventListener("click", closeImageModal);
    });
    imageModal.querySelectorAll("[data-image-zoom]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.imageZoom;
        if (action === "in") setImageZoom(imageZoomState.scale + 0.35);
        if (action === "out") setImageZoom(imageZoomState.scale - 0.35);
        if (action === "reset") resetImageZoom();
      });
    });

    const viewport = imageModal.querySelector(".image-viewport");
    if (viewport) {
      viewport.addEventListener("wheel", handleImageWheel, { passive: false });
      viewport.addEventListener("dblclick", handleImageDoubleClick);
      viewport.addEventListener("pointerdown", handleImagePointerDown);
      viewport.addEventListener("pointermove", handleImagePointerMove);
      viewport.addEventListener("pointerup", handleImagePointerUp);
      viewport.addEventListener("pointercancel", handleImagePointerUp);
      viewport.addEventListener("touchstart", handleImageTouchStart, { passive: false });
      viewport.addEventListener("touchmove", handleImageTouchMove, { passive: false });
      viewport.addEventListener("touchend", handleImageTouchEnd);
      viewport.addEventListener("touchcancel", handleImageTouchEnd);
    }

    return imageModal;
  }

  function openImageModal(image) {
    if (!image || !image.src) return;
    const modal = ensureImageModal();
    const img = modal.querySelector(".image-dialog-img");
    const caption = modal.querySelector(".image-dialog-caption");
    if (!img || !caption) return;

    img.src = image.src;
    img.alt = image.alt || "Evidencia visual";
    caption.textContent = image.caption || image.alt || "Evidencia visual";
    caption.hidden = !caption.textContent;
    resetImageZoom();
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");

    const close = modal.querySelector(".image-close");
    if (close) close.focus({ preventScroll: true });

    if (!prefersReduced) {
      const dialog = modal.querySelector(".image-dialog");
      animeDriver.remove(dialog);
      animeDriver({
        targets: dialog,
        opacity: [0, 1],
        scale: [0.97, 1],
        duration: 260,
        easing: "easeOutExpo",
      });
    }
  }

  function closeImageModal() {
    if (!imageModal) return;
    imageModal.classList.remove("is-open");
    imageModal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    resetImageZoom();
  }

  function imageParts() {
    if (!imageModal) return {};
    return {
      img: imageModal.querySelector(".image-dialog-img"),
      viewport: imageModal.querySelector(".image-viewport"),
      label: imageModal.querySelector(".image-zoom-label"),
    };
  }

  function clampImagePan() {
    const { viewport } = imageParts();
    if (!viewport || imageZoomState.scale <= 1) {
      imageZoomState.x = 0;
      imageZoomState.y = 0;
      return;
    }
    const rect = viewport.getBoundingClientRect();
    const maxX = Math.max(0, (rect.width * (imageZoomState.scale - 1)) / 2);
    const maxY = Math.max(0, (rect.height * (imageZoomState.scale - 1)) / 2);
    imageZoomState.x = Math.max(-maxX, Math.min(maxX, imageZoomState.x));
    imageZoomState.y = Math.max(-maxY, Math.min(maxY, imageZoomState.y));
  }

  function applyImageZoom() {
    const { img, label, viewport } = imageParts();
    if (!img) return;
    clampImagePan();
    img.style.transform = `translate3d(${imageZoomState.x}px, ${imageZoomState.y}px, 0) scale(${imageZoomState.scale})`;
    if (label) label.textContent = `${Math.round(imageZoomState.scale * 100)}%`;
    if (viewport) viewport.classList.toggle("is-zoomed", imageZoomState.scale > 1.01);
  }

  function setImageZoom(scale) {
    imageZoomState.scale = Math.max(1, Math.min(4, Number(scale) || 1));
    if (imageZoomState.scale <= 1.01) {
      imageZoomState.scale = 1;
      imageZoomState.x = 0;
      imageZoomState.y = 0;
    }
    applyImageZoom();
  }

  function resetImageZoom() {
    imageZoomState.scale = 1;
    imageZoomState.x = 0;
    imageZoomState.y = 0;
    imageZoomState.dragging = false;
    imageZoomState.touchDistance = 0;
    applyImageZoom();
  }

  function handleImageWheel(event) {
    if (!imageModal || !imageModal.classList.contains("is-open")) return;
    event.preventDefault();
    const delta = event.deltaY < 0 ? 0.22 : -0.22;
    setImageZoom(imageZoomState.scale + delta);
  }

  function handleImageDoubleClick() {
    setImageZoom(imageZoomState.scale > 1.01 ? 1 : 2.2);
  }

  function handleImagePointerDown(event) {
    if (imageZoomState.scale <= 1.01) return;
    const { viewport } = imageParts();
    imageZoomState.dragging = true;
    imageZoomState.startX = event.clientX;
    imageZoomState.startY = event.clientY;
    imageZoomState.originX = imageZoomState.x;
    imageZoomState.originY = imageZoomState.y;
    if (viewport && event.pointerId !== undefined) viewport.setPointerCapture(event.pointerId);
  }

  function handleImagePointerMove(event) {
    if (!imageZoomState.dragging) return;
    imageZoomState.x = imageZoomState.originX + event.clientX - imageZoomState.startX;
    imageZoomState.y = imageZoomState.originY + event.clientY - imageZoomState.startY;
    applyImageZoom();
  }

  function handleImagePointerUp(event) {
    const { viewport } = imageParts();
    imageZoomState.dragging = false;
    if (viewport && event.pointerId !== undefined && viewport.hasPointerCapture(event.pointerId)) {
      viewport.releasePointerCapture(event.pointerId);
    }
  }

  function touchDistance(touches) {
    if (!touches || touches.length < 2) return 0;
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.hypot(dx, dy);
  }

  function handleImageTouchStart(event) {
    if (event.touches.length === 2) {
      event.preventDefault();
      imageZoomState.touchDistance = touchDistance(event.touches);
      imageZoomState.originX = imageZoomState.x;
      imageZoomState.originY = imageZoomState.y;
      imageZoomState.startX = (event.touches[0].clientX + event.touches[1].clientX) / 2;
      imageZoomState.startY = (event.touches[0].clientY + event.touches[1].clientY) / 2;
    }
  }

  function handleImageTouchMove(event) {
    if (event.touches.length !== 2 || !imageZoomState.touchDistance) return;
    event.preventDefault();
    const nextDistance = touchDistance(event.touches);
    const centerX = (event.touches[0].clientX + event.touches[1].clientX) / 2;
    const centerY = (event.touches[0].clientY + event.touches[1].clientY) / 2;
    const scaleRatio = nextDistance / imageZoomState.touchDistance;
    imageZoomState.x = imageZoomState.originX + (centerX - imageZoomState.startX);
    imageZoomState.y = imageZoomState.originY + (centerY - imageZoomState.startY);
    setImageZoom(imageZoomState.scale * scaleRatio);
    imageZoomState.touchDistance = nextDistance;
    imageZoomState.originX = imageZoomState.x;
    imageZoomState.originY = imageZoomState.y;
    imageZoomState.startX = centerX;
    imageZoomState.startY = centerY;
  }

  function handleImageTouchEnd() {
    imageZoomState.touchDistance = 0;
  }

  function resetSimulation(root) {
    const nodes = Array.from(root.querySelectorAll("[data-sim-node]"));
    const packet = root.querySelector(".sim-packet");
    const log = root.querySelector(".sim-log");
    animeDriver.remove([packet, ...nodes].filter(Boolean));
    root.dataset.simStepIndex = "-1";
    nodes.forEach((node) => node.classList.remove("is-active", "is-complete"));
    if (packet) {
      packet.style.opacity = "0";
      packet.style.transform = "translate(0, 0)";
    }
    if (log) log.textContent = "Dato listo para guardar localmente.";
  }

  function markSimulationStep(data, index, root, options = {}) {
    const simulation = data.simulation || {};
    const steps = simulation.steps || [];
    const nodes = Array.from(root.querySelectorAll("[data-sim-node]"));
    const packet = root.querySelector(".sim-packet");
    const log = root.querySelector(".sim-log");
    const node = nodes[index];
    const step = steps[index];
    if (!node || !step) return;

    nodes.forEach((item, itemIndex) => {
      item.classList.remove("is-active");
      if (options.completePrevious && itemIndex <= index) item.classList.add("is-complete");
    });
    node.classList.add("is-active", "is-complete");
    root.dataset.simStepIndex = String(index);
    if (log) log.textContent = `${step.label}: ${step.detail}`;

    if (packet && options.movePacket) {
      const targetX = node.offsetLeft + 18;
      const targetY = node.offsetTop + 18;
      packet.style.opacity = "1";
      if (prefersReduced) {
        packet.style.transform = `translate(${targetX}px, ${targetY}px)`;
      } else {
        animeDriver.remove(packet);
        animeDriver({
          targets: packet,
          translateX: targetX,
          translateY: targetY,
          duration: 420,
          easing: "easeInOutSine",
        });
      }
    }
  }

  function stepSyncSimulation(data, trigger, root) {
    const steps = data.simulation?.steps || [];
    if (!steps.length) return;
    const current = Number(root.dataset.simStepIndex || "-1");
    const next = current + 1 >= steps.length ? 0 : current + 1;
    if (next === 0) resetSimulation(root);
    markSimulationStep(data, next, root, { completePrevious: true, movePacket: true });
    if (trigger) trigger.textContent = next + 1 >= steps.length ? "Reiniciar pasos" : "Siguiente paso";
  }

  function runSyncSimulation(data, trigger, root = panel) {
    const simulation = data.simulation || {};
    const nodes = Array.from(root.querySelectorAll("[data-sim-node]"));
    const packet = root.querySelector(".sim-packet");
    const log = root.querySelector(".sim-log");
    if (!nodes.length || !packet) return;

    const steps = simulation.steps || [];
    if (trigger) trigger.disabled = true;
    resetSimulation(root);

    const setLog = (index) => {
      const step = steps[index];
      if (log && step) log.textContent = `${step.label}: ${step.detail}`;
    };

    if (prefersReduced) {
      nodes.forEach((node, index) => {
        markSimulationStep(data, index, root, { completePrevious: true, movePacket: true });
      });
      if (trigger) trigger.disabled = false;
      return;
    }

    animeDriver.remove([packet, ...nodes]);
    packet.style.opacity = "1";
    packet.style.transform = "translate(0, 0)";

    const timeline = animeDriver.timeline({
      easing: "easeInOutSine",
      complete: () => {
        if (trigger) trigger.disabled = false;
        if (log) log.textContent = "Sincronización completada: el bin queda confirmado entre SQLite, API y SQL Server.";
      },
    });

    nodes.forEach((node, index) => {
      const targetX = node.offsetLeft + 18;
      const targetY = node.offsetTop + 18;
      timeline
        .add({
          targets: packet,
          translateX: targetX,
          translateY: targetY,
          duration: index === 0 ? 620 : 820,
          begin: () => {
            nodes.forEach((item) => item.classList.remove("is-active"));
          },
          complete: () => {
            node.classList.add("is-active", "is-complete");
            setLog(index);
          },
        })
        .add({
          targets: node,
          scale: [1, 1.035, 1],
          duration: 380,
          endDelay: 1750,
          complete: () => {
            node.classList.remove("is-active");
            node.classList.add("is-complete");
          },
        });
    });
  }

  function calculateDistanceKm(originLat, originLng, destinationLat, destinationLng) {
    const toRad = (value) => value * Math.PI / 180;
    const earthKm = 6371;
    const dLat = toRad(destinationLat - originLat);
    const dLng = toRad(destinationLng - originLng);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(originLat)) * Math.cos(toRad(destinationLat)) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return earthKm * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function animateRouteProgress() {
    const progressPath = panel.querySelector(".route-progress");
    const routeRunner = panel.querySelector(".route-runner");
    if (!progressPath) return;

    const routeLength = typeof progressPath.getTotalLength === "function" ? progressPath.getTotalLength() : 800;
    progressPath.style.strokeDasharray = routeLength;
    progressPath.style.strokeDashoffset = routeLength;

    if (prefersReduced) {
      progressPath.style.strokeDashoffset = 0;
      return;
    }

    animeDriver.remove([progressPath, routeRunner].filter(Boolean));
    animeDriver({
      targets: progressPath,
      strokeDashoffset: [routeLength, 0],
      duration: 1900,
      easing: "easeInOutSine",
    });

    if (routeRunner && typeof animeDriver.path === "function") {
      const motionPath = animeDriver.path(progressPath);
      animeDriver({
        targets: routeRunner,
        translateX: motionPath("x"),
        translateY: motionPath("y"),
        rotate: motionPath("angle"),
        duration: 2100,
        easing: "easeInOutSine",
      });
    }
  }

  function routeFallbackDistance(data, statusText, locationText) {
    const routeStatus = panel.querySelector(".route-status");
    const routeDistance = panel.querySelector(".route-distance");
    const routeLocation = panel.querySelector(".route-location");
    const routeMapLink = panel.querySelector(".route-map-link");
    const originLat = Number(data.route_fallback_origin_lat);
    const originLng = Number(data.route_fallback_origin_lng);
    const destinationLat = Number(data.route_destination_lat);
    const destinationLng = Number(data.route_destination_lng);

    if (routeStatus) routeStatus.textContent = statusText;
    if (routeLocation) routeLocation.textContent = locationText;
    if (
      routeDistance &&
      Number.isFinite(originLat) &&
      Number.isFinite(originLng) &&
      Number.isFinite(destinationLat) &&
      Number.isFinite(destinationLng)
    ) {
      const km = calculateDistanceKm(originLat, originLng, destinationLat, destinationLng);
      routeDistance.textContent = `${km.toFixed(km < 10 ? 1 : 0)} km aprox. desde ${data.route_fallback_origin || "referencia"}`;
    }
    animateRouteProgress();
  }

  function explainLocationBlock(error) {
    if (!error) return "El navegador no entrego la ubicacion.";
    if (error.code === 1) return "Permiso bloqueado. Activalo desde el candado de la barra de direcciones.";
    if (error.code === 2) return "No se pudo obtener una posicion estable en este momento.";
    if (error.code === 3) return "La solicitud tardo demasiado. Intenta de nuevo.";
    return "No se pudo usar la ubicacion del navegador.";
  }

  async function startRoute(data, trigger) {
    const routeStatus = panel.querySelector(".route-status");
    const routeDistance = panel.querySelector(".route-distance");
    const routeLocation = panel.querySelector(".route-location");
    const destination = data.route_destination || data.map_address || "INACAP Sede La Serena";
    const fallback = data.directions_link || data.map_link || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(destination)}`;
    const destinationLat = Number(data.route_destination_lat);
    const destinationLng = Number(data.route_destination_lng);

    if (!navigator.geolocation) {
      routeFallbackDistance(data, "GPS no disponible", "Este navegador no permite pedir ubicacion. Usa Abrir Maps si quieres ver la ruta.");
      return;
    }

    if (!window.isSecureContext) {
      routeFallbackDistance(
        data,
        "GPS bloqueado por origen no seguro",
        "Abre la pagina en localhost o HTTPS para que el navegador pueda pedir permiso."
      );
      return;
    }

    if (navigator.permissions && navigator.permissions.query) {
      try {
        const permission = await navigator.permissions.query({ name: "geolocation" });
        if (permission.state === "denied") {
          routeFallbackDistance(
            data,
            "Ubicacion bloqueada",
            "Activa Ubicacion desde el candado del navegador y vuelve a trazar."
          );
          return;
        }
      } catch (error) {
        // Algunos navegadores no permiten consultar este permiso; se intenta pedir ubicacion directo.
      }
    }

    if (routeStatus) routeStatus.textContent = "Solicitando ubicacion...";
    if (routeLocation) routeLocation.textContent = "Acepta el permiso del navegador para calcular desde tu posicion";
    if (trigger) trigger.disabled = true;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        const origin = `${lat},${lng}`;
        const url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&travelmode=driving`;
        if (Number.isFinite(destinationLat) && Number.isFinite(destinationLng)) {
          const km = calculateDistanceKm(lat, lng, destinationLat, destinationLng);
          if (routeDistance) routeDistance.textContent = `${km.toFixed(km < 10 ? 1 : 0)} km aprox.`;
        }
        if (routeLocation) routeLocation.textContent = `Tu ubicacion: ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        if (routeStatus) routeStatus.textContent = "Linea de ruta calculada";
        if (routeMapLink) routeMapLink.href = url;
        if (trigger) trigger.disabled = false;
        animateRouteProgress();
      },
      (error) => {
        routeFallbackDistance(
          data,
          "Usando distancia de referencia",
          explainLocationBlock(error)
        );
        if (trigger) trigger.disabled = false;
      },
      { enableHighAccuracy: true, timeout: 9000, maximumAge: 300000 }
    );
  }

  function hidePanel() {
    panel.style.display = "none";
    document.body.classList.remove("panel-open");
    document.body.classList.remove("panel-collapsed");
    panel.setAttribute("aria-hidden", "true");
    panel.classList.remove("is-collapsed");
    panel.classList.remove("is-loading");
    content.innerHTML = "";
    // Recompute layout when panel is hidden so scene expands back.
    stabilizeLayout();
  }

  function togglePanel() {
    if (!toggleButton) return;

    const collapsed = panel.classList.toggle("is-collapsed");
    document.body.classList.toggle("panel-collapsed", collapsed);
    toggleButton.setAttribute("aria-expanded", String(!collapsed));
    toggleButton.setAttribute("aria-label", collapsed ? "Expandir panel" : "Minimizar panel");
    toggleButton.setAttribute("title", collapsed ? "Expandir panel" : "Minimizar panel");
    toggleButton.innerHTML = `<i class="bi ${collapsed ? "bi-arrows-angle-expand" : "bi-dash-lg"}" aria-hidden="true"></i>`;

    if (!prefersReduced) {
      animeDriver({
        targets: panel,
        scale: collapsed ? [1, 0.96] : [0.96, 1],
        duration: 260,
        easing: "easeOutExpo",
      });
    }
    relayoutCurrentScene();
    // Ensure layout is stable after collapsing/expanding
    stabilizeLayout();
    logLayoutEvent("panel:toggle", { collapsed });
  }

  if (toggleButton) toggleButton.addEventListener("click", togglePanel);
  if (closeButton) {
    closeButton.addEventListener("click", () => {
      if (currentLevel === "children") {
        renderHome();
      } else {
        hidePanel();
      }
    });
  }

  window.addEventListener("keydown", (event) => {
    const imageIsOpen = imageModal && imageModal.classList.contains("is-open");
    if (event.key === "Escape") {
      if (imageIsOpen) {
        closeImageModal();
        return;
      }
      if (simulationModal && simulationModal.classList.contains("is-open")) {
        closeSimulationModal();
        return;
      }
      if (currentLevel === "children") renderHome();
      else hidePanel();
    }
    if (!imageIsOpen) return;
    if (event.key === "+" || event.key === "=") {
      event.preventDefault();
      setImageZoom(imageZoomState.scale + 0.35);
    }
    if (event.key === "-" || event.key === "_") {
      event.preventDefault();
      setImageZoom(imageZoomState.scale - 0.35);
    }
    if (event.key === "0") {
      event.preventDefault();
      resetImageZoom();
    }
  });

  window.addEventListener("resize", () => {
    scheduleViewportAdapt();
  });

  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", scheduleViewportAdapt);
  }

  document.addEventListener("visibilitychange", () => {
    if (!window.anime || !Array.isArray(window.anime.running)) return;
    window.anime.running.forEach((animation) => {
      if (document.hidden && typeof animation.pause === "function") animation.pause();
      if (!document.hidden && typeof animation.play === "function" && !prefersReduced) animation.play();
    });
  });

  adaptViewport({ render: false });
  bootMotion();
  renderHome();

  // Fallback: si no se detectan burbujas después del render inicial,
  // forzamos un re-render seguro una vez para evitar vistas vacías.
  window.setTimeout(() => {
    try {
      const found = scene.querySelectorAll('.bubble').length;
      if (!found) {
        console.warn('No bubbles found after initial render — forcing re-render');
        if (typeof logLayoutEvent === 'function') logLayoutEvent('fallback:renderHome', { found });
        clearScene(() => {
          renderHome();
          window.setTimeout(() => {
            const again = scene.querySelectorAll('.bubble').length;
            if (!again) {
              if (typeof logLayoutEvent === 'function') logLayoutEvent('fallback:failed', { again });
              console.error('Fallback re-render did not restore bubbles');
            } else {
              if (typeof logLayoutEvent === 'function') logLayoutEvent('fallback:success', { again });
            }
          }, 300);
        });
      }
    } catch (e) {
      // no-op
    }
  }, 350);
})();
