import Matter from 'matter-js';
import './style.css';
import './reveal.css';

type Fate = 'boss' | 'reply' | 'coffee';
type Phase = 'loading' | 'ready' | 'dropping' | 'alarm' | 'result';
type Player = { name: string; avatar: string };

declare global {
  interface Window {
    Aigram?: { telegramId: string | null; isInAigram: boolean; callAigramAPI: (url: string, method?: string) => Promise<any> };
    __LAST_STRAW?: { getState: () => object; dropAt: (x: number) => void; forceOutcome: (fate: Fate) => void };
  }
}

const query = new URLSearchParams(location.search);
const locale: 'zh' | 'en' = (() => {
  const override = localStorage.getItem('game_locale');
  if (override === 'zh' || override === 'en') return override;
  return navigator.language.toLowerCase().startsWith('zh') ? 'zh' : 'en';
})();

const copy = {
  en: {
    eyebrow: 'OFFICE SURVIVAL FORECAST No. 01', titleA: "TODAY'S", titleB: 'LAST STRAW',
    loading: 'CALIBRATING YOUR BAD LUCK…', prompt: 'TAP TO DROP YOURSELF', sub: 'One fall. Three terrible possibilities.',
    drop: 'DROP ME', falling: 'NO TAKING IT BACK', boss: 'THE BOSS', reply: 'REPLY ALL', coffee: 'THE SPILL',
    bossAlarm: 'THE BOSS WANTS A WORD.', replyAlarm: 'YOU HIT REPLY ALL.', coffeeAlarm: 'THAT WAS HIS COFFEE.',
    bossTurn: 'He packed the wrong box.', replyTurn: 'Everyone finally saw who stole your work.', coffeeTurn: 'He fell into the right box.',
    again: 'DROP AGAIN', videoSoon: 'FULL REVERSAL FILM IN PRODUCTION', mute: 'SOUND', fate: 'TODAY DEALT YOU',
  },
  zh: {
    eyebrow: '办公室生存预报 01', titleA: '今天最后的', titleB: '一根稻草',
    loading: '正在校准你的霉运…', prompt: '点击，把自己扔下去', sub: '一次下落，三种糟糕可能。',
    drop: '扔下我', falling: '没有后悔药', boss: '老板找你', reply: '误点全员回复', coffee: '咖啡泼了',
    bossAlarm: '老板说：来聊一下。', replyAlarm: '你刚刚点了全员回复。', coffeeAlarm: '那杯咖啡是老板的。',
    bossTurn: '最后收拾箱子的人不是你。', replyTurn: '所有人终于看见是谁偷了你的功劳。', coffeeTurn: '他掉进了最合适的箱子。',
    again: '再掉一次', videoSoon: '完整反转影像制作中', mute: '声音', fate: '今天抽中了',
  },
}[locale];

