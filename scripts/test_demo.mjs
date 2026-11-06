import assert from 'node:assert/strict';

import {
  arcIndex,
  clampCenter,
  clampIndex,
  gestureAxis,
  swipeIndex,
} from '../site/demo.mjs';

function test(name, run) {
  try {
    run();
  } catch (error) {
    error.message = `${name}: ${error.message}`;
    throw error;
  }
}

test('gesture axis ignores small or diagonal movement', () => {
  assert.equal(gestureAxis(0, 0), null);
  assert.equal(gestureAxis(7, 7), null);
  assert.equal(gestureAxis(8, 8), null);
  assert.equal(gestureAxis(8, 7), 'horizontal');
  assert.equal(gestureAxis(-8, 7), 'horizontal');
  assert.equal(gestureAxis(7, -8), 'vertical');
  assert.equal(gestureAxis(8, 20), 'vertical');
  assert.equal(gestureAxis(40, 4), 'horizontal');
});

test('clampIndex keeps indexes inside the list', () => {
  assert.equal(clampIndex(-1, 3), 0);
  assert.equal(clampIndex(0, 3), 0);
  assert.equal(clampIndex(2, 3), 2);
  assert.equal(clampIndex(5, 3), 2);
  assert.equal(clampIndex(1, 0), 0);
});

test('plugin swipe threshold and clamped directions', () => {
  assert.equal(swipeIndex(1, -71, 3, 72), 1);
  assert.equal(swipeIndex(1, -72, 3, 72), 2);
  assert.equal(swipeIndex(1, 72, 3, 72), 0);
  assert.equal(swipeIndex(1, 0, 3, 72), 1);

  assert.equal(swipeIndex(0, 200, 3, 72), 0);
  assert.equal(swipeIndex(2, -200, 3, 72), 2);
  assert.equal(swipeIndex(1, -200, 3, 72), 2);
  assert.equal(swipeIndex(1, 200, 3, 72), 0);
});

test('pet center clamps to the stage including oversized elements', () => {
  assert.equal(clampCenter(-50, 300, 100), 50);
  assert.equal(clampCenter(500, 300, 100), 250);
  assert.equal(clampCenter(150, 300, 100), 150);
  assert.equal(clampCenter(150, 50, 100), 25);
  assert.equal(clampCenter(150, 0, 100), 0);
});

test('arc drag starts at the active item and previews 48px per item', () => {
  assert.equal(arcIndex(1, 0, 3, 48), 1);
  assert.equal(arcIndex(1, -47, 3, 48), 1);
  assert.equal(arcIndex(1, -48, 3, 48), 2);
  assert.equal(arcIndex(1, 47, 3, 48), 1);
  assert.equal(arcIndex(1, 48, 3, 48), 0);
  assert.equal(arcIndex(1, -96, 3, 48), 2);
  assert.equal(arcIndex(1, 96, 3, 48), 0);
});

test('arc preview clamps at both ends from any starting point', () => {
  assert.equal(arcIndex(0, -200, 3, 48), 2);
  assert.equal(arcIndex(0, 200, 3, 48), 0);
  assert.equal(arcIndex(2, 200, 3, 48), 0);
  assert.equal(arcIndex(2, -200, 3, 48), 2);
});

console.log('OK: demo gesture and index helpers passed');
