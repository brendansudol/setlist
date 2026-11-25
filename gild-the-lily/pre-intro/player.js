// Inlined by build.py so the practice sheet also plays directly from disk.
(() => {
  'use strict';
  const score = JSON.parse(document.getElementById('score-data').textContent);
  const bars = Array.from(document.querySelectorAll('.bar'));
  const groups = bars.map(bar => bar.querySelectorAll('.step'));
  const cursors = bars.map(bar => bar.querySelector('.cursor'));
  const go = document.getElementById('go');
  const goText = document.getElementById('go-text');
  const tempo = document.getElementById('tempo');
  const tempoOut = document.getElementById('tempo-out');
  const clickBox = document.getElementById('click');
  const loop = document.getElementById('loop');
  const position = document.getElementById('position');
  const controls = document.querySelector('.controls');
  const Audio = window.AudioContext || window.webkitAudioContext;

  const buffers = new Map();
  const ringing = new Map();
  let ctx, master, run, timer, frame;
  let first = 0, last = bars.length - 1;
  let queue = [], activeBar = -1, activeStep = null;

  function buffer(midi) {
    if (buffers.has(midi)) return buffers.get(midi);
    const frequency = 440 * 2 ** ((midi - 69) / 12);
    const period = Math.round(ctx.sampleRate / frequency - 0.5);
    const sound = ctx.createBuffer(1, Math.ceil(ctx.sampleRate * 6.2), ctx.sampleRate);
    const data = sound.getChannelData(0);
    let previous = 0;
    for (let i = 0; i < period; i++) {
      previous = 0.55 * (Math.random() * 2 - 1) + 0.45 * previous;
      data[i] = previous;
    }
    data[period] = 0.5 * data[0];
    for (let i = period + 1; i < data.length; i++) {
      data[i] = 0.998 * 0.5 * (data[i - period] + data[i - period - 1]);
    }
    const pluck = { sound, rate: frequency * (period + 0.5) / ctx.sampleRate };
    buffers.set(midi, pluck);
    return pluck;
  }

  function damp(time, strings = ringing.keys()) {
    for (const string of strings) {
      const voice = ringing.get(string);
      if (!voice) continue;
      voice.gain.gain.setTargetAtTime(0, time, 0.004);
      voice.source.stop(time + 0.025);
      ringing.delete(string);
    }
  }

  function pluck(string, midi, event, time, duration) {
    const tone = buffer(midi);
    const source = ctx.createBufferSource();
    const gain = ctx.createGain();
    const soft = ['hammer', 'pull', 'slide'].includes(event.tech);
    source.buffer = tone.sound;
    source.playbackRate.value = tone.rate;
    gain.gain.value = soft ? 0.55 : 0.85;
    source.connect(gain).connect(master);
    let vibrato, depth;
    if (event.tech === 'slide' || event.tech === 'slide in') {
      // The approach mark before fret 10 gives direction only.
      source.detune.setValueAtTime(100 * (event.slideOffset ?? -2), time);
      source.detune.linearRampToValueAtTime(0, time + Math.min(0.10, duration * 0.45));
    } else if (event.tech === 'bend') {
      source.detune.setValueAtTime(0, time);
      source.detune.linearRampToValueAtTime(100, time + duration * 0.85);
    } else if (event.tech === 'vibrato') {
      vibrato = ctx.createOscillator();
      depth = ctx.createGain();
      vibrato.frequency.value = 5.5;
      depth.gain.value = 16;
      vibrato.connect(depth).connect(source.detune);
      vibrato.start(time);
    }
    source.onended = () => {
      if (vibrato) {
        vibrato.stop();
        vibrato.disconnect();
        depth.disconnect();
      }
      source.disconnect();
      gain.disconnect();
    };
    source.start(time, soft ? 0.012 : 0);
    ringing.set(string, { source, gain });
  }

  function tick(time, downbeat) {
    const osc = ctx.createOscillator(), gain = ctx.createGain();
    osc.frequency.value = downbeat ? 1568 : 1047;
    gain.gain.setValueAtTime(0.0001, time);
    gain.gain.exponentialRampToValueAtTime(downbeat ? 0.5 : 0.32, time + 0.002);
    gain.gain.exponentialRampToValueAtTime(0.0001, time + 0.06);
    osc.connect(gain).connect(master);
    osc.start(time);
    osc.stop(time + 0.08);
  }

  // Wake at every beat and every written onset. Rests advance the same clock
  // as notes, including the full-bar rests and the two half rests in bar 59.
  function pump() {
    while (run && run.time < ctx.currentTime + 0.15) {
      const beatSeconds = 60 / Number(tempo.value);
      const time = run.time;
      if (run.count < 4) {
        tick(time, run.count === 0);
        run.count++;
        run.time += beatSeconds;
        queue.push({ time, end: run.time, bar: -1, count: run.count });
        continue;
      }
      const steps = score.bars[run.bar], event = steps[run.step];
      const beatOffset = run.at % score.beat;
      const ticks = Math.min(event.at + event.dur - run.at, score.beat - beatOffset);
      if (run.at === event.at) {
        // Let the original pre-intro arpeggios ring across strings.
        const letRing = run.bar < score.preIntroBars && event.notes.length && !(run.bar === first && run.step === 0);
        damp(time, letRing ? event.notes.map(([string]) => string) : undefined);
        for (const [string, midi] of event.notes) {
          pluck(string, midi, event, time, event.dur * beatSeconds / score.beat);
        }
      }
      if (clickBox.checked && beatOffset === 0) tick(time, run.at === 0);
      const dx = (event.endX - event.x) / event.dur;
      const x = event.x + (run.at - event.at) * dx;
      run.time += ticks * beatSeconds / score.beat;
      queue.push({ time, end: run.time, bar: run.bar, step: run.step, x, endX: x + dx * ticks });
      run.at += ticks;
      if (run.at === event.at + event.dur) run.step++;
      if (run.step === steps.length) {
        run.step = run.at = 0;
        run.bar = run.bar === last ? first : run.bar + 1;
      }
    }
  }

  function reveal(element, force = false) {
    const rect = element.getBoundingClientRect();
    const top = controls.offsetHeight + 20;
    if (force || rect.top < top || rect.bottom > window.innerHeight - 10) {
      window.scrollBy(0, rect.top - top);
    }
  }

  function draw() {
    const now = ctx.currentTime;
    while (queue.length && queue[0].end <= now) queue.shift();
    const q = queue[0];
    if (q && q.time <= now) {
      if (q.bar < 0) {
        position.textContent = 'Count-in · ' + q.count;
      } else {
        const bar = bars[q.bar], step = groups[q.bar][q.step];
        if (activeBar !== q.bar) {
          if (activeBar >= 0) bars[activeBar].classList.remove('now');
          activeBar = q.bar;
          bar.classList.add('now');
          position.textContent = 'Bar ' + (q.bar + 1) + ' / ' + bars.length;
          reveal(bar);
        }
        if (activeStep !== step) {
          if (activeStep) activeStep.classList.remove('on');
          activeStep = step;
          step.classList.add('on');
        }
        const x = q.x + (q.endX - q.x) * (now - q.time) / (q.end - q.time);
        const cursor = cursors[q.bar];
        cursor.setAttribute('x1', x.toFixed(2));
        cursor.setAttribute('x2', x.toFixed(2));
      }
    }
    if (run) frame = requestAnimationFrame(draw);
  }

  async function start() {
    if (!Audio || run) return;
    const session = { bar: first, step: 0, at: 0, time: 0, count: 0 };
    run = session;
    go.setAttribute('aria-pressed', 'true');
    goText.textContent = 'Stop';
    try {
      if (!ctx) ctx = new Audio();
      await ctx.resume();
      if (run !== session) return;
      master = ctx.createGain();
      master.gain.value = 0.5;
      master.connect(ctx.destination);
      run.time = ctx.currentTime + 0.07;
      pump();
      timer = setInterval(pump, 25);
      frame = requestAnimationFrame(draw);
    } catch (error) {
      if (run === session) {
        stop();
        goText.textContent = 'Retry audio';
      }
    }
  }

  function stop() {
    run = null;
    clearInterval(timer);
    cancelAnimationFrame(frame);
    if (master) {
      const output = master;
      output.gain.setTargetAtTime(0, ctx.currentTime, 0.006);
      damp(ctx.currentTime);
      setTimeout(() => output.disconnect(), 80);
      master = null;
    }
    queue = [];
    if (activeBar >= 0) bars[activeBar].classList.remove('now');
    if (activeStep) activeStep.classList.remove('on');
    activeBar = -1;
    activeStep = null;
    go.setAttribute('aria-pressed', 'false');
    goText.textContent = 'Play';
    position.textContent = '';
  }

  function setRange(a, b, jump) {
    const restart = !!run;
    if (restart) stop();
    first = a;
    last = b;
    const single = a === b;
    document.getElementById('single-bar')?.remove();
    if (single) {
      const option = new Option('Bar ' + (a + 1), (a + 1) + '-' + (b + 1));
      option.id = 'single-bar';
      loop.add(option);
    }
    loop.value = (a + 1) + '-' + (b + 1);
    bars.forEach((bar, i) => {
      bar.classList.toggle('out', i < a || i > b);
      bar.setAttribute('aria-pressed', String(single && i === a));
    });
    if (jump) reveal(document.getElementById('section-' + (a + 1)) || bars[a], true);
    if (restart) start();
  }

  function toggle() { if (run) stop(); else start(); }

  go.addEventListener('click', toggle);
  tempo.addEventListener('input', () => { tempoOut.textContent = tempo.value + ' bpm'; });
  function applyLoopOption() {
    const [a, b] = loop.value.split('-').map(Number);
    setRange(a - 1, b - 1, true);
  }
  loop.addEventListener('change', applyLoopOption);
  function followPassageLink() {
    const anchor = location.hash.slice(1);
    const option = Array.from(loop.options).find(o => o.dataset.anchor === anchor);
    if (option) {
      loop.value = option.value;
      applyLoopOption();
    }
  }
  window.addEventListener('load', followPassageLink);
  window.addEventListener('hashchange', followPassageLink);
  bars.forEach((bar, i) => bar.addEventListener('click', () => {
    if (first === i && last === i) setRange(0, bars.length - 1, false);
    else setRange(i, i, false);
  }));
  document.addEventListener('keydown', event => {
    if (event.key !== ' ' || event.repeat || event.metaKey || event.ctrlKey || event.altKey) return;
    if (event.target.closest('button, input, select, summary, a, textarea')) return;
    event.preventDefault();
    toggle();
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && run) stop(); });
  if (!Audio) { go.disabled = true; goText.textContent = 'Audio unavailable'; }
})();
