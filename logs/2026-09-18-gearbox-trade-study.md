---
title: Gearbox trade study
date: 2026-09-18
author: [Hunter Adams]
tags: [mechanical, trade-study, procurement]
attachments:
  - docs/gearbox-trade-study-rev-A.pdf
summary: Compared harmonic drive, planetary and cycloidal options against backlash, cost and lead time. Recommending the planetary with firmware compensation.
---

# Gearbox trade study

Resolving open question 1 from the kickoff. Full scoring matrix is in the
attached PDF; the short version is below.

## Findings

- The harmonic drive meets the backlash spec outright (< 1 arcmin) but costs
  $410 and has a **nine week lead time**. That lead time alone disqualifies it —
  it lands after our integration milestone.
- The planetary gearbox has 12 arcmin of backlash, which is ~0.35 mm at our
  output radius. That is inside the 0.5 mm budget only if we compensate, and it
  leaves nothing for the rest of the error stack.
- Firmware backlash compensation is well understood and we have an encoder on
  the output shaft, so the compensation is measurable rather than open-loop.

## Recommendation

Planetary gearbox, encoder on the output shaft, backlash compensation in
firmware. Revisit if bench testing shows the error stack exceeding 0.4 mm.

> Risk noted: this couples our position accuracy to firmware correctness. If the
> compensation is wrong we will see it as a mechanical problem and waste time
> looking in the wrong place. Bench test the compensation in isolation first.
