---
title: Project kickoff and problem definition
date: 2026-09-15
author: [Hunter Adams]
tags: [planning, requirements]
---

# Project kickoff and problem definition

First working session of the term. We scoped the problem statement down from
the broad pitch to something a four-person team can actually build and validate
by the Symposium deadline.

## What we decided

- **Scope.** One actuated axis with closed-loop position control, rather than the
  three-axis system in the original pitch. Three axes is a fabrication problem,
  not an engineering one, and it would eat the entire budget.
- **Success criterion.** Steady-state position error under 0.5 mm, settling in
  under 400 ms against a 2 kg payload.
- **Budget.** $600 of the $750 allocation, leaving headroom for a second
  iteration of the parts most likely to fail.

## Open questions

1. Do we need a harmonic drive, or is a planetary gearbox with backlash
   compensation in firmware good enough? This is the decision that drives cost.
2. Encoder placement — motor shaft or output shaft. Output shaft is correct but
   needs a custom mount.

## Next steps

| Task | Owner | Due |
| --- | --- | --- |
| Draft requirements matrix | Hunter | Sep 19 |
| Gearbox trade study | TBD | Sep 22 |
| Supplier lead times | TBD | Sep 22 |
