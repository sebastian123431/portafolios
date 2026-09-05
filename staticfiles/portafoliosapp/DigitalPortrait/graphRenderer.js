function cssColor(name, fallback) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

export class GraphRenderer {
  constructor(canvas, stage) {
    this.canvas = canvas;
    this.stage = stage;
    this.ctx = canvas.getContext("2d");
    this.width = 0;
    this.height = 0;
    this.pixelRatio = 1;
    this.graph = { nodes: [], connections: [] };
    this.colors = {
      accent: "#00d9ff",
      graph: "#dce8e6",
    };
  }

  setGraph(graph) {
    this.graph = graph || { nodes: [], connections: [] };
  }

  resize() {
    const rect = this.stage.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    this.width = Math.max(1, Math.round(rect.width));
    this.height = Math.max(1, Math.round(rect.height));
    this.pixelRatio = ratio;
    this.canvas.width = Math.round(this.width * ratio);
    this.canvas.height = Math.round(this.height * ratio);
    this.canvas.style.width = `${this.width}px`;
    this.canvas.style.height = `${this.height}px`;
    this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    this.refreshColors();
  }

  refreshColors() {
    this.colors.accent = cssColor("--accent-color", "#00d9ff");
    this.colors.graph = cssColor("--graph-color", "#dce8e6");
  }

  render(progress, time = 0) {
    const ctx = this.ctx;
    const { nodes, connections } = this.graph;
    const accent = this.colors.accent;
    const graphColor = this.colors.graph;
    const width = this.width;
    const height = this.height;
    const revealWindow = 0.22;

    ctx.clearRect(0, 0, width, height);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    this.drawSurfaceGlow(progress, time, accent);

    connections.forEach((connection) => {
      const visibility = Math.max(0, Math.min(1, (progress - connection.reveal + revealWindow) / revealWindow));
      if (visibility <= 0) return;

      const from = nodes[connection.from];
      const to = nodes[connection.to];
      if (!from || !to) return;

      const fromPos = this.nodePosition(from, progress, time);
      const toPos = this.nodePosition(to, progress, time);
      const capBoost = from.type === "cap" || to.type === "cap" ? 1.18 : 1;
      const faceBoost = from.region === "face" && to.region === "face" ? 1.18 : 1;
      const clothingSurface = from.type === "clothing-surface" || to.type === "clothing-surface";
      const featureBoost = from.type === "feature" || to.type === "feature" || from.type === "silhouette" || to.type === "silhouette" ? 1.32 : clothingSurface ? 0.46 : 0.78;
      const alpha = visibility * (0.1 + connection.strength * 0.46) * featureBoost * capBoost * faceBoost;

      ctx.strokeStyle = `rgba(220, 232, 230, ${alpha})`;
      ctx.lineWidth = 0.42 + connection.strength * (featureBoost > 1 || capBoost > 1 || faceBoost > 1 ? 1.05 : 0.62);
      ctx.beginPath();
      ctx.moveTo(fromPos.x, fromPos.y);
      ctx.lineTo(toPos.x, toPos.y);
      ctx.stroke();
    });

    this.drawTriangles(progress, time, graphColor);

    nodes.forEach((node) => {
      const visibility = Math.max(0, Math.min(1, (progress - node.reveal + revealWindow) / revealWindow));
      if (visibility <= 0) return;

      const pos = this.nodePosition(node, progress, time);
      const techBlend = Math.max(0, Math.min(1, (progress - 0.35) / 0.65));
      const alpha = visibility * node.opacity;
      const radius = node.radius * (0.72 + visibility * 0.48);

      ctx.fillStyle = techBlend > 0.55 ? accent : node.color;
      ctx.globalAlpha = node.type === "clothing-surface" ? alpha * 0.46 : node.type === "surface" ? alpha * 0.72 : alpha;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
      ctx.fill();

      if ((node.edge > 0.24 || node.contrast > 0.1 || node.type === "silhouette" || node.type === "cap" || node.region === "face" && node.type === "feature") && progress > 0.52) {
        ctx.globalAlpha = alpha * (node.type === "clothing-surface" ? 0.06 : node.type === "surface" ? 0.12 : node.type === "cap" ? 0.28 : node.region === "face" ? 0.42 : 0.36);
        ctx.strokeStyle = accent;
        ctx.lineWidth = 0.75;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius + 2.2, 0, Math.PI * 2);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    });
  }

  drawSurfaceGlow(progress, time, accent) {
    if (progress < 0.42) return;

    const ctx = this.ctx;
    const nodes = this.graph.nodes;
    const glowProgress = Math.max(0, Math.min(1, (progress - 0.42) / 0.58));
    const step = progress > 0.84 ? 11 : 18;

    for (let index = 0; index < nodes.length; index += step) {
      const node = nodes[index];
      if (!node || node.type !== "surface" && node.type !== "dark" && node.type !== "cap") continue;
      if (node.ny < 0.56 && node.type !== "cap") continue;
      const visibility = Math.max(0, Math.min(1, (progress - node.reveal + 0.28) / 0.28));
      if (visibility <= 0) continue;

      const pos = this.nodePosition(node, progress, time);
      const clothingBoost = node.ny > 0.66 ? 1.35 : 1;
      const radius = (5 + node.density * 12) * clothingBoost;
      const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, radius);
      gradient.addColorStop(0, `rgba(0, 217, 255, ${0.065 * visibility * glowProgress * clothingBoost})`);
      gradient.addColorStop(1, "rgba(0, 217, 255, 0)");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  drawTriangles(progress, time, graphColor) {
    if (progress < 0.58) return;

    const ctx = this.ctx;
    const nodes = this.graph.nodes;
    const step = progress > 0.82 ? 24 : 42;
    ctx.strokeStyle = graphColor;
    ctx.lineWidth = 0.45;

    for (let index = 0; index < nodes.length - step * 2; index += step) {
      const a = nodes[index];
      const b = nodes[index + step];
      const c = nodes[index + step * 2];
      if (!a || !b || !c) continue;
      const reveal = Math.max(a.reveal, b.reveal, c.reveal) + 0.12;
      const visibility = Math.max(0, Math.min(1, (progress - reveal + 0.18) / 0.18));
      if (visibility <= 0) continue;

      const pa = this.nodePosition(a, progress, time);
      const pb = this.nodePosition(b, progress, time);
      const pc = this.nodePosition(c, progress, time);
      if (Math.hypot(pa.x - pb.x, pa.y - pb.y) > 86 || Math.hypot(pb.x - pc.x, pb.y - pc.y) > 86) continue;

      ctx.globalAlpha = visibility * 0.08;
      ctx.beginPath();
      ctx.moveTo(pa.x, pa.y);
      ctx.lineTo(pb.x, pb.y);
      ctx.lineTo(pc.x, pc.y);
      ctx.closePath();
      ctx.fillStyle = graphColor;
      ctx.fill();
      ctx.globalAlpha = visibility * 0.16;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }

  nodePosition(node, progress, time) {
    const digitalAmount = Math.max(0, Math.min(1, (progress - node.reveal + 0.18) / 0.3));
    const breathe = Math.sin(time * 0.001 * node.speed + node.phase) * 1.4 * digitalAmount;
    return {
      x: node.nx * this.width + node.driftX * digitalAmount + breathe,
      y: node.ny * this.height + node.driftY * digitalAmount - breathe * 0.7,
    };
  }
}
