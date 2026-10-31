const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('site.js', 'utf8');

function page({ reduced = false, observer = true, reject = false, pending = false } = {}) {
  const listeners = {};
  const motion = { matches: reduced, addEventListener: (name, fn) => { listeners[name] = fn; } };
  function video(logo) {
    const events = {};
    return { tagName: 'VIDEO', hidden: logo, ended: false, plays: 0, pauses: 0,
      hasAttribute: name => name === 'data-logo-animado' && logo,
      removeAttribute() {},
      addEventListener: (name, fn) => { events[name] = fn; },
      play() { this.plays++; if (logo && pending) return new Promise((resolve, reject) => { this.rejectPlay = reject; }); return reject && logo ? Promise.reject(new Error('autoplay')) : Promise.resolve(); },
      pause() { this.pauses++; },
      fire(name) { if (name === 'ended') this.ended = true; events[name]?.(); },
    };
  }
  const logo = video(true), game = video(false);
  logo.parentElement = { querySelector: () => logo };
  const observers = [];
  class IO {
    constructor(fn) { this.fn = fn; this.targets = []; observers.push(this); }
    observe(el) { this.targets.push(el); }
    unobserve() {}
  }
  const context = { matchMedia: () => motion, window: observer ? { IntersectionObserver: IO } : {},
    IntersectionObserver: IO, document: { documentElement: { classList: { add() {} } },
      querySelectorAll: selector => selector === 'video' ? [logo, game] : [],
    },
  };
  vm.runInNewContext(code, context);
  return { logo, game, visible(target, value) { observers.at(-1).fn([{ target, isIntersecting: value }]); },
    change(value) { motion.matches = value; listeners.change?.(); }, observers };
}

test('logo starts only in view and stays on the poster after finishing', async () => {
  const p = page();
  assert.ok(p.observers.at(-1).targets.includes(p.logo.parentElement));
  assert.equal(p.logo.plays, 0);
  p.visible(p.logo.parentElement, true);
  assert.equal(p.logo.plays, 1);
  assert.equal(p.logo.hidden, false);
  p.logo.fire('ended');
  assert.equal(p.logo.hidden, true);
  p.visible(p.logo.parentElement, false);
  p.visible(p.logo.parentElement, true);
  assert.equal(p.logo.plays, 1);
});

test('reduced motion keeps the poster, including live preference changes', () => {
  const p = page({ reduced: true });
  assert.equal(p.logo.plays, 0);
  p.visible(p.logo.parentElement, true);
  assert.equal(p.logo.plays, 0);
  assert.equal(p.logo.hidden, true);
  p.change(false);
  assert.equal(p.logo.plays, 1);
  assert.equal(p.logo.hidden, false);
  p.change(true);
  assert.equal(p.logo.hidden, true);
  assert.ok(p.logo.pauses > 0);
});

test('autoplay rejection and media errors retain the static fallback', async () => {
  const p = page({ reject: true });
  p.visible(p.logo.parentElement, true);
  await Promise.resolve(); await Promise.resolve();
  assert.equal(p.logo.hidden, true);
  const q = page();
  q.visible(q.logo.parentElement, true);
  q.logo.fire('error');
  assert.equal(q.logo.hidden, true);
  q.visible(q.logo.parentElement, true);
  assert.equal(q.logo.hidden, true);
});

test('game videos continue to play in view and pause out of view', () => {
  const p = page();
  p.visible(p.game, true);
  assert.equal(p.game.plays, 1);
  p.visible(p.game, false);
  assert.ok(p.game.pauses > 0);
  p.change(true);
  p.visible(p.game, true);
  assert.equal(p.game.plays, 1);
});

test('without IntersectionObserver the logo still respects reduced motion', () => {
  const p = page({ observer: false, reduced: true });
  assert.equal(p.logo.plays, 0);
  assert.equal(p.logo.hidden, true);
  p.change(false);
  assert.equal(p.logo.plays, 1);
});

// Pausar durante o carregamento aborta play(); isso não deve invalidar a mídia.
test('a loading interruption can resume when the logo comes back into view', async () => {
  const p = page({ pending: true });
  p.visible(p.logo.parentElement, true);
  p.visible(p.logo.parentElement, false);
  p.logo.rejectPlay(Object.assign(new Error('paused while loading'), { name: 'AbortError' }));
  await Promise.resolve(); await Promise.resolve();
  p.visible(p.logo.parentElement, true);
  assert.equal(p.logo.plays, 2);
  assert.equal(p.logo.hidden, false);
});
