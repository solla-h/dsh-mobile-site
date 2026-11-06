/* Interactive simulations. No gateway calls, storage, or copied app code. */

const AXIS_LOCK = 8;
const SWIPE_COMMIT = 72;
const ARC_STEP = 48;
const DOUBLE_TAP_DELAY = 320;
const REACTION_MS = 900;

export function gestureAxis(dx, dy, threshold = AXIS_LOCK) {
  const x = Math.abs(dx);
  const y = Math.abs(dy);
  if (x < threshold && y < threshold) return null;
  if (x === y) return null;
  return x > y ? 'horizontal' : 'vertical';
}

export function clampIndex(index, count) {
  if (!Number.isFinite(count) || count < 1) return 0;
  const value = Number.isFinite(index) ? Math.trunc(index) : 0;
  return Math.min(Math.max(value, 0), count - 1);
}

export function swipeIndex(index, dx, count, threshold = SWIPE_COMMIT) {
  const current = clampIndex(index, count);
  if (!Number.isFinite(dx) || Math.abs(dx) < threshold) return current;
  return clampIndex(current + (dx < 0 ? 1 : -1), count);
}

export function arcIndex(index, dy, count, step = ARC_STEP) {
  const current = clampIndex(index, count);
  if (!Number.isFinite(dy) || !(step > 0)) return current;
  return clampIndex(current + Math.trunc(-dy / step), count);
}

export function clampCenter(center, stageWidth, elementWidth) {
  const stage = Number.isFinite(stageWidth) ? stageWidth : 0;
  if (stage <= 0) return 0;
  const element = Math.max(0, Number.isFinite(elementWidth) ? elementWidth : 0);
  const half = Math.min(element, stage) / 2;
  const value = Number.isFinite(center) ? center : stage / 2;
  return Math.min(Math.max(value, half), stage - half);
}

function markReady(root) {
  root.classList.add('demo-ready');
  for (const controls of root.querySelectorAll('[data-demo-controls]')) {
    controls.hidden = false;
  }
}

