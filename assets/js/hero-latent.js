(function () {
  const canvas = document.querySelector("[data-latent-canvas]");
  if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const ctx = canvas.getContext("2d");
  const clusters = [
    { x: 0.22, y: 0.45, color: "98,216,239", spread: 145, density: 86 },
    { x: 0.42, y: 0.34, color: "98,216,239", spread: 116, density: 74 },
    { x: 0.64, y: 0.42, color: "156,119,216", spread: 138, density: 86 },
    { x: 0.54, y: 0.66, color: "238,247,251", spread: 92, density: 58 },
    { x: 0.78, y: 0.28, color: "98,216,239", spread: 102, density: 56 },
  ];
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
        + Math.sin(x * 0.008 + frame * 0.008) * 26
        + Math.sin(x * 0.021 + frame * 0.004) * 12;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = `rgba(${color}, ${alpha})`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  function drawDensityContour(cluster, alpha) {
    const cx = width * cluster.x + Math.sin(frame * 0.004 + cluster.x * 10) * 24;
    const cy = height * cluster.y + Math.cos(frame * 0.003 + cluster.y * 8) * 14;
    for (let ring = 0; ring < 4; ring += 1) {
      ctx.beginPath();
      const radiusX = cluster.spread * (0.55 + ring * 0.28);
      const radiusY = radiusX * (0.42 + ring * 0.035);
      for (let i = 0; i <= 128; i += 1) {
        const t = (i / 128) * Math.PI * 2;
        const wobble = Math.sin(t * 5 + frame * 0.01 + ring) * 5;
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
    const x = width * (0.08 + progress * 0.84);
    const y = height * 0.52
      + Math.sin(progress * Math.PI * 2.2) * 54
      + Math.sin(frame * 0.012) * 18;
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, 90);
    gradient.addColorStop(0, "rgba(98,216,239,0.24)");
    gradient.addColorStop(0.38, "rgba(156,119,216,0.1)");
    gradient.addColorStop(1, "rgba(98,216,239,0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, 90, 0, Math.PI * 2);
    ctx.fill();
  }

  function draw() {
    frame += 1;
    ctx.clearRect(0, 0, width, height);

    drawFieldLine(0.46, 0.22, "98,216,239");
    drawFieldLine(0.54, 0.16, "156,119,216");
    drawFieldLine(0.62, 0.11, "98,216,239");
    drawFieldLine(0.38, 0.1, "238,247,251");
    drawSignalPulse();

    clusters.forEach((cluster) => drawDensityContour(cluster, 0.18));

    particles.forEach((particle) => {
      const cluster = clusters[particle.clusterIndex];
      particle.angle += particle.speed;
      const clusterDriftX = Math.sin(frame * 0.004 + particle.clusterIndex) * 28;
      const clusterDriftY = Math.cos(frame * 0.003 + particle.clusterIndex * 1.7) * 14;
      const radiusPulse = 1 + Math.sin(frame * 0.008 + particle.phase) * 0.08;
      const x = width * cluster.x + Math.cos(particle.angle) * particle.radius * radiusPulse + clusterDriftX;
      const y = height * cluster.y + Math.sin(particle.angle * 1.7) * particle.radius * 0.56 * radiusPulse + clusterDriftY;
      ctx.beginPath();
      ctx.arc(x, y, particle.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${cluster.color}, ${0.2 + Math.sin(frame * 0.02 + particle.radius) * 0.15})`;
      ctx.fill();
    });

    window.requestAnimationFrame(draw);
  }

  resize();
  seed();
  window.addEventListener("resize", resize);
  draw();
})();
