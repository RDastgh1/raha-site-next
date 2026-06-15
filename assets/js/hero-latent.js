(function () {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const rotator = document.querySelector("[data-title-rotator]");

  function setupTitleRotator() {
    if (!rotator) return;

    const phrases = Array.from(rotator.querySelectorAll("span"))
      .map((span) => span.textContent.trim())
      .filter(Boolean);

    if (!phrases.length) return;

    if (reduceMotion) {
      rotator.classList.add("is-static");
      return;
    }

    rotator.textContent = "";
    const target = document.createElement("span");
    target.className = "raha-title-typing";
    target.setAttribute("aria-live", "polite");
    rotator.appendChild(target);

    let phraseIndex = 0;
    let characterIndex = 0;
    let deleting = false;

    function tick() {
      const phrase = phrases[phraseIndex];
      target.textContent = phrase.slice(0, characterIndex);

      if (!deleting && characterIndex < phrase.length) {
        characterIndex += 1;
        window.setTimeout(tick, 72);
        return;
      }

      if (!deleting) {
        deleting = true;
        window.setTimeout(tick, 1400);
        return;
      }

      if (characterIndex > 0) {
        characterIndex -= 1;
        window.setTimeout(tick, 42);
        return;
      }

      deleting = false;
      phraseIndex = (phraseIndex + 1) % phrases.length;
      window.setTimeout(tick, 260);
    }

    window.setTimeout(tick, 260);
  }

  setupTitleRotator();

  if (window.location.pathname.endsWith("/") && !window.location.hash) {
    window.history.scrollRestoration = "manual";
    window.addEventListener("load", () => {
      window.setTimeout(() => window.scrollTo(0, 0), 0);
    }, { once: true });
  }

  const canvas = document.querySelector("[data-latent-canvas]");
  if (!canvas || reduceMotion) return;

  const ctx = canvas.getContext("2d");
  const baseClusters = [
    { x: 0.04, y: 0.14, color: "98,216,239", spread: 260, density: 40 },
    { x: 0.18, y: 0.30, color: "98,216,239", spread: 320, density: 54 },
    { x: 0.42, y: 0.22, color: "156,119,216", spread: 340, density: 60 },
    { x: 0.60, y: 0.46, color: "98,216,239", spread: 360, density: 64 },
    { x: 0.78, y: 0.22, color: "156,119,216", spread: 320, density: 44 },
    { x: 0.94, y: 0.42, color: "98,216,239", spread: 300, density: 38 },
    { x: 0.74, y: 0.82, color: "238,247,251", spread: 260, density: 36 },
    { x: 0.92, y: 0.76, color: "98,216,239", spread: 240, density: 34 },
  ];
  const clusters = [];
  baseClusters.forEach((cluster, index) => {
    clusters.push(cluster);
    clusters.push({
      x: 1 - cluster.x,
      y: cluster.y,
      color: index % 2 === 0 ? "98,216,239" : "156,119,216",
      spread: cluster.spread * 0.88,
      density: Math.max(18, Math.round(cluster.density * 0.6)),
    });
  });
  const particles = [];
  let width = 0;
  let height = 0;
  let frame = 0;

  function resize() {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = canvas.offsetWidth;
    height = canvas.offsetHeight;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  function seed() {
    particles.length = 0;
    clusters.forEach((cluster, clusterIndex) => {
      for (let i = 0; i < cluster.density; i += 1) {
        particles.push({
          clusterIndex,
          angle: Math.random() * Math.PI * 2,
          radius: Math.pow(Math.random(), 1.65) * cluster.spread,
          speed: 0.0007 + Math.random() * 0.0023,
          size: 0.55 + Math.random() * 1.8,
          phase: Math.random() * Math.PI * 2,
        });
      }
    });
  }

  function drawFieldLine(yOffset, alpha, color) {
    ctx.beginPath();
    for (let x = 0; x <= width; x += 24) {
      const y = height * yOffset
        + Math.sin(x * 0.0065 + frame * 0.006) * 42
        + Math.sin(x * 0.015 + frame * 0.0035) * 18;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = `rgba(${color}, ${alpha})`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  function drawDensityContour(cluster, alpha) {
    const cx = width * cluster.x + Math.sin(frame * 0.004 + cluster.x * 10) * (width * 0.035);
    const cy = height * cluster.y + Math.cos(frame * 0.003 + cluster.y * 8) * (height * 0.018);
    for (let ring = 0; ring < 4; ring += 1) {
      ctx.beginPath();
      const radiusX = cluster.spread * (0.46 + ring * 0.3);
      const radiusY = radiusX * (0.42 + ring * 0.035);
      for (let i = 0; i <= 128; i += 1) {
        const t = (i / 128) * Math.PI * 2;
        const wobble = Math.sin(t * 5 + frame * 0.01 + ring) * 8;
        const x = cx + Math.cos(t) * (radiusX + wobble);
        const y = cy + Math.sin(t) * (radiusY + wobble * 0.55);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = `rgba(${cluster.color}, ${alpha / (ring + 1.4)})`;
      ctx.lineWidth = 0.85;
      ctx.stroke();
    }
  }

  function drawSignalPulse() {
    const progress = (frame % 520) / 520;
    const x = width * (0.0 + progress * 1.0);
    const y = height * 0.52
      + Math.sin(progress * Math.PI * 2.2) * 72
      + Math.sin(frame * 0.012) * 26;
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, 90);
    gradient.addColorStop(0, "rgba(98,216,239,0.12)");
    gradient.addColorStop(0.38, "rgba(156,119,216,0.06)");
    gradient.addColorStop(1, "rgba(98,216,239,0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, 90, 0, Math.PI * 2);
    ctx.fill();
  }

  function draw() {
    frame += 1;
    ctx.clearRect(0, 0, width, height);

    drawFieldLine(0.08, 0.05, "238,247,251");
    drawFieldLine(0.18, 0.07, "98,216,239");
    drawFieldLine(0.30, 0.08, "156,119,216");
    drawFieldLine(0.44, 0.11, "98,216,239");
    drawFieldLine(0.58, 0.10, "156,119,216");
    drawFieldLine(0.72, 0.08, "98,216,239");
    drawFieldLine(0.86, 0.05, "238,247,251");
    drawSignalPulse();

    clusters.forEach((cluster) => drawDensityContour(cluster, 0.075));

    particles.forEach((particle) => {
      const cluster = clusters[particle.clusterIndex];
      particle.angle += particle.speed;
      const clusterDriftX = Math.sin(frame * 0.004 + particle.clusterIndex) * (width * 0.085);
      const clusterDriftY = Math.cos(frame * 0.003 + particle.clusterIndex * 1.7) * (height * 0.04);
      const radiusPulse = 1 + Math.sin(frame * 0.008 + particle.phase) * 0.14;
      const x = width * cluster.x + Math.cos(particle.angle) * particle.radius * radiusPulse + clusterDriftX;
      const y = height * cluster.y + Math.sin(particle.angle * 1.7) * particle.radius * 0.56 * radiusPulse + clusterDriftY;
      ctx.beginPath();
      ctx.arc(x, y, particle.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${cluster.color}, ${0.055 + Math.sin(frame * 0.02 + particle.radius) * 0.04})`;
      ctx.fill();
    });

    window.requestAnimationFrame(draw);
  }

  resize();
  seed();
  window.addEventListener("resize", resize);
  draw();
})();
