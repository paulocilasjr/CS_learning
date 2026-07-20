(() => {
  "use strict";

  const config = window.GAME_CONFIG;
  const missions = config.missions;
  const cards = config.cards;
  const directionArrow = { north: "↑", east: "→", south: "↓", west: "←" };

  const elements = {
    missionTitle: document.querySelector("#missionTitle"),
    skillLabel: document.querySelector("#skillLabel"),
    story: document.querySelector("#storyText"),
    instruction: document.querySelector("#instructionText"),
    board: document.querySelector("#board"),
    feedback: document.querySelector("#feedback"),
    coachFace: document.querySelector("#coachFace"),
    cardTray: document.querySelector("#cardTray"),
    planTray: document.querySelector("#planTray"),
    planCount: document.querySelector("#planCount"),
    tryCounter: document.querySelector("#tryCounter"),
    levelProgress: document.querySelector("#levelProgress"),
    badgeCount: document.querySelector("#badgeCount"),
    tryButton: document.querySelector("#tryButton"),
    undoButton: document.querySelector("#undoButton"),
    clearButton: document.querySelector("#clearButton"),
    hintButton: document.querySelector("#hintButton"),
    speakButton: document.querySelector("#speakButton"),
    restartButton: document.querySelector("#restartButton"),
    exitButton: document.querySelector("#exitButton"),
    celebration: document.querySelector("#celebration"),
    celebrationTitle: document.querySelector("#celebrationTitle"),
    celebrationText: document.querySelector("#celebrationText"),
    nextButton: document.querySelector("#nextButton"),
    goodbye: document.querySelector("#goodbye"),
  };

  const saved = config.savedProgress;

  let currentIndex = config.startIndex;
  let badges = 0;
  if (!config.explicitStart && saved && Number.isInteger(saved.current_index)) {
    currentIndex = saved.current_index >= missions.length ? 0 : saved.current_index;
    badges = Math.min(Number(saved.badges) || 0, missions.length);
  }

  let mission = missions[currentIndex];
  let plan = [];
  let attempts = 0;
  let hintIndex = 0;
  let running = false;
  let activeStep = -1;
  let world = startingWorld(mission);

  function startingWorld(item) {
    return {
      position: [...item.start],
      facing: item.facing,
      remaining_stars: item.stars.map(position => [...position]),
      complete: false,
    };
  }

  function samePosition(left, right) {
    return left[0] === right[0] && left[1] === right[1];
  }

  function positionKey(position) {
    return `${position[0]},${position[1]}`;
  }

  function setPhase(name) {
    document.querySelectorAll(".thinking-step").forEach(step => {
      step.classList.toggle("active", step.dataset.phase === name);
    });
  }

  function showFeedback(text, tone = "") {
    elements.feedback.textContent = text;
    elements.feedback.className = `feedback ${tone}`.trim();
    elements.coachFace.textContent = tone === "good" ? "🥳" : tone === "notice" ? "🤔" : "🤖";
  }

  function renderProgress() {
    elements.levelProgress.replaceChildren();
    missions.forEach((item, index) => {
      const dot = document.createElement("span");
      dot.className = "progress-dot";
      if (index < currentIndex) dot.classList.add("done");
      if (index === currentIndex) dot.classList.add("current");
      dot.title = `Level ${item.number}: ${item.name}`;
      elements.levelProgress.append(dot);
    });
    elements.badgeCount.textContent = `🏅 ${badges}`;
  }

  function renderBoard(state, bumpPosition = null) {
    const obstacles = new Set(mission.obstacles.map(positionKey));
    const stars = new Set(state.remaining_stars.map(positionKey));
    elements.board.style.gridTemplateColumns = `repeat(${mission.width}, 1fr)`;
    elements.board.replaceChildren();

    for (let y = 0; y < mission.height; y += 1) {
      for (let x = 0; x < mission.width; x += 1) {
        const position = [x, y];
        const key = positionKey(position);
        const cell = document.createElement("div");
        cell.className = "board-cell";
        if (samePosition(position, mission.goal)) cell.classList.add("goal");
        if (bumpPosition && samePosition(position, bumpPosition)) cell.classList.add("bump");

        if (obstacles.has(key)) {
          cell.textContent = "🪨";
          cell.setAttribute("aria-label", "space rock");
        } else if (samePosition(position, state.position)) {
          const droid = document.createElement("span");
          droid.className = "droid";
          droid.textContent = "🤖";
          const facing = document.createElement("span");
          facing.className = "facing";
          facing.textContent = directionArrow[state.facing];
          cell.append(droid, facing);
          cell.setAttribute("aria-label", `BB-8 facing ${state.facing}`);
        } else if (stars.has(key)) {
          cell.textContent = "⭐";
          cell.setAttribute("aria-label", "star map");
        }

        if (samePosition(position, mission.goal)) {
          const goal = document.createElement("span");
          goal.className = "goal-corner";
          goal.textContent = "🏁";
          cell.append(goal);
        }
        elements.board.append(cell);
      }
    }
  }

  function renderCards() {
    elements.cardTray.replaceChildren();
    mission.cards.forEach(action => {
      const card = cards[action];
      const button = document.createElement("button");
      button.type = "button";
      button.className = "action-card";
      button.disabled = running;
      button.setAttribute("aria-label", card.spoken_name);
      button.innerHTML = `<span class="action-picture">${card.picture}</span><span class="action-name">${card.name}</span>`;
      button.addEventListener("click", () => addCard(action));
      elements.cardTray.append(button);
    });
  }

  function renderPlan() {
    elements.planTray.replaceChildren();
    elements.planCount.textContent = `${plan.length} ${plan.length === 1 ? "step" : "steps"} / ${mission.max_steps}`;
    if (plan.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-plan";
      empty.textContent = "Tap a picture card to start your plan";
      elements.planTray.append(empty);
    } else {
      plan.forEach((action, index) => {
        const card = cards[action];
        const button = document.createElement("button");
        button.type = "button";
        button.className = "plan-card";
        if (index === activeStep) button.classList.add("active");
        button.dataset.step = String(index + 1);
        button.textContent = card.picture;
        button.title = `Remove step ${index + 1}: ${card.spoken_name}`;
        button.disabled = running;
        button.addEventListener("click", () => removeCard(index));
        elements.planTray.append(button);
      });
    }
    elements.undoButton.disabled = running || plan.length === 0;
    elements.clearButton.disabled = running || plan.length === 0;
    elements.tryButton.disabled = running || plan.length === 0;
  }

  function resetBoardForPlanning() {
    world = startingWorld(mission);
    activeStep = -1;
    renderBoard(world);
    setPhase("plan");
  }

  function addCard(action) {
    if (running) return;
    if (plan.length >= mission.max_steps) {
      showFeedback("Your plan is full. Tap a plan card to remove one, or try the plan now.", "notice");
      return;
    }
    plan.push(action);
    resetBoardForPlanning();
    renderPlan();
    showFeedback(`${cards[action].name} joined your plan. What should happen next?`);
  }

  function removeCard(index) {
    if (running) return;
    const [removed] = plan.splice(index, 1);
    resetBoardForPlanning();
    renderPlan();
    showFeedback(`You changed the plan by removing ${cards[removed].name}. Good debugging!`, "good");
  }

  function undo() {
    if (plan.length) removeCard(plan.length - 1);
  }

  function clearPlan() {
    if (running || plan.length === 0) return;
    plan = [];
    resetBoardForPlanning();
    renderPlan();
    showFeedback("The plan is clear. Build a new idea and try again.", "good");
  }

  async function api(path, payload = {}) {
    const response = await fetch(`${config.apiBase}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`Game connection error (${response.status})`);
    return response.json();
  }

  async function tryPlan() {
    if (running || plan.length === 0) return;
    running = true;
    attempts += 1;
    elements.tryCounter.textContent = `🌱 Try ${attempts}: every try teaches your brain!`;
    setPhase("try");
    showFeedback("Watch closely. What does each picture make BB-8 do?");
    renderCards();
    renderPlan();

    try {
      const started = await api("/run/start", { mission: currentIndex, plan });
      world = started.world;
      activeStep = -1;
      renderBoard(world);
      renderPlan();
      window.setTimeout(runNextStep, 450);
    } catch (error) {
      running = false;
      renderCards();
      renderPlan();
      showFeedback("The game connection paused. Please try again.", "notice");
      console.error(error);
    }
  }

  async function runNextStep() {
    try {
      const progress = await api("/run/next");
      activeStep = progress.index - 1;
      world = progress.world;
      renderPlan();
      renderBoard(world, progress.error ? world.position : null);
      showFeedback(progress.error || progress.message, progress.error ? "notice" : "");

      if (!progress.finished) {
        window.setTimeout(runNextStep, config.stepDelayMs);
        return;
      }

      running = false;
      activeStep = -1;
      renderCards();
      renderPlan();
      if (progress.complete) {
        completeMission();
      } else {
        reflectOnAttempt(progress);
      }
    } catch (error) {
      running = false;
      activeStep = -1;
      renderCards();
      renderPlan();
      showFeedback("The game connection paused. Your plan is still here.", "notice");
      console.error(error);
    }
  }

  function reflectOnAttempt(progress) {
    setPhase("change");
    if (progress.error.includes("rock")) {
      showFeedback("The rock stopped BB-8. Great noticing! Which step should change before that move?", "notice");
    } else if (progress.error.includes("edge")) {
      showFeedback("BB-8 reached the edge. Great clue! Change a turn or remove a move.", "notice");
    } else if (progress.error.includes("no star")) {
      showFeedback("BB-8 reached down before standing on the star. Change the order and try again.", "notice");
    } else if (world.remaining_stars.length > 0) {
      showFeedback("The star is still waiting. Where should GET or CHECK go in the plan?", "notice");
    } else {
      showFeedback("BB-8 stopped before the flag. Look at the board, change one idea, and try again.", "notice");
    }
    speak(elements.feedback.textContent);
  }

  function completeMission() {
    badges = Math.max(badges, currentIndex + 1);
    saveProgress(currentIndex + 1);
    elements.badgeCount.textContent = `🏅 ${badges}`;
    elements.celebrationTitle.textContent = attempts > 1 ? "You kept trying!" : "Your plan worked!";
    elements.celebrationText.textContent = attempts > 1
      ? `You noticed, changed your idea, and solved it in ${attempts} tries. That is how coders learn.`
      : "You looked, planned, and checked your idea. That is strong thinking!";
    elements.nextButton.textContent = currentIndex === missions.length - 1 ? "PLAY AGAIN ↺" : "NEXT ADVENTURE ➜";
    elements.celebration.classList.remove("hidden");
    speak(`${elements.celebrationTitle.textContent} ${elements.celebrationText.textContent}`);
  }

  function nextMission() {
    elements.celebration.classList.add("hidden");
    currentIndex = currentIndex === missions.length - 1 ? 0 : currentIndex + 1;
    loadMission();
  }

  function showHint() {
    const hint = mission.hints[Math.min(hintIndex, mission.hints.length - 1)];
    hintIndex += 1;
    setPhase("look");
    showFeedback(`Clue: ${hint}`, "notice");
    speak(hint);
  }

  function speak(text) {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const voice = new SpeechSynthesisUtterance(text);
    voice.rate = 0.82;
    voice.pitch = 1.08;
    window.speechSynthesis.speak(voice);
  }

  function readMission() {
    speak(`${mission.name}. ${mission.story} Your goal: ${mission.instruction}`);
  }

  async function saveProgress(nextIndex = currentIndex) {
    if (!config.saveEnabled) return;
    try {
      await api("/progress", { current_index: nextIndex, badges });
    } catch (error) {
      console.error("Could not save picture progress", error);
    }
  }

  function startOver() {
    if (!window.confirm("Grown-up check: start the picture adventure again from level 1?")) return;
    currentIndex = 0;
    badges = 0;
    saveProgress(0);
    loadMission();
  }

  async function leaveGame() {
    await saveProgress();
    elements.goodbye.classList.remove("hidden");
    try { await api("/close"); } catch (_error) { /* The server may close first. */ }
  }

  function loadMission() {
    mission = missions[currentIndex];
    attempts = 0;
    hintIndex = 0;
    running = false;
    activeStep = -1;
    plan = [...mission.starter_plan];
    world = startingWorld(mission);

    elements.missionTitle.textContent = `Level ${mission.number}: ${mission.name}`;
    elements.skillLabel.textContent = mission.skill;
    elements.story.textContent = mission.story;
    elements.instruction.textContent = `🎯 ${mission.instruction}`;
    elements.tryCounter.textContent = "🌱 Every try grows your brain!";
    setPhase("look");
    renderProgress();
    renderBoard(world);
    renderCards();
    renderPlan();

    if (mission.starter_plan.length) {
      showFeedback("R2-D2 left a plan. Tap TRY, watch where it stops, then fix it.", "notice");
    } else if (mission.number === 1) {
      showFeedback("Look at BB-8 and the flag. Then tap the big GO card.");
    } else {
      showFeedback("First look at the board. What needs to happen before BB-8 reaches the flag?");
    }
  }

  elements.tryButton.addEventListener("click", tryPlan);
  elements.undoButton.addEventListener("click", undo);
  elements.clearButton.addEventListener("click", clearPlan);
  elements.hintButton.addEventListener("click", showHint);
  elements.speakButton.addEventListener("click", readMission);
  elements.restartButton.addEventListener("click", startOver);
  elements.exitButton.addEventListener("click", leaveGame);
  elements.nextButton.addEventListener("click", nextMission);
  window.addEventListener("beforeunload", () => {
    if (!config.saveEnabled) return;
    const payload = new Blob(
      [JSON.stringify({ current_index: currentIndex, badges })],
      { type: "application/json" },
    );
    navigator.sendBeacon(`${config.apiBase}/progress`, payload);
  });

  loadMission();
})();