function initPetDemo(root) {
  if (!root) return;
  const stage = root.querySelector('[data-pet-stage]');
  const button = root.querySelector('[data-pet-button]');
  const image = root.querySelector('[data-pet-image]');
  if (!stage || !button || !image) return;

  const chat = root.querySelector('[data-pet-chat]');
  const newButton = root.querySelector('[data-pet-new]');
  const resetButton = root.querySelector('[data-pet-reset]');
  const motion = root.querySelector('[data-pet-motion]');
  const status = root.querySelector('[data-pet-status]');
  const reduceQuery =
    typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-reduced-motion: reduce)')
      : null;

  const stillSrc = image.dataset.still || image.getAttribute('src') || '';
  const idleSrc = image.dataset.idle || stillSrc;
  const happySrc = image.dataset.happy || stillSrc;
  const failedSources = new Set();

  let currentMode = 'still';
  let currentSource = stillSrc;
  let reactionTimer = 0;
  let pendingSingle = 0;
  let suppressClickUntil = 0;
  let visible = true;
  let moved = false;
  let center = 0;

  let pointerId = null;
  let dragStartX = 0;
  let dragStartY = 0;
  let dragStartCenter = 0;
  let axis = null;
  let dragging = false;

  function prefersReducedMotion() {
    return Boolean(reduceQuery && reduceQuery.matches);
  }

  function setStatus(key) {
    if (status) status.textContent = root.dataset[key] || '';
  }

  function applyMode(mode) {
    let source = stillSrc;
    if (mode === 'idle') source = idleSrc;
    if (mode === 'happy') source = happySrc;
    if (!source || failedSources.has(source)) {
      mode = 'still';
      source = stillSrc;
    }
    if (!source) return;
    currentMode = mode;
    currentSource = source;
    if (image.getAttribute('src') !== source) image.src = source;
  }

  function syncImage() {
    if (document.hidden || !visible) {
      stopReaction();
      applyMode('still');
      return;
    }
    if (currentMode === 'happy') return;
    applyMode(motion && motion.checked ? 'idle' : 'still');
  }

  function stopReaction() {
    if (reactionTimer) {
      window.clearTimeout(reactionTimer);
      reactionTimer = 0;
    }
    if (currentMode === 'happy') currentMode = 'still';
  }

  function scheduleReactionEnd() {
    if (currentMode !== 'happy') return;
    if (reactionTimer) window.clearTimeout(reactionTimer);
    reactionTimer = window.setTimeout(() => {
      reactionTimer = 0;
      currentMode = 'still';
      syncImage();
    }, REACTION_MS);
  }

  function cancelPendingSingle() {
    if (pendingSingle) {
      window.clearTimeout(pendingSingle);
      pendingSingle = 0;
    }
  }

  function suppressPointerClick() {
    suppressClickUntil = Date.now() + 450;
  }

  function metrics() {
    return {
      stageWidth: stage.clientWidth,
      buttonWidth: button.getBoundingClientRect().width || button.offsetWidth || 0,
    };
  }

  function layout() {
    const { stageWidth, buttonWidth } = metrics();
    if (!stageWidth || !buttonWidth) return;
    if (!moved) center = stageWidth / 2;
    center = clampCenter(center, stageWidth, buttonWidth);
    button.style.left = `${center}px`;
  }

  function react() {
    cancelPendingSingle();
    stopReaction();
    setStatus('reacted');
    if (!prefersReducedMotion() && !document.hidden && visible) {
      applyMode('happy');
      // Start the visible reaction after loading, so a cold request cannot consume it.
      if (image.complete && image.naturalWidth > 0) scheduleReactionEnd();
    } else {
      syncImage();
    }
  }

  function openChat() {
    cancelPendingSingle();
    stopReaction();
    if (chat) chat.hidden = false;
    setStatus('created');
    syncImage();
  }

  function resetDemo() {
    cancelPendingSingle();
    stopReaction();
    if (chat) chat.hidden = true;
    moved = false;
    center = 0;
    layout();
    setStatus('reset');
    syncImage();
  }

  function releasePointer() {
    const id = pointerId;
    pointerId = null;
    dragging = false;
    axis = null;
    if (id !== null && button.hasPointerCapture && button.hasPointerCapture(id)) {
      try {
        button.releasePointerCapture(id);
      } catch {
        /* The pointer may already be gone. */
      }
    }
  }

  function finishPointer(cancelled) {
    const wasDragging = dragging;
    const travelled = Math.abs(center - dragStartCenter);
    const { stageWidth } = metrics();

    if (wasDragging) {
      suppressPointerClick();
      moved = stageWidth > 0 && Math.abs(center - stageWidth / 2) > 0.5;
      if (!cancelled && travelled > 0.5) setStatus('moved');
    }
    releasePointer();
  }

  image.addEventListener('load', scheduleReactionEnd);
  image.addEventListener('error', () => {
    if (currentMode === 'still') return;
    failedSources.add(currentSource);
    applyMode('still');
  });

  button.addEventListener('pointerdown', (event) => {
    if (pointerId !== null || event.isPrimary === false) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    suppressClickUntil = 0;
    layout();
    const { stageWidth, buttonWidth } = metrics();
    if (!stageWidth || !buttonWidth) return;

    pointerId = event.pointerId;
    dragStartX = event.clientX;
    dragStartY = event.clientY;
    dragStartCenter = center;
    axis = null;
    dragging = false;
    try {
      button.setPointerCapture(event.pointerId);
    } catch {
      /* Pointer capture is an enhancement; moves still arrive while over the button. */
    }
  });

  button.addEventListener('pointermove', (event) => {
    if (event.pointerId !== pointerId) return;
    const dx = event.clientX - dragStartX;
    const dy = event.clientY - dragStartY;

    if (!axis) {
      const intent = gestureAxis(dx, dy);
      if (!intent) return;
      axis = intent;
      if (intent === 'vertical') return;
      dragging = true;
      cancelPendingSingle();
    }

    if (!dragging) return;
    event.preventDefault();
    const { stageWidth, buttonWidth } = metrics();
    if (!stageWidth || !buttonWidth) return;
    center = clampCenter(dragStartCenter + dx, stageWidth, buttonWidth);
    button.style.left = `${center}px`;
  });

  button.addEventListener('pointerup', (event) => {
    if (event.pointerId !== pointerId) return;
    finishPointer(false);
  });

  button.addEventListener('pointercancel', (event) => {
    if (event.pointerId !== pointerId) return;
    finishPointer(true);
  });

  button.addEventListener('lostpointercapture', (event) => {
    if (event.pointerId !== pointerId) return;
    finishPointer(true);
  });

  button.addEventListener('click', (event) => {
    if (event.detail > 0 && Date.now() < suppressClickUntil) {
      suppressClickUntil = 0;
      event.preventDefault();
      return;
    }

    if (event.detail === 0) {
      cancelPendingSingle();
      react();
      return;
    }

    if (event.detail > 1 || pendingSingle) {
      cancelPendingSingle();
      openChat();
      return;
    }

    pendingSingle = window.setTimeout(() => {
      pendingSingle = 0;
      react();
    }, DOUBLE_TAP_DELAY);
  });

  if (newButton) newButton.addEventListener('click', openChat);
  if (resetButton) resetButton.addEventListener('click', resetDemo);

  if (motion) {
    motion.addEventListener('change', () => {
      if (!motion.checked) stopReaction();
      syncImage();
    });
  }

  if (reduceQuery) {
    const onReduceChange = () => {
      if (reduceQuery.matches) stopReaction();
      syncImage();
    };
    if (typeof reduceQuery.addEventListener === 'function') {
      reduceQuery.addEventListener('change', onReduceChange);
    }
  }

  document.addEventListener('visibilitychange', syncImage);

  if (typeof window.IntersectionObserver === 'function') {
    const observer = new window.IntersectionObserver((entries) => {
      const entry = entries[entries.length - 1];
      if (!entry) return;
      visible = entry.isIntersecting;
      syncImage();
    });
    observer.observe(button);
  }

  if (typeof window.ResizeObserver === 'function') {
    const observer = new window.ResizeObserver(layout);
    observer.observe(stage);
    observer.observe(button);
  } else {
    window.addEventListener('resize', layout);
  }

  if (chat) chat.hidden = true;
  layout();
  syncImage();
  button.disabled = false;
  markReady(root);
}

