(function () {
    "use strict";

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );

    const canvas = document.createElement("canvas");
    canvas.className = "glow-cursor__canvas";
    canvas.setAttribute("aria-hidden", "true");
    document.body.appendChild(canvas);

    const context = canvas.getContext("2d", { alpha: true });
    if (!context) {
        canvas.remove();
        return;
    }

    const settings = {
        color: [103, 232, 249],
        secondaryColor: [167, 139, 250],
        trailLength: reducedMotion.matches ? 16 : 40,
        trailWidth: 8,
        followSpeed: reducedMotion.matches ? 0.5 : 0.16,
        glowSpread: 1.2,
        idleTimeout: reducedMotion.matches ? 350 : 700,
        fadeDuration: reducedMotion.matches ? 350 : 900,
        pulseSpeed: reducedMotion.matches ? 0 : 1.1,
        maxDevicePixelRatio: 1.5
    };

    const points = Array.from(
        { length: settings.trailLength },
        () => ({ x: 0, y: 0 })
    );
    const target = { x: 0, y: 0 };
    const head = { x: 0, y: 0 };

    let width = 1;
    let height = 1;
    let pixelRatio = 1;
    let initialized = false;
    let pointerInside = false;
    let fade = 0;
    let lastInputTime = 0;
    let lastFrameTime = 0;
    let animationFrame = 0;

    function resizeCanvas() {
        pixelRatio = Math.min(
            window.devicePixelRatio || 1,
            settings.maxDevicePixelRatio
        );
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = Math.round(width * pixelRatio);
        canvas.height = Math.round(height * pixelRatio);
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    }

    function colorAt(progress, alpha) {
        const mix = Math.min(Math.max(progress, 0), 1);
        const red = Math.round(
            settings.color[0] +
                (settings.secondaryColor[0] - settings.color[0]) * mix
        );
        const green = Math.round(
            settings.color[1] +
                (settings.secondaryColor[1] - settings.color[1]) * mix
        );
        const blue = Math.round(
            settings.color[2] +
                (settings.secondaryColor[2] - settings.color[2]) * mix
        );

        return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
    }

    function initializeTrail(x, y) {
        target.x = x;
        target.y = y;
        head.x = x;
        head.y = y;

        points.forEach((point) => {
            point.x = x;
            point.y = y;
        });

        initialized = true;
    }

    function updatePointer(event) {
        if (!initialized) {
            initializeTrail(event.clientX, event.clientY);
        }

        target.x = event.clientX;
        target.y = event.clientY;
        pointerInside = true;
        lastInputTime = performance.now();

        if (!animationFrame) {
            animationFrame = requestAnimationFrame(render);
        }
    }

    function drawTrail(time) {
        context.clearRect(0, 0, width, height);
        if (!initialized || fade <= 0.001) return;

        const denominator = Math.max(points.length - 1, 1);

        for (let index = 0; index < points.length - 1; index += 1) {
            const start = points[index];
            const end = points[index + 1];
            const progress = index / denominator;
            const life = Math.pow(1 - progress, 1.05);
            const widthAtPoint =
                settings.trailWidth * (1 - 0.75 * Math.pow(progress, 1.15));
            const pulse =
                1 +
                Math.sin(time * settings.pulseSpeed - progress * 11) * 0.12;

            context.beginPath();
            context.moveTo(start.x, start.y);
            context.lineTo(end.x, end.y);
            context.lineCap = "round";
            context.lineJoin = "round";
            context.strokeStyle = colorAt(progress, 0.35);
            context.lineWidth = Math.max(
                widthAtPoint * (1.3 + settings.glowSpread * 0.65),
                1
            );
            context.shadowColor = colorAt(progress, 0.9);
            context.shadowBlur = widthAtPoint * (1.3 + settings.glowSpread);
            context.globalAlpha = fade * life * pulse;
            context.stroke();

            context.shadowBlur = widthAtPoint * 0.45;
            context.strokeStyle = colorAt(progress, 0.92);
            context.lineWidth = Math.max(widthAtPoint * 0.48, 1);
            context.globalAlpha = fade * life * pulse;
            context.stroke();
        }

        context.globalAlpha = 1;
        context.shadowBlur = 0;

        const hotspot = context.createRadialGradient(
            head.x,
            head.y,
            0,
            head.x,
            head.y,
            settings.trailWidth * 5
        );
        hotspot.addColorStop(0, `rgba(255, 255, 255, ${fade * 0.7})`);
        hotspot.addColorStop(0.2, `rgba(103, 232, 249, ${fade * 0.45})`);
        hotspot.addColorStop(1, "rgba(103, 232, 249, 0)");
        context.fillStyle = hotspot;
        context.beginPath();
        context.arc(
            head.x,
            head.y,
            settings.trailWidth * 5,
            0,
            Math.PI * 2
        );
        context.fill();
    }

    function render(now) {
        animationFrame = 0;
        const delta = lastFrameTime
            ? Math.min((now - lastFrameTime) / 16.667, 3)
            : 1;
        lastFrameTime = now;

        if (initialized) {
            const headEase =
                1 - Math.pow(1 - settings.followSpeed, delta);
            const chainEase =
                1 - Math.pow(1 - (0.28 + settings.followSpeed * 0.35), delta);

            head.x += (target.x - head.x) * headEase;
            head.y += (target.y - head.y) * headEase;
            points[0].x = head.x;
            points[0].y = head.y;

            for (let index = 1; index < points.length; index += 1) {
                points[index].x +=
                    (points[index - 1].x - points[index].x) * chainEase;
                points[index].y +=
                    (points[index - 1].y - points[index].y) * chainEase;
            }
        }

        const idleFor = now - lastInputTime;
        const shouldFade = !pointerInside || idleFor > settings.idleTimeout;
        const fadeTarget = initialized && !shouldFade ? 1 : 0;
        const fadeStep = Math.min(
            1,
            ((16.667 * delta) / settings.fadeDuration) * 7
        );
        fade += (fadeTarget - fade) * fadeStep;

        drawTrail(now * 0.001);

        const waitingForIdle =
            pointerInside && idleFor <= settings.idleTimeout;
        const trailVisible = fade > 0.002;

        if (waitingForIdle || trailVisible) {
            animationFrame = requestAnimationFrame(render);
        } else {
            context.clearRect(0, 0, width, height);
            lastFrameTime = 0;
        }
    }

    function leaveViewport() {
        pointerInside = false;

        if (!animationFrame && fade > 0.002) {
            animationFrame = requestAnimationFrame(render);
        }
    }

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas, { passive: true });
    window.addEventListener("pointermove", updatePointer, { passive: true });
    window.addEventListener("blur", leaveViewport);
    document.documentElement.addEventListener("pointerleave", leaveViewport);
})();
