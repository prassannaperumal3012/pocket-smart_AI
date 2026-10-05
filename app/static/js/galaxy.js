(() => {
    const canvas = document.getElementById("galaxy-background");
    if (!canvas) return;

    const gl = canvas.getContext("webgl", {
        alpha: true,
        antialias: false,
        premultipliedAlpha: false
    });
    if (!gl) return;

    const vertexShader = `
        attribute vec2 position;
        attribute vec2 uv;
        varying vec2 vUv;

        void main() {
            vUv = uv;
            gl_Position = vec4(position, 0.0, 1.0);
        }
    `;

    const fragmentShader = `
        precision highp float;

        uniform float uTime;
        uniform vec3 uResolution;
        uniform vec2 uFocal;
        uniform vec2 uRotation;
        uniform float uStarSpeed;
        uniform float uDensity;
        uniform float uHueShift;
        uniform float uSpeed;
        uniform vec2 uMouse;
        uniform float uGlowIntensity;
        uniform float uSaturation;
        uniform bool uMouseRepulsion;
        uniform float uTwinkleIntensity;
        uniform float uRotationSpeed;
        uniform float uRepulsionStrength;
        uniform float uMouseActiveFactor;
        varying vec2 vUv;

        #define NUM_LAYER 4.0
        #define STAR_COLOR_CUTOFF 0.2
        #define MAT45 mat2(0.7071, -0.7071, 0.7071, 0.7071)
        #define PERIOD 3.0

        float Hash21(vec2 p) {
            p = fract(p * vec2(123.34, 456.21));
            p += dot(p, p + 45.32);
            return fract(p.x * p.y);
        }

        float tri(float x) {
            return abs(fract(x) * 2.0 - 1.0);
        }

        float tris(float x) {
            float t = fract(x);
            return 1.0 - smoothstep(0.0, 1.0, abs(2.0 * t - 1.0));
        }

        float trisn(float x) {
            float t = fract(x);
            return 2.0 * (1.0 - smoothstep(0.0, 1.0, abs(2.0 * t - 1.0))) - 1.0;
        }

        vec3 hsv2rgb(vec3 c) {
            vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
            vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
            return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
        }

        float Star(vec2 uv, float flare) {
            float d = length(uv);
            float m = (0.05 * uGlowIntensity) / max(d, 0.0001);
            float rays = smoothstep(0.0, 1.0, 1.0 - abs(uv.x * uv.y * 1000.0));
            m += rays * flare * uGlowIntensity;
            uv *= MAT45;
            rays = smoothstep(0.0, 1.0, 1.0 - abs(uv.x * uv.y * 1000.0));
            m += rays * 0.3 * flare * uGlowIntensity;
            return m * smoothstep(1.0, 0.2, d);
        }

        vec3 StarLayer(vec2 uv) {
            vec3 col = vec3(0.0);
            vec2 gv = fract(uv) - 0.5;
            vec2 id = floor(uv);

            for (int y = -1; y <= 1; y++) {
                for (int x = -1; x <= 1; x++) {
                    vec2 offset = vec2(float(x), float(y));
                    vec2 si = id + offset;
                    float seed = Hash21(si);
                    float size = fract(seed * 345.32);
                    float glossLocal = tri(uStarSpeed / (PERIOD * seed + 1.0));
                    float flareSize = smoothstep(0.9, 1.0, size) * glossLocal;

                    float red = smoothstep(STAR_COLOR_CUTOFF, 1.0, Hash21(si + 1.0)) + STAR_COLOR_CUTOFF;
                    float blu = smoothstep(STAR_COLOR_CUTOFF, 1.0, Hash21(si + 3.0)) + STAR_COLOR_CUTOFF;
                    float grn = min(red, blu) * seed;
                    vec3 base = vec3(red, grn, blu);

                    float hue = atan(base.g - base.r, base.b - base.r) / (2.0 * 3.14159) + 0.5;
                    hue = fract(hue + uHueShift / 360.0);
                    float gray = dot(base, vec3(0.299, 0.587, 0.114));
                    float sat = length(base - vec3(gray)) * uSaturation;
                    float val = max(max(base.r, base.g), base.b);
                    base = hsv2rgb(vec3(hue, sat, val));

                    vec2 pad = vec2(
                        tris(seed * 34.0 + uTime * uSpeed / 10.0),
                        tris(seed * 38.0 + uTime * uSpeed / 30.0)
                    ) - 0.5;

                    float star = Star(gv - offset - pad, flareSize);
                    float twinkle = trisn(uTime * uSpeed + seed * 6.2831) * 0.5 + 1.0;
                    twinkle = mix(1.0, twinkle, uTwinkleIntensity);
                    col += star * size * twinkle * base;
                }
            }
            return col;
        }

        void main() {
            vec2 focalPx = uFocal * uResolution.xy;
            vec2 uv = (vUv * uResolution.xy - focalPx) / uResolution.y;
            vec2 mousePosUV = (uMouse * uResolution.xy - focalPx) / uResolution.y;
            float mouseDistance = length(uv - mousePosUV);

            if (uMouseRepulsion) {
                vec2 away = uv - mousePosUV;
                float influence = exp(-mouseDistance * 5.0);
                vec2 repulsion = normalize(away + vec2(0.00001)) * influence;
                uv += repulsion * 0.18 * uRepulsionStrength * uMouseActiveFactor;
            }

            float autoRotAngle = uTime * uRotationSpeed;
            mat2 autoRot = mat2(cos(autoRotAngle), -sin(autoRotAngle), sin(autoRotAngle), cos(autoRotAngle));
            uv = autoRot * uv;
            uv = mat2(uRotation.x, -uRotation.y, uRotation.y, uRotation.x) * uv;

            vec3 col = vec3(0.0);
            for (float i = 0.0; i < 1.0; i += 1.0 / NUM_LAYER) {
                float depth = fract(i + uStarSpeed * uSpeed);
                float scale = mix(20.0 * uDensity, 0.5 * uDensity, depth);
                float fade = depth * smoothstep(1.0, 0.9, depth);
                col += StarLayer(uv * scale + i * 453.32) * fade;
            }

            float repelGap = smoothstep(0.025, 0.15, mouseDistance);
            col *= mix(1.0, 0.2 + 0.8 * repelGap, uMouseActiveFactor);
            float alpha = min(smoothstep(0.0, 0.3, length(col)), 1.0);
            gl_FragColor = vec4(col, alpha);
        }
    `;

    function compileShader(type, source) {
        const shader = gl.createShader(type);
        if (!shader) return null;
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            gl.deleteShader(shader);
            return null;
        }
        return shader;
    }

    const vertex = compileShader(gl.VERTEX_SHADER, vertexShader);
    const fragment = compileShader(gl.FRAGMENT_SHADER, fragmentShader);
    if (!vertex || !fragment) return;

    const program = gl.createProgram();
    if (!program) return;
    gl.attachShader(program, vertex);
    gl.attachShader(program, fragment);
    gl.linkProgram(program);
    gl.deleteShader(vertex);
    gl.deleteShader(fragment);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return;

    const vertices = new Float32Array([
        -1, -1, 0, 0,
         1, -1, 1, 0,
        -1,  1, 0, 1,
        -1,  1, 0, 1,
         1, -1, 1, 0,
         1,  1, 1, 1
    ]);
    const buffer = gl.createBuffer();
    if (!buffer) return;
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    gl.useProgram(program);

    const position = gl.getAttribLocation(program, "position");
    const uv = gl.getAttribLocation(program, "uv");
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(uv);
    gl.vertexAttribPointer(uv, 2, gl.FLOAT, false, 16, 8);

    const uniform = (name) => gl.getUniformLocation(program, name);
    const uniforms = {
        time: uniform("uTime"),
        resolution: uniform("uResolution"),
        focal: uniform("uFocal"),
        rotation: uniform("uRotation"),
        starSpeed: uniform("uStarSpeed"),
        density: uniform("uDensity"),
        hueShift: uniform("uHueShift"),
        speed: uniform("uSpeed"),
        mouse: uniform("uMouse"),
        glow: uniform("uGlowIntensity"),
        saturation: uniform("uSaturation"),
        mouseRepulsion: uniform("uMouseRepulsion"),
        twinkle: uniform("uTwinkleIntensity"),
        rotationSpeed: uniform("uRotationSpeed"),
        repulsionStrength: uniform("uRepulsionStrength"),
        mouseActive: uniform("uMouseActiveFactor")
    };

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    gl.clearColor(0, 0, 0, 0);

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const targetMouse = { x: 0.5, y: 0.5, active: 0 };
    const smoothMouse = { x: 0.5, y: 0.5, active: 0 };
    let animationFrame = 0;
    let elapsedTime = 0;
    let previousTimestamp = null;

    function resize() {
        const scale = Math.min(
            window.devicePixelRatio || 1,
            1.25,
            2000 / Math.max(window.innerWidth, 1),
            1400 / Math.max(window.innerHeight, 1)
        );
        canvas.width = Math.max(1, Math.round(window.innerWidth * scale));
        canvas.height = Math.max(1, Math.round(window.innerHeight * scale));
        gl.viewport(0, 0, canvas.width, canvas.height);
        gl.useProgram(program);
        gl.uniform3f(uniforms.resolution, canvas.width, canvas.height, canvas.width / canvas.height);
    }

    function render(timestamp) {
        animationFrame = 0;
        if (document.hidden) {
            previousTimestamp = null;
            return;
        }

        const frameDelta = previousTimestamp === null
            ? 0
            : Math.min(Math.max((timestamp - previousTimestamp) * 0.001, 0), 0.05);
        previousTimestamp = timestamp;
        elapsedTime += frameDelta * (reducedMotion.matches ? 0.35 : 1);

        const frameScale = frameDelta > 0 ? frameDelta / (1 / 60) : 0;
        const blend = 1 - Math.pow(1 - 0.17, frameScale);
        smoothMouse.x += (targetMouse.x - smoothMouse.x) * blend;
        smoothMouse.y += (targetMouse.y - smoothMouse.y) * blend;
        smoothMouse.active += (targetMouse.active - smoothMouse.active) * blend;

        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.uniform1f(uniforms.time, elapsedTime);
        gl.uniform2f(uniforms.focal, 0.5, 0.5);
        gl.uniform2f(uniforms.rotation, 1, 0);
        gl.uniform1f(uniforms.starSpeed, (elapsedTime * 0.5) / 10);
        gl.uniform1f(uniforms.density, 1.1);
        gl.uniform1f(uniforms.hueShift, 228);
        gl.uniform1f(uniforms.speed, 1);
        gl.uniform2f(uniforms.mouse, smoothMouse.x, smoothMouse.y);
        gl.uniform1f(uniforms.glow, 0.38);
        gl.uniform1f(uniforms.saturation, 0.72);
        gl.uniform1i(uniforms.mouseRepulsion, 1);
        gl.uniform1f(uniforms.twinkle, 0.32);
        gl.uniform1f(uniforms.rotationSpeed, 0.1);
        gl.uniform1f(uniforms.repulsionStrength, 3.0);
        gl.uniform1f(uniforms.mouseActive, smoothMouse.active);
        gl.drawArrays(gl.TRIANGLES, 0, 6);

        animationFrame = window.requestAnimationFrame(render);
    }

    function handlePointerMove(event) {
        targetMouse.x = event.clientX / Math.max(window.innerWidth, 1);
        targetMouse.y = 1 - event.clientY / Math.max(window.innerHeight, 1);
        targetMouse.active = 1;
    }

    function handlePointerLeave() {
        targetMouse.active = 0;
    }

    function handleVisibilityChange() {
        if (document.hidden) {
            if (animationFrame) window.cancelAnimationFrame(animationFrame);
            animationFrame = 0;
            previousTimestamp = null;
        } else if (!animationFrame) {
            animationFrame = window.requestAnimationFrame(render);
        }
    }

    window.addEventListener("resize", resize, { passive: true });
    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("pointerleave", handlePointerLeave, { passive: true });
    document.addEventListener("visibilitychange", handleVisibilityChange);
    resize();

    animationFrame = window.requestAnimationFrame(render);
})();