document.documentElement.lang = locale;
document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <section class="ls-shell">
    <div class="ls-paper" aria-hidden="true"></div>
    <header class="ls-header">
      <span class="ls-eyebrow">${copy.eyebrow}</span>
      <h1><span>${copy.titleA}</span><strong>${copy.titleB}</strong></h1>
      <p id="instruction">${copy.loading}</p>
    </header>
    <main class="ls-machine" id="machine">
      <div class="ls-machine__rail" aria-hidden="true"></div>
      <div id="crane" class="ls-crane" hidden>
        <div class="ls-crane__hook"></div>
        <div class="ls-avatar"><img id="avatar" alt="" draggable="false" /></div>
        <b id="player-name"></b>
      </div>
      <canvas id="board" aria-hidden="true"></canvas>
      <div id="puck" class="ls-puck" hidden><img alt="" draggable="false" /></div>
      <div class="ls-gates" aria-hidden="true">
        <div data-fate="boss"><span>01</span><b>${copy.boss}</b></div>
        <div data-fate="reply"><span>02</span><b>${copy.reply}</b></div>
        <div data-fate="coffee"><span>03</span><b>${copy.coffee}</b></div>
      </div>
      <div id="alarm" class="ls-alarm" hidden><span>!</span><strong></strong></div>
    </main>
    <button id="drop" class="ls-drop" type="button" disabled>${copy.loading}</button>
    <section id="result" class="ls-result" hidden>
      <video id="result-video" playsinline preload="auto"></video>
      <img id="result-still" alt="" draggable="false" />
      <div class="ls-result__shade"></div>
      <div class="ls-result__top"><span>${copy.fate}</span><strong id="result-label"></strong></div>
      <div class="ls-result__bottom">
        <h2 id="result-turn"></h2>
        <p id="result-note"></p>
        <button id="again" type="button">${copy.again}</button>
      </div>
    </section>
  </section>`;

const shell = document.querySelector<HTMLElement>('.ls-shell')!;
const machine = document.querySelector<HTMLElement>('#machine')!;
const canvas = document.querySelector<HTMLCanvasElement>('#board')!;
const ctx = canvas.getContext('2d')!;
const crane = document.querySelector<HTMLElement>('#crane')!;
const craneAvatar = document.querySelector<HTMLImageElement>('#avatar')!;
const playerName = document.querySelector<HTMLElement>('#player-name')!;
const puckEl = document.querySelector<HTMLElement>('#puck')!;
const puckImg = puckEl.querySelector<HTMLImageElement>('img')!;
const instruction = document.querySelector<HTMLElement>('#instruction')!;
const dropButton = document.querySelector<HTMLButtonElement>('#drop')!;
const alarm = document.querySelector<HTMLElement>('#alarm')!;
const alarmText = alarm.querySelector<HTMLElement>('strong')!;
const result = document.querySelector<HTMLElement>('#result')!;
const resultVideo = document.querySelector<HTMLVideoElement>('#result-video')!;
const resultStill = document.querySelector<HTMLImageElement>('#result-still')!;
const resultLabel = document.querySelector<HTMLElement>('#result-label')!;
const resultTurn = document.querySelector<HTMLElement>('#result-turn')!;
const resultNote = document.querySelector<HTMLElement>('#result-note')!;
const againButton = document.querySelector<HTMLButtonElement>('#again')!;

let phase: Phase = 'loading';
let player: Player = { name: 'AlterU', avatar: './default-avatar.png' };
let engine: Matter.Engine | null = null;
let puck: Matter.Body | null = null;
let pins: Matter.Body[] = [];
let aim = .5;
let aimOverride: number | null = null;
let startAt = performance.now();
let lastTs = performance.now();
let raf = 0;
let lastPinTone = 0;
let audio: AudioContext | null = null;
let currentFate: Fate | null = null;

function tone(from: number, to: number, duration: number, type: OscillatorType = 'triangle', gain = .045) {
  audio ||= new AudioContext();
  const now = audio.currentTime, oscillator = audio.createOscillator(), volume = audio.createGain();
  oscillator.type = type; oscillator.frequency.setValueAtTime(from, now); oscillator.frequency.exponentialRampToValueAtTime(Math.max(30, to), now + duration);
  volume.gain.setValueAtTime(gain, now); volume.gain.exponentialRampToValueAtTime(.0001, now + duration);
  oscillator.connect(volume).connect(audio.destination); oscillator.start(now); oscillator.stop(now + duration);
}

async function loadPlayer() {
  const overrideName = query.get('user_name');
  const overrideAvatar = query.get('avatar_url');
  if (overrideName || overrideAvatar) {
    player = { name: overrideName || 'AlterU', avatar: overrideAvatar || './default-avatar.png' };
    return ready();
  }
  const A = window.Aigram;
  if (A?.isInAigram && A.telegramId) {
    try {
      const response = await A.callAigramAPI(`/note/telegram/user/get/info/by/telegram_id?telegram_id=${encodeURIComponent(A.telegramId)}`, 'GET');
      const info = response?.data ?? response;
      player = { name: String(info?.name ?? info?.user_name ?? 'AlterU'), avatar: String(info?.head_url ?? './default-avatar.png') };
    } catch { /* honest published fallback */ }
  }
  ready();
}

function ready() {
  craneAvatar.src = puckImg.src = player.avatar;
  playerName.textContent = player.name;
  crane.hidden = false;
  phase = 'ready';
  instruction.textContent = copy.sub;
  dropButton.disabled = false;
  dropButton.textContent = copy.drop;
  setupWorld();
}

function setupWorld() {
  if (engine) Matter.Engine.clear(engine);
  engine = Matter.Engine.create();
  engine.gravity.y = 1.05;
  pins = []; puck = null; currentFate = null;
  puckEl.hidden = true; alarm.hidden = true; result.hidden = true; resultVideo.pause();
  const w = machine.clientWidth, h = machine.clientHeight;
  const dpr = Math.min(2, devicePixelRatio || 1);
  canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr); canvas.style.width = `${w}px`; canvas.style.height = `${h}px`; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const walls = [
    Matter.Bodies.rectangle(-10, h / 2, 20, h, { isStatic: true }),
    Matter.Bodies.rectangle(w + 10, h / 2, 20, h, { isStatic: true }),
  ];
  const top = Math.max(80, h * .17), bottom = h - Math.max(92, h * .18);
  const rows = h < 420 ? 5 : 6;
  for (let row = 0; row < rows; row++) {
    const count = row % 2 ? 6 : 5;
    const y = top + (bottom - top) * (row / Math.max(1, rows - 1));
    for (let col = 0; col < count; col++) {
      const x = w * .12 + (w * .76) * ((col + (row % 2 ? 0 : .5)) / count);
      const pin = Matter.Bodies.circle(x, y, Math.max(5, w * .015), { isStatic: true, restitution: .42, label: 'pin' });
      pins.push(pin);
    }
  }
  const dividers = [w / 3, w * 2 / 3].map(x => Matter.Bodies.rectangle(x, h - 45, 8, 92, { isStatic: true, chamfer: { radius: 4 } }));
  Matter.Composite.add(engine.world, [...walls, ...pins, ...dividers]);
  Matter.Events.on(engine, 'collisionStart', event => {
    const now = performance.now();
    if (!puck || now - lastPinTone < 45) return;
    if (event.pairs.some(pair => pair.bodyA.label === 'pin' || pair.bodyB.label === 'pin')) {
      lastPinTone = now; shell.classList.remove('hit'); void shell.offsetWidth; shell.classList.add('hit');
      tone(420 + (puck.position.x / w) * 340, 330, .055);
    }
  });
}

function dropAt(normalized?: number) {
  if (phase !== 'ready' || !engine) return;
  if (typeof normalized === 'number') aimOverride = Math.max(.12, Math.min(.88, normalized));
  const w = machine.clientWidth, r = Math.max(15, Math.min(19, w * .048));
  const x = w * (aimOverride ?? aim);
  puck = Matter.Bodies.circle(x, 54, r, { restitution: .36, friction: .04, frictionAir: .002, density: .0022, label: 'player' });
  Matter.Composite.add(engine.world, puck);
  puckEl.style.width = puckEl.style.height = `${r * 2}px`; puckEl.hidden = false; crane.hidden = true;
  phase = 'dropping'; dropButton.disabled = true; dropButton.textContent = copy.falling; instruction.textContent = copy.falling;
  tone(180, 110, .09, 'sine');
}

function fateFromX(x: number): Fate { return x < machine.clientWidth / 3 ? 'boss' : x < machine.clientWidth * 2 / 3 ? 'reply' : 'coffee'; }
function labelFor(fate: Fate) { return fate === 'boss' ? copy.boss : fate === 'reply' ? copy.reply : copy.coffee; }
function alarmFor(fate: Fate) { return fate === 'boss' ? copy.bossAlarm : fate === 'reply' ? copy.replyAlarm : copy.coffeeAlarm; }
function turnFor(fate: Fate) { return fate === 'boss' ? copy.bossTurn : fate === 'reply' ? copy.replyTurn : copy.coffeeTurn; }

function reveal(fate: Fate) {
  if (phase !== 'dropping') return;
  currentFate = fate; phase = 'alarm';
  if (puck) { Matter.Body.setStatic(puck, true); }
  alarmText.textContent = alarmFor(fate); alarm.hidden = false;
  tone(880, 680, .08, 'square'); setTimeout(() => tone(880, 680, .08, 'square'), 190);
  setTimeout(() => showResult(fate), 900);
}

function showResult(fate: Fate) {
  phase = 'result'; result.hidden = false; result.classList.remove('resolved'); result.classList.add('show');
  resultLabel.textContent = labelFor(fate); resultTurn.textContent = turnFor(fate);
  const media = {
    boss: { video: './generated/boss_result.mp4', start: './generated/boss_start.webp', end: './generated/boss_end.webp' },
    reply: { video: './generated/reply_result.mp4', start: './generated/reply_start.webp', end: './generated/reply_end.webp' },
    coffee: { video: './generated/coffee_result.mp4', start: './generated/coffee_start.webp', end: './generated/coffee_end.webp' },
  }[fate];
  resultNote.textContent = ''; resultVideo.hidden = false; resultStill.hidden = true;
  resultVideo.src = media.video; resultVideo.poster = media.start; resultVideo.currentTime = 0;
  resultVideo.onended = () => { result.classList.add('resolved'); tone(392, 523, .1); setTimeout(() => tone(523, 659, .1), 110); };
  resultVideo.onerror = () => { resultVideo.hidden = true; resultStill.hidden = false; resultStill.src = media.end; resultNote.textContent = copy.videoSoon; result.classList.add('resolved'); };
  resultVideo.play().catch(() => { resultVideo.controls = true; });
}

function reset() {
  result.classList.remove('show', 'resolved'); result.hidden = true; resultVideo.pause(); resultVideo.removeAttribute('src'); resultVideo.load();
  crane.hidden = false; phase = 'ready'; aimOverride = null; startAt = performance.now(); instruction.textContent = copy.sub;
  dropButton.disabled = false; dropButton.textContent = copy.drop; setupWorld();
}

function draw() {
  const w = machine.clientWidth, h = machine.clientHeight;
  ctx.clearRect(0, 0, w, h);
  ctx.strokeStyle = 'rgba(244,200,75,.3)'; ctx.lineWidth = 1;
  for (const pin of pins) {
    ctx.beginPath(); ctx.arc(pin.position.x, pin.position.y, pin.circleRadius || 6, 0, Math.PI * 2);
    ctx.fillStyle = '#f4c84b'; ctx.fill(); ctx.strokeStyle = '#171512'; ctx.lineWidth = 2; ctx.stroke();
  }
  ctx.strokeStyle = 'rgba(244,240,225,.16)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(w / 3, h - 90); ctx.lineTo(w / 3, h); ctx.moveTo(w * 2 / 3, h - 90); ctx.lineTo(w * 2 / 3, h); ctx.stroke();
}

function loop(ts: number) {
  const dt = Math.min(32, ts - lastTs); lastTs = ts;
  if (phase === 'ready') {
    const wave = .5 + Math.sin((ts - startAt) * Math.PI * .00084) * .32;
    aim = wave; crane.style.left = `${wave * 100}%`;
  }
  if (engine) Matter.Engine.update(engine, dt);
  draw();
  if (puck) {
    puckEl.style.transform = `translate3d(${puck.position.x}px,${puck.position.y}px,0) translate(-50%,-50%) rotate(${puck.angle}rad)`;
    if (phase === 'dropping' && puck.position.y > machine.clientHeight - 52) reveal(query.get('outcome') as Fate || fateFromX(puck.position.x));
  }
  raf = requestAnimationFrame(loop);
}

dropButton.addEventListener('pointerdown', event => { event.preventDefault(); dropAt(); });
machine.addEventListener('pointerdown', event => { if (phase !== 'ready' || (event.target as HTMLElement).closest('button')) return; event.preventDefault(); dropAt(); });
againButton.addEventListener('pointerdown', event => { event.preventDefault(); reset(); });
addEventListener('keydown', event => {
  if (!['Space', 'Enter'].includes(event.code)) return; event.preventDefault();
  if (phase === 'ready') dropAt(); else if (phase === 'result') reset();
});
addEventListener('resize', () => { if (phase === 'ready') setupWorld(); });
window.__LAST_STRAW = {
  getState: () => ({ phase, fate: currentFate, player: player.name, aim, puck: puck ? { x: puck.position.x, y: puck.position.y } : null }),
  dropAt,
  forceOutcome: fate => { if (phase === 'ready') dropAt(fate === 'boss' ? .18 : fate === 'reply' ? .5 : .82); setTimeout(() => reveal(fate), 80); },
};

loadPlayer();
lastTs = performance.now(); raf = requestAnimationFrame(loop);
addEventListener('beforeunload', () => cancelAnimationFrame(raf));
