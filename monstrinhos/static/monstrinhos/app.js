"use strict";

// A batalha vive no navegador: ela não envia nem altera dados no servidor.
document.querySelectorAll("[data-battle]").forEach((arena) => {
  const startButton = arena.querySelector("[data-battle-start]");
  const target = arena.querySelector("[data-battle-target]");
  const targetLabel = arena.querySelector("[data-battle-target-label]");
  const scoreLabel = arena.querySelector("[data-battle-score]");
  const timeLabel = arena.querySelector("[data-battle-time]");
  const recordLabel = arena.querySelector("[data-battle-record]");
  const statusLabel = arena.querySelector("[data-battle-status]");
  const storageKey = `monstrinhos:recorde:${arena.dataset.monsterId}`;
  const duration = 10000;
  let score = 0;
  let record = 0;
  let running = false;
  let deadline = 0;
  let timer = null;

  // O jogo também funciona no modo privado ou com armazenamento bloqueado.
  try {
    const savedRecord = Number(localStorage.getItem(storageKey));
    if (Number.isSafeInteger(savedRecord) && savedRecord >= 0) record = savedRecord;
  } catch (_) {
    // O recorde continua disponível na memória desta página.
  }
  recordLabel.textContent = String(record);

  function finishBattle() {
    if (!running) return;
    running = false;
    window.clearInterval(timer);
    timer = null;
    target.disabled = true;
    targetLabel.textContent = "Mandou bem!";
    timeLabel.textContent = "0,0";
    arena.classList.remove("battle-running");
    startButton.disabled = false;
    startButton.textContent = "Jogar novamente";
    const newRecord = score > record;
    if (newRecord) {
      record = score;
      recordLabel.textContent = String(record);
      try {
        localStorage.setItem(storageKey, String(record));
      } catch (_) {
        // A indisponibilidade do localStorage não interrompe a brincadeira.
      }
    }
    statusLabel.textContent = `${newRecord ? "Novo recorde! " : "Batalha concluída! "}${score} ${score === 1 ? "clique" : "cliques"} em 10 segundos.`;
  }

  function updateClock() {
    const remaining = Math.max(0, deadline - performance.now());
    timeLabel.textContent = (remaining / 1000).toFixed(1).replace(".", ",");
    if (remaining <= 0) finishBattle();
  }

  startButton.addEventListener("click", () => {
    if (running) return;
    score = 0;
    scoreLabel.textContent = "0";
    timeLabel.textContent = "10,0";
    running = true;
    deadline = performance.now() + duration;
    startButton.disabled = true;
    startButton.textContent = "Batalha em andamento";
    target.disabled = false;
    targetLabel.textContent = "Clique aqui!";
    arena.classList.add("battle-running");
    statusLabel.textContent = "Valendo! Clique no alvo ou use Enter ou Espaço.";
    // Foco no alvo permite jogar também com o teclado.
    target.focus({ preventScroll: true });
    timer = window.setInterval(updateClock, 50);
  });

  target.addEventListener("click", () => {
    if (!running) return;
    // Compara o relógio em cada clique, mesmo se a aba atrasar o temporizador.
    if (performance.now() >= deadline) {
      finishBattle();
      return;
    }
    score += 1;
    scoreLabel.textContent = String(score);
  });

  // Ao retornar de outra aba, atualiza o prazo sem prolongar a partida.
  document.addEventListener("visibilitychange", () => {
    if (running) updateClock();
  });
});
