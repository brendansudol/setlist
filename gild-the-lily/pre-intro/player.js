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

  // Steel-string voice from Woodshed's js/audio.js (b7265be).
  function fundamentalDecay(midi) {
    if (midi <= 50) return 2.6;
    if (midi <= 57) return 2.6 + ((midi - 50) / 7) * 8.4;
    return 11 + (midi - 57) * 0.15;
  }

  function stringBuffer(midi) {
    if (buffers.has(midi)) return buffers.get(midi);
    const sr = ctx.sampleRate, f0 = 440 * 2 ** ((midi - 69) / 12);
    // A whole note at the slowest practice tempo lasts six seconds.
    const sound = ctx.createBuffer(1, Math.ceil(sr * 6.2), sr);
    const samples = sound.getChannelData(0);
    const pickPosition = 0.19 + 0.035 * Math.sin(midi * 1.9);
    const baseDecay = fundamentalDecay(midi);
    const top = Math.min(5200, sr * 0.45);
    const tilt = 1.55 - 0.45 * Math.min(1, Math.max(0, (midi - 50) / 14));
    for (let k = 1; k * f0 < top; k++) {
      const hz = k * f0 * Math.sqrt(1 + 0.00005 * k * k);
      const body = hz * hz / (hz * hz + 115 * 115) / Math.sqrt(1 + (hz / 4200) ** 4);
      const amp = Math.max(Math.abs(Math.sin(k * Math.PI * pickPosition)), 0.14) / k ** tilt * body;
      const decay = baseDecay + 24 * (hz - f0) / 1000;
      // The lower partials have a strong attack and a quieter, lingering component.
      const parts = k <= 12 ? [[0.72, 1, -0.00014], [0.28, 0.5, 0.00036]] : [[1, 1, 0]];
      for (const [share, speed, detune] of parts) {
        const r = 10 ** (-(decay * speed) / 20 / sr);
        const w = 2 * Math.PI * hz * (1 + detune) / sr;
        const length = Math.min(samples.length, Math.ceil(60 / (decay * speed) * sr));
        const c1 = 2 * r * Math.cos(w), c2 = r * r;
        let last = 0, previous = -amp * share * Math.sin(w) / r;
        for (let i = 0; i < length; i++) {
          const sample = c1 * last - c2 * previous;
          samples[i] += sample;
          previous = last;
          last = sample;
        }
      }
    }

    // A repeatable, twelve-millisecond pick transient.
    let seed = midi * 9301 + 49297, noise = 0, peak = 0;
    for (let i = 0; i < samples.length; i++) peak = Math.max(peak, Math.abs(samples[i]));
    const attack = Math.floor(sr * 0.012);
    for (let i = 0; i < attack; i++) {
      seed = (seed * 1103515245 + 12345) & 0x7fffffff;
      noise += 0.35 * (seed / 0x3fffffff - 1 - noise);
      samples[i] += noise * peak * 0.22 * (1 - i / attack) ** 2;
    }
    const windowLength = Math.floor(sr * 0.3);
    let energy = 0;
    for (let i = 0; i < windowLength; i++) energy += samples[i] ** 2;
    const level = 0.16 / Math.sqrt(energy / windowLength);
    const fade = Math.floor(sr * 0.2);
    for (let i = 0; i < samples.length; i++) {
      samples[i] *= level * Math.min(1, (samples.length - i) / fade);
    }
    buffers.set(midi, sound);
    return sound;
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
    const source = ctx.createBufferSource();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    const soft = ['hammer', 'pull', 'slide'].includes(event.tech);
    const velocity = soft ? 0.55 : 0.85;
    source.buffer = stringBuffer(midi);
    filter.type = 'lowpass';
    filter.frequency.value = 1800 + velocity * 5200;
    gain.gain.value = velocity * 0.8;
    if (soft) {
      gain.gain.setValueAtTime(0, time);
      gain.gain.linearRampToValueAtTime(velocity * 0.8, time + 0.006);
    }
    source.connect(filter).connect(gain).connect(master);
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
      filter.disconnect();
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

  function setAudioSessionType(type) {
    try {
      if (navigator.audioSession) navigator.audioSession.type = type;
    } catch {
      // Audio session hints are optional. Web Audio can still play without one.
    }
  }

  async function start() {
    if (!Audio || run) return;
    const session = { bar: first, step: 0, at: 0, time: 0, count: 0 };
    run = session;
    go.setAttribute('aria-pressed', 'true');
    goText.textContent = 'Stop';
    try {
      // On iPhone, music playback uses media volume even in Silent Mode.
      setAudioSessionType('playback');
      if (!ctx) ctx = new Audio();
      await ctx.resume();
      if (run !== session) return;
      master = ctx.createGain();
      master.gain.value = 0.5;
      master.connect(ctx.destination);
      // Build one uncached pitch per scheduler tick, starting during the count-in.
      const pitches = score.bars.slice(first, last + 1).flatMap(steps =>
        steps.flatMap(event => event.notes.map(([, midi]) => midi)));
      const toWarm = [...new Set(pitches)].filter(midi => !buffers.has(midi));
      run.time = ctx.currentTime + 0.07;
      pump();
      timer = setInterval(() => {
        pump();
        if (toWarm.length) stringBuffer(toWarm.shift());
      }, 25);
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
    setAudioSessionType('auto');
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
