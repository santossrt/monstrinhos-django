const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'monstrinhos', 'static', 'monstrinhos', 'app.js'),
  'utf8',
);

// The real browser script runs unchanged. This DOM supplies only the elements
// exposed by detalhe.html; the clock lets tests exercise delayed browser timers.
function createBattle({ storageUnavailable = false, stored = new Map() } = {}) {
  let now = 0;
  let nextTimer = 1;
  const timers = new Map();
  const elements = new Map();
  const documentHandlers = new Map();

  function element(textContent = '') {
    const handlers = new Map();
    return {
      textContent,
      disabled: false,
      dataset: {},
      classList: { add() {}, remove() {} },
      addEventListener(name, callback) {
        if (!handlers.has(name)) handlers.set(name, []);
        handlers.get(name).push(callback);
      },
      dispatch(name = 'click') {
        for (const callback of handlers.get(name) ?? []) {
          callback({ type: name, target: this, preventDefault() {} });
        }
      },
      click() { if (!this.disabled) this.dispatch(); },
      focus() {},
    };
  }

  for (const [name, value] of Object.entries({
    start: 'Iniciar batalha', target: '', 'target-label': 'Prepare-se!',
    score: '0', time: '10,0', record: '0',
    status: 'Seu monstrinho está pronto. E você?',
  })) elements.set(`[data-battle-${name}]`, element(value));
  elements.get('[data-battle-target]').disabled = true;
  const battle = element();
  battle.dataset.monsterId = '1';
  battle.querySelector = (selector) => elements.get(selector) ?? null;

  const document = {
    querySelectorAll: (selector) => selector === '[data-battle]' ? [battle] : [],
    addEventListener(name, callback) {
      if (!documentHandlers.has(name)) documentHandlers.set(name, []);
      documentHandlers.get(name).push(callback);
    },
  };
  const storage = {
    getItem(key) {
      if (storageUnavailable) throw new Error('Browser storage disabled');
      return stored.get(key) ?? null;
    },
    setItem(key, value) {
      if (storageUnavailable) throw new Error('Browser storage disabled');
      stored.set(key, String(value));
    },
  };
  function schedule(callback, delay) {
    const id = nextTimer++;
    timers.set(id, { callback, deadline: now + delay, delay });
    return id;
  }
  const sandbox = {
    document,
    localStorage: storage,
    performance: { now: () => now },
    setInterval: schedule,
    clearInterval: (id) => timers.delete(id),
  };
  sandbox.window = sandbox;
  vm.runInNewContext(source, sandbox, { filename: 'app.js' });

  return {
    start: elements.get('[data-battle-start]'),
    target: elements.get('[data-battle-target]'),
    score: elements.get('[data-battle-score]'),
    time: elements.get('[data-battle-time]'),
    record: elements.get('[data-battle-record]'),
    status: elements.get('[data-battle-status]'),
    stored,
    elapseWithoutTimers(milliseconds) { now += milliseconds; },
    returnToTab() {
      for (const callback of documentHandlers.get('visibilitychange') ?? []) callback();
    },
    advance(milliseconds) {
      const finishAt = now + milliseconds;
      let iterations = 0;
      while (true) {
        const due = [...timers.entries()]
          .filter(([, timer]) => timer.deadline <= finishAt)
          .sort(([, a], [, b]) => a.deadline - b.deadline)[0];
        if (!due) break;
        assert.ok(++iterations < 10000, 'The browser timer must eventually finish');
        const [, timer] = due;
        now = Math.max(now, timer.deadline);
        timer.deadline = now + timer.delay;
        timer.callback();
      }
      now = finishAt;
    },
  };
}

test('o alvo fica bloqueado antes do início e cliques não pontuam', () => {
  const game = createBattle();
  assert.equal(game.target.disabled, true);
  game.target.dispatch();
  assert.equal(game.score.textContent, '0');
  assert.equal(game.start.disabled, false);
});

test('iniciar habilita os ataques e cada clique conta uma vez', () => {
  const game = createBattle();
  game.start.click();
  assert.equal(game.target.disabled, false);
  assert.equal(game.start.disabled, true);
  game.target.click();
  game.target.click();
  game.target.click();
  assert.equal(game.score.textContent, '3');
  game.advance(1000);
  assert.ok(Number(game.time.textContent.replace(',', '.')) <= 9);
});

test('um segundo início durante a rodada não zera a pontuação nem o prazo', () => {
  const game = createBattle();
  game.start.click();
  game.target.click();
  game.advance(9000);
  game.start.dispatch();
  assert.equal(game.score.textContent, '1');
  game.advance(1000);
  assert.equal(game.target.disabled, true);
  assert.equal(game.start.disabled, false);
});

test('a batalha termina em dez segundos e bloqueia ataques posteriores', () => {
  const game = createBattle();
  game.start.click();
  game.advance(9900);
  assert.equal(game.target.disabled, false);
  game.target.click();
  game.advance(100);
  assert.equal(game.target.disabled, true);
  assert.equal(game.start.disabled, false);
  assert.equal(Number(game.time.textContent.replace(',', '.')), 0);
  assert.equal(game.score.textContent, '1');
  game.target.dispatch();
  assert.equal(game.score.textContent, '1');
});

test('um ataque no prazo exato não pontua mesmo com o timer do navegador atrasado', () => {
  const game = createBattle();
  game.start.click();
  game.target.click();
  game.elapseWithoutTimers(10000);
  game.target.dispatch();
  assert.equal(game.score.textContent, '1');
  assert.equal(game.target.disabled, true);
  assert.equal(game.start.disabled, false);
});

test('voltar para uma aba suspensa encerra a rodada vencida', () => {
  const game = createBattle();
  game.start.click();
  game.target.click();
  game.elapseWithoutTimers(20000);
  game.returnToTab();
  assert.equal(game.target.disabled, true);
  assert.equal(game.start.disabled, false);
  assert.equal(Number(game.time.textContent.replace(',', '.')), 0);
  assert.equal(game.score.textContent, '1');
});

test('reiniciar limpa a rodada e conserva o maior recorde', () => {
  const game = createBattle();
  game.start.click();
  game.target.click();
  game.target.click();
  game.advance(10000);
  assert.equal(game.record.textContent, '2');
  game.start.click();
  assert.equal(game.score.textContent, '0');
  assert.equal(game.target.disabled, false);
  assert.equal(Number(game.time.textContent.replace(',', '.')), 10);
  game.target.click();
  game.advance(10000);
  assert.equal(game.score.textContent, '1');
  assert.equal(game.record.textContent, '2');
});

test('o recorde pode ser recuperado ao reabrir a página', () => {
  const stored = new Map();
  const first = createBattle({ stored });
  first.start.click();
  first.target.click();
  first.target.click();
  first.advance(10000);
  assert.equal(first.record.textContent, '2');
  assert.equal(createBattle({ stored }).record.textContent, '2');
});

test('a batalha e o recorde da página funcionam com localStorage indisponível', () => {
  const game = createBattle({ storageUnavailable: true });
  game.start.click();
  game.target.click();
  game.target.click();
  game.advance(10000);
  assert.equal(game.target.disabled, true);
  assert.equal(game.record.textContent, '2');
  game.start.click();
  game.target.click();
  game.advance(10000);
  assert.equal(game.record.textContent, '2');
});

test('o script também carrega em páginas sem batalha', () => {
  vm.runInNewContext(source, {
    document: {
      querySelectorAll: () => [],
    },
  });
});
