import { samplePortrait } from "./imageSampler.js";
import { generateGraph } from "./graphGenerator.js";
import { GraphRenderer } from "./graphRenderer.js";

const animeDriver = window.anime || {
  timeline: () => ({ seek: () => {}, add: () => ({}) }),
};

function setPortraitMask(stage, progress) {
  const boundary = 8 + progress * 112;
  stage.style.setProperty("--digital-progress", progress.toFixed(3));
  stage.style.setProperty("--portrait-progress", `${boundary.toFixed(2)}%`);
  stage.style.setProperty("--portrait-saturate", Math.max(0.42, 1 - progress * 0.52).toFixed(3));
  stage.style.setProperty("--portrait-contrast", (1 + progress * 0.1).toFixed(3));
  stage.style.setProperty("--frame-opacity", (0.18 + progress * 0.5).toFixed(3));
  const pulseOpacity = 0.18 + progress * 0.38;
  stage.parentElement?.style.setProperty("--pulse-opacity", pulseOpacity.toFixed(3));
  stage.parentElement?.style.setProperty("--pulse-opacity-soft", (pulseOpacity * 0.65).toFixed(3));
}

function fitImageToStage(image, stage) {
  const imageRatio = image.naturalWidth / image.naturalHeight;
  stage.style.aspectRatio = imageRatio > 0 ? `${image.naturalWidth} / ${image.naturalHeight}` : "0.83";
}

async function loadPortrait(image) {
  if (image.complete && image.naturalWidth > 0) return image;
  await new Promise((resolve, reject) => {
    image.addEventListener("load", resolve, { once: true });
    image.addEventListener("error", reject, { once: true });
  });
  return image;
}

function createTimeline(state) {
  return animeDriver.timeline({
    autoplay: true,
    loop: true,
    direction: "alternate",
    duration: 1000,
    easing: "easeInOutSine",
    update: () => {
      state.onUpdate?.(state.progress);
    },
  }).add({
    targets: state,
    progress: [0, 1],
    duration: 5200,
    easing: "easeInOutSine",
  });
}

function updateReadout(root, progress) {
  const label = root.querySelector("[data-progress-label]");
  if (label) label.textContent = `${Math.round(progress * 100)}%`;
}

async function boot(root) {
  const stage = root.querySelector(".portrait-stage");
  const image = root.querySelector(".portrait");
  const graphCanvas = root.querySelector(".graph");
  const analysisCanvas = root.querySelector(".analysis-canvas");
  const state = {
    progress: 0,
    onUpdate: (progress) => {
      setPortraitMask(stage, progress);
      updateReadout(root, progress);
    },
  };
  const renderer = new GraphRenderer(graphCanvas, stage);
  let running = true;

  try {
    await loadPortrait(image);
  } catch (error) {
    stage.classList.add("is-missing");
    setPortraitMask(stage, 0);
    renderer.resize();
    return;
  }

  stage.classList.remove("is-missing");
  fitImageToStage(image, stage);
  renderer.resize();

  const sample = samplePortrait(image, analysisCanvas, {
    sampleWidth: window.innerWidth < 760 ? 380 : 540,
  });
  renderer.setGraph(generateGraph(sample));
  createTimeline(state);

  const renderLoop = (time) => {
    if (!running) return;
    renderer.render(state.progress, time);
    requestAnimationFrame(renderLoop);
  };

  window.addEventListener("resize", () => {
    renderer.resize();
    setPortraitMask(stage, state.progress);
  });

  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) requestAnimationFrame(renderLoop);
  });

  requestAnimationFrame(renderLoop);
}

document.querySelectorAll("[data-digital-portrait]").forEach((root) => {
  boot(root);
});