function initPluginDemo(root) {
  if (!root) return;
  const zone = root.querySelector('[data-plugin-zone]');
  const cards = zone ? Array.from(zone.querySelectorAll('[data-plugin-card]')) : [];
  if (!zone || cards.length === 0) return;

  const previous = root.querySelector('[data-plugin-prev]');
  const next = root.querySelector('[data-plugin-next]');
  const reset = root.querySelector('[data-plugin-reset]');
  const count = root.querySelector('[data-plugin-count]');
  const status = root.querySelector('[data-plugin-status]');

  const initial = Math.floor(cards.length / 2);
  let index = initial;
  let pointerId = null;
  let startX = 0;
  let startY = 0;
  let axis = null;
  let dragging = false;

  function setDraggingState(active) {
    if (active) zone.dataset.dragging = 'true';
    else delete zone.dataset.dragging;
  }

  function resetTransforms() {
    for (const card of cards) card.style.transform = '';
  }

  function render(announce) {
    for (let i = 0; i < cards.length; i += 1) {
      const card = cards[i];
      card.hidden = i !== index;
      card.style.transform = '';
    }

    if (count) count.textContent = `${index + 1} / ${cards.length}`;
    if (previous) previous.disabled = index === 0;
    if (next) next.disabled = index === cards.length - 1;

    if (announce && status) {
      const heading = cards[index].querySelector('h4');
      const title = heading ? heading.textContent.trim() : '';
      status.textContent = `${index + 1} / ${cards.length}: ${title}`;
    }
  }

  function navigate(delta) {
    const target = clampIndex(index + delta, cards.length);
    if (target === index) return;
    index = target;
    render(true);
  }

  function stopPointer() {
    const id = pointerId;
    pointerId = null;
    dragging = false;
    axis = null;
    setDraggingState(false);
    resetTransforms();
    if (id !== null && zone.hasPointerCapture && zone.hasPointerCapture(id)) {
      try {
        zone.releasePointerCapture(id);
      } catch {
        /* The pointer may already be gone. */
      }
    }
  }

  zone.addEventListener('pointerdown', (event) => {
    if (pointerId !== null || event.isPrimary === false) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    const target = event.target;
    if (
      target &&
      typeof target.closest === 'function' &&
      target.closest('button, a, input, select, textarea, [role="button"]')
    ) {
      return;
    }

    pointerId = event.pointerId;
    startX = event.clientX;
    startY = event.clientY;
    axis = null;
    dragging = false;
    try {
      zone.setPointerCapture(event.pointerId);
    } catch {
      /* Pointer capture is optional for the simulation. */
    }
  });

  zone.addEventListener('pointermove', (event) => {
    if (event.pointerId !== pointerId) return;
    const dx = event.clientX - startX;
    const dy = event.clientY - startY;

    if (!axis) {
      const intent = gestureAxis(dx, dy);
      if (!intent) return;
      axis = intent;
      if (intent === 'vertical') return;
      dragging = true;
      setDraggingState(true);
    }

    if (!dragging) return;
    event.preventDefault();
    const shift = Math.max(-96, Math.min(96, dx));
    cards[index].style.transform = `translateX(${shift}px) rotate(${shift / 24}deg)`;
  });

  zone.addEventListener('pointerup', (event) => {
    if (event.pointerId !== pointerId) return;
    const wasDragging = dragging;
    const dx = event.clientX - startX;
    stopPointer();
    if (!wasDragging) return;
    const target = swipeIndex(index, dx, cards.length);
    if (target !== index) {
      index = target;
      render(true);
    }
  });

  zone.addEventListener('pointercancel', (event) => {
    if (event.pointerId !== pointerId) return;
    stopPointer();
  });

  zone.addEventListener('lostpointercapture', (event) => {
    if (event.pointerId !== pointerId) return;
    stopPointer();
  });

  zone.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;

    if (event.key === 'Escape') {
      if (pointerId !== null) {
        event.preventDefault();
        stopPointer();
      }
      return;
    }

    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    if (pointerId !== null) stopPointer();
    navigate(event.key === 'ArrowLeft' ? -1 : 1);
  });

  if (previous) {
    previous.addEventListener('click', () => {
      if (pointerId !== null) stopPointer();
      navigate(-1);
    });
  }

  if (next) {
    next.addEventListener('click', () => {
      if (pointerId !== null) stopPointer();
      navigate(1);
    });
  }

  if (reset) {
    reset.addEventListener('click', () => {
      if (pointerId !== null) stopPointer();
      index = initial;
      render(true);
    });
  }

  render(false);
  markReady(root);
}

