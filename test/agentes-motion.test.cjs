const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('site.js', 'utf8');

function page({ reduced = false, observer = true, hidden = false, crop = true } = {}) {
  const changes = [], visibility = [], observers = [];
  const motion = { matches: reduced, addEventListener: (_, fn) => changes.push(fn) };
  const imgs = ['claudio', 'valdir'].map(name => {
    const events = {}, attrs = { src: `img/equipe/${name}.webp` }, classes = new Set();
    return { dataset: { retratoAnimado: `img/equipe/animados/${name}.png` }, writes: 0,
      classList: { toggle(name, value) { if (value) classes.add(name); else classes.delete(name); }, contains: name => classes.has(name) },
      getAttribute: key => attrs[key], setAttribute(key, value) { attrs[key] = value; this.writes++; },
      addEventListener: (name, fn) => { events[name] = fn; }, fire: name => events[name]?.(),
    };
  });
  class IO {
    constructor(fn) { this.fn = fn; this.targets = []; observers.push(this); }
    observe(el) { this.targets.push(el); }
    unobserve() {}
  }
  const document = { hidden, documentElement: { classList: { add() {} } },
    querySelectorAll: selector => selector === 'img[data-retrato-animado]' ? imgs : [],
    addEventListener: (_, fn) => visibility.push(fn),
  };
  const window = { CSS: { supports: () => crop }, ...(observer ? { IntersectionObserver: IO } : {}) };
  vm.runInNewContext(code, { matchMedia: () => motion, window, IntersectionObserver: IO, document });
  return { imgs, visible(im, value) { observers.find(o => o.targets.includes(im)).fn([{ target: im, isIntersecting: value }]); },
    reduced(value) { motion.matches = value; changes.forEach(fn => fn()); },
    hidden(value) { document.hidden = value; visibility.forEach(fn => fn()); },
  };
}

test('the homepage keeps six existing static images as the no-JS fallback', () => {
  const html = fs.readFileSync('index.html', 'utf8');
  const agents = [...html.matchAll(/<img\b[^>]*data-retrato-animado="([^"]+)"[^>]*>/g)];
  assert.equal(agents.length, 6);
  for (const [, animated] of agents) {
    const name = animated.match(/\/([^/]+)\.png$/)[1];
    const tag = agents.find(row => row[1] === animated)[0];
    assert.ok(tag.includes(`src="img/equipe/${name}.webp"`));
    assert.ok(tag.includes('width="240" height="240"'));
    assert.ok(tag.includes('loading="lazy" decoding="async"'));
    assert.ok(fs.existsSync(`img/equipe/${name}.webp`));
    assert.ok(fs.existsSync(animated));
  }
});

test('only visible portraits request animation and repeat notifications do not restart it', () => {
  const p = page(), [a, b] = p.imgs;
  assert.equal(a.writes, 0);
  p.visible(a, true);
  assert.equal(a.getAttribute('src'), a.dataset.retratoAnimado);
  assert.equal(a.classList.contains('retrato-em-movimento'), true);
  assert.equal(b.writes, 0);
  p.visible(a, true);
  assert.equal(a.writes, 1);
  p.visible(a, false);
  assert.equal(a.getAttribute('src'), 'img/equipe/claudio.webp');
  assert.equal(a.classList.contains('retrato-em-movimento'), false);
});

test('reduced motion blocks animation requests and responds to live preference changes', () => {
  const p = page({ reduced: true }), [a] = p.imgs;
  p.visible(a, true);
  assert.equal(a.writes, 0);
  assert.equal(a.classList.contains('retrato-em-movimento'), false);
  p.reduced(false);
  assert.equal(a.getAttribute('src'), a.dataset.retratoAnimado);
  p.reduced(true);
  assert.equal(a.getAttribute('src'), 'img/equipe/claudio.webp');
  assert.equal(a.classList.contains('retrato-em-movimento'), false);
});

test('hiding the tab restores static portraits and visibility resumes only those in view', () => {
  const p = page(), [a, b] = p.imgs;
  p.visible(a, true);
  p.hidden(true);
  assert.equal(a.getAttribute('src'), 'img/equipe/claudio.webp');
  assert.equal(a.classList.contains('retrato-em-movimento'), false);
  p.hidden(false);
  assert.equal(a.getAttribute('src'), a.dataset.retratoAnimado);
  assert.equal(b.writes, 0);
});

test('an animation error keeps the existing static fallback without retry loops', () => {
  const p = page(), [a] = p.imgs;
  p.visible(a, true);
  a.fire('error');
  assert.equal(a.getAttribute('src'), 'img/equipe/claudio.webp');
  p.visible(a, false); p.visible(a, true); p.reduced(false);
  assert.equal(a.writes, 2);
});

test('without IntersectionObserver all portraits remain static', () => {
  const p = page({ observer: false });
  p.reduced(false);
  assert.ok(p.imgs.every(im => im.writes === 0));
});

test('without square cropping support the original portraits remain static', () => {
  const p = page({ crop: false });
  p.reduced(false);
  assert.ok(p.imgs.every(im => im.writes === 0));
});
