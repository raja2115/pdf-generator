// ═══════════════════════════════════════════
//   REPORT AI — script.js
// ═══════════════════════════════════════════

// ── Particle Canvas ──────────────────────────
(function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H, particles = [];

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    function Particle() {
        this.x = Math.random() * W;
        this.y = Math.random() * H;
        this.r = Math.random() * 1.5 + 0.4;
        this.vx = (Math.random() - 0.5) * 0.4;
        this.vy = (Math.random() - 0.5) * 0.4;
        this.alpha = Math.random() * 0.5 + 0.1;
        const colors = ['#3b82f6','#8b5cf6','#ec4899','#06b6d4','#10b981'];
        this.color = colors[Math.floor(Math.random() * colors.length)];
    }

    function initParticleList(n) {
        particles = [];
        for (let i = 0; i < n; i++) particles.push(new Particle());
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);
        particles.forEach(p => {
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
            if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.alpha;
            ctx.fill();
        });
        // Draw connections
        ctx.globalAlpha = 1;
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(139,92,246,${0.12 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(draw);
    }

    resize();
    initParticleList(90);
    draw();
    window.addEventListener('resize', () => { resize(); initParticleList(90); });
})();

// ── Main App ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

    // Elements
    const formState    = document.getElementById('formState');
    const loadingState = document.getElementById('loadingState');
    const resultState  = document.getElementById('resultState');
    const errorState   = document.getElementById('errorState');
    const form         = document.getElementById('reportForm');
    const progressBar  = document.getElementById('progressBar');
    const loadingMsg   = document.getElementById('loadingMessage');
    const loadingPct   = document.getElementById('loadingPercentage');
    const downloadBtn  = document.getElementById('downloadBtn');
    const viewBtn      = document.getElementById('viewBtn');
    const backBtn      = document.getElementById('backBtn');
    const retryBtn     = document.getElementById('retryBtn');
    const topicInput   = document.getElementById('projectTopic');

    let progressInterval;

    // ── Suggestion chips
    document.querySelectorAll('.sug-chip').forEach(btn => {
        btn.addEventListener('click', () => {
            topicInput.value = btn.dataset.topic;
            topicInput.focus();
        });
    });

    // ── Loading stages
    const stages = [
        { pct: 15,  step: 1, msg: 'Analyzing project requirements...' },
        { pct: 30,  step: 2, msg: 'Generating engineering content...' },
        { pct: 50,  step: 2, msg: 'Writing 17 technical sections...' },
        { pct: 65,  step: 3, msg: 'Fetching hardware images from Pexels...' },
        { pct: 80,  step: 3, msg: 'Downloading component photos...' },
        { pct: 90,  step: 4, msg: 'Compiling PDF document...' },
        { pct: 95,  step: 4, msg: 'Applying professional formatting...' }
    ];

    function activateStep(n) {
        for (let i = 1; i <= 4; i++) {
            const el = document.getElementById('step' + i);
            if (!el) continue;
            el.classList.remove('active', 'done');
            const badge = el.querySelector('.step-badge');
            if (i < n) {
                el.classList.add('done');
                badge.innerHTML = '<i class="fa-solid fa-check"></i>';
                badge.classList.remove('pending');
            } else if (i === n) {
                el.classList.add('active');
                badge.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
                badge.classList.remove('pending');
            } else {
                badge.innerHTML = '<i class="fa-regular fa-circle"></i>';
                badge.classList.add('pending');
            }
        }
    }

    function startProgress() {
        let idx = 0;
        progressBar.style.width = '0%';
        loadingPct.textContent = '0%';
        loadingMsg.textContent = 'Initializing AI engine...';
        activateStep(1);

        progressInterval = setInterval(() => {
            if (idx < stages.length) {
                const s = stages[idx++];
                progressBar.style.width = s.pct + '%';
                loadingPct.textContent = s.pct + '%';
                loadingMsg.textContent = s.msg;
                activateStep(s.step);
            }
        }, 2200);
    }

    function stopProgress(ok) {
        clearInterval(progressInterval);
        if (ok) {
            progressBar.style.width = '100%';
            loadingPct.textContent = '100%';
            loadingMsg.textContent = 'Done!';
            activateStep(5); // marks all as done
        }
    }

    function show(el) {
        [formState, loadingState, resultState, errorState].forEach(e => e && e.classList.add('hidden'));
        el && el.classList.remove('hidden');
    }

    // ── Form submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const topic        = topicInput.value.trim();
        const requirements = document.getElementById('requirements').value.trim();
        if (!topic) return;

        show(loadingState);
        startProgress();

        try {
            const res  = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, requirements })
            });
            const data = await res.json();
            stopProgress(res.ok);

            if (res.ok) {
                setTimeout(() => {
                    downloadBtn.href = data.pdf_url;
                    downloadBtn.setAttribute('download', data.pdf_url.split('/').pop() || 'Report.pdf');
                    viewBtn.href = data.view_url;
                    show(resultState);
                    launchConfetti();
                }, 600);
            } else {
                throw new Error(data.error || 'Generation failed. Please try again.');
            }
        } catch (err) {
            stopProgress(false);
            document.getElementById('errorText').textContent = err.message;
            show(errorState);
        }
    });

    backBtn && backBtn.addEventListener('click', () => {
        show(formState);
        topicInput.value = '';
        document.getElementById('requirements').value = '';
    });

    retryBtn && retryBtn.addEventListener('click', () => show(formState));

    // ── Confetti burst
    function launchConfetti() {
        const colors = ['#3b82f6','#8b5cf6','#ec4899','#10b981','#f59e0b','#06b6d4'];
        for (let i = 0; i < 120; i++) {
            const dot = document.createElement('div');
            Object.assign(dot.style, {
                position: 'fixed',
                width: Math.random() * 8 + 4 + 'px',
                height: Math.random() * 8 + 4 + 'px',
                borderRadius: Math.random() > 0.5 ? '50%' : '2px',
                background: colors[Math.floor(Math.random() * colors.length)],
                left: Math.random() * 100 + 'vw',
                top: '-10px',
                zIndex: '9999',
                pointerEvents: 'none',
                opacity: '1',
                transition: 'none'
            });
            document.body.appendChild(dot);
            const dur = Math.random() * 2 + 1.5;
            const x   = (Math.random() - 0.5) * 300;
            dot.animate([
                { transform: 'translate(0,0) rotate(0deg)', opacity: 1 },
                { transform: `translate(${x}px, ${window.innerHeight + 50}px) rotate(${Math.random()*720}deg)`, opacity: 0 }
            ], { duration: dur * 1000, easing: 'cubic-bezier(0.25,0.46,0.45,0.94)', fill: 'forwards', delay: Math.random() * 600 }).onfinish = () => dot.remove();
        }
    }
});