function initArcDemo(root) {
  if (!root) return;
  const handle = root.querySelector('[data-arc-handle]');
  const menu = root.querySelector('[data-arc-menu]');
  const closeButton = root.querySelector('[data-arc-close]');
  const options = menu ? Array.from(menu.querySelectorAll('[data-arc-option]')) : [];
  const panels = Array.from(root.querySelectorAll('[data-arc-panel]'));
  const status = root.querySelector('[data-arc-status]');
  if (!handle || !menu || options.length === 0 || panels.length === 0) return;

  const count = Math.min(options.length, panels.length);
  const initial = Math.floor(count / 2);
  const optionIndexes = options.map((option, position) => {
    const value = Number.parseInt(option.dataset.index || '', 10);
    return Number.isInteger(value) && value >= 0 && value < count ? value : position;
  });

  let committed = initial;
  let preview = initial;
  let open = false;
  let suppressClickUntil = 0;
  let drag = null;

  function message(key) {
    if (status) status.textContent = root.dataset[key] || '';
  }

  function announceCommitted() {
    if (!status) return;
    const heading = panels[committed] ? panels[committed].querySelector('h4') : null;
    status.textContent = heading ? heading.textContent.trim() : '';
  }

  function updateOptions() {
    for (let i = 0; i < options.length; i += 1) {
      const option = options[i];
      const optionIndex = optionIndexes[i];
      option.setAttribute('aria-pressed', String(optionIndex === committed));
      option.classList.toggle('is-preview', open && optionIndex === preview);
    }
  }

  function showPanel(next) {
    committed = clampIndex(next, count);
    for (let i = 0; i < panels.length; i += 1) {
      panels[i].hidden = i !== committed;
    }
    updateOptions();
  }

  function onOutsideClick(event) {
    if (!open) return;
    const target = event.target;
    if (target && handle.contains(target)) return;
    cancelMenu();
  }

  function openMenu() {
    if (open) return;
    open = true;
    preview = committed;
    menu.hidden = false;
    root.setAttribute('data-open', '');
    handle.setAttribute('aria-expanded', 'true');
    updateOptions();
    message('opened');
    document.addEventListener('click', onOutsideClick);
  }

  function closeMenu(announceCancel, restoreFocus) {
    if (!open) return;
    const restore = restoreFocus && menu.contains(document.activeElement);
    open = false;
    menu.hidden = true;
    root.removeAttribute('data-open');
    handle.setAttribute('aria-expanded', 'false');
    preview = committed;
    updateOptions();
    document.removeEventListener('click', onOutsideClick);
    if (announceCancel) message('cancelled');
    if (restore) handle.focus({ preventScroll: true });
  }

  function cancelMenu() {
    closeMenu(true, true);
  }

  function commit(next) {
    showPanel(next);
    announceCommitted();
    closeMenu(false, true);
  }

  function suppressPointerClick() {
    suppressClickUntil = Date.now() + 450;
  }

  function releasePointer() {
    if (!drag) return;
    const id = drag.id;
    drag = null;
    if (handle.hasPointerCapture && handle.hasPointerCapture(id)) {
      try {
        handle.releasePointerCapture(id);
      } catch {
        /* The pointer may already be gone. */
      }
    }
  }

  function cancelDrag() {
    if (!drag) return false;
    suppressPointerClick();
    releasePointer();
    return true;
  }

  function onHandleClick(event) {
    if (event.detail > 0 && Date.now() < suppressClickUntil) {
      suppressClickUntil = 0;
      event.preventDefault();
      return;
    }

    if (!open) {
      openMenu();
      return;
    }

    if (event.detail === 0) {
      commit(preview);
      return;
    }

    cancelMenu();
  }

  handle.addEventListener('click', onHandleClick);

  handle.addEventListener('pointerdown', (event) => {
    if (drag || event.isPrimary === false) return;
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    suppressClickUntil = 0;
    drag = {
      id: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      startIndex: committed,
      axis: null,
    };
    try {
      handle.setPointerCapture(event.pointerId);
    } catch {
      /* Capture is optional; the handle also receives moves while over it. */
    }
  });

  handle.addEventListener('pointermove', (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    const dx = event.clientX - drag.startX;
    const dy = event.clientY - drag.startY;

    if (!drag.axis) {
      const intent = gestureAxis(dx, dy);
      if (!intent) return;
      drag.axis = intent;
      if (intent === 'vertical') {
        event.preventDefault();
        if (!open) openMenu();
      } else {
        return;
      }
    }

    if (drag.axis !== 'vertical') return;
    event.preventDefault();
    preview = arcIndex(drag.startIndex, dy, count);
    updateOptions();
  });

  handle.addEventListener('pointerup', (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    const wasVertical = drag.axis === 'vertical';
    const wasHorizontal = drag.axis === 'horizontal';
    releasePointer();
    if (wasVertical) {
      suppressPointerClick();
      commit(preview);
    } else if (wasHorizontal) {
      suppressPointerClick();
    }
  });

  handle.addEventListener('pointercancel', (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    cancelDrag();
    cancelMenu();
  });

  handle.addEventListener('lostpointercapture', (event) => {
    if (!drag || event.pointerId !== drag.id) return;
    cancelDrag();
    cancelMenu();
  });

  root.addEventListener('keydown', (event) => {
    const target = event.target;
    const inMenu = target && menu.contains(target);
    if (target !== handle && !inMenu) return;

    if (event.key === 'Escape') {
      if (!open && !drag) return;
      event.preventDefault();
      cancelDrag();
      cancelMenu();
      return;
    }

    if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') return;
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    event.preventDefault();
    cancelDrag();
    if (!open) openMenu();
    preview = clampIndex(preview + (event.key === 'ArrowUp' ? 1 : -1), count);
    updateOptions();
  });

  for (let i = 0; i < options.length; i += 1) {
    const optionIndex = optionIndexes[i];
    options[i].addEventListener('click', () => {
      if (!open) return;
      commit(optionIndex);
    });
  }

  if (closeButton) closeButton.addEventListener('click', cancelMenu);

  menu.hidden = true;
  handle.setAttribute('aria-expanded', 'false');
  root.removeAttribute('data-open');
  showPanel(initial);
  handle.disabled = false;
  markReady(root);
}

function startDemos() {
  initPetDemo(document.querySelector('[data-pet-demo]'));
  initPluginDemo(document.querySelector('[data-plugin-demo]'));
  initArcDemo(document.querySelector('[data-arc-demo]'));
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startDemos, { once: true });
  } else {
    startDemos();
  }
}
